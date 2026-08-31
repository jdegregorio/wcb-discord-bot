"""Thin Discord adapter around Trubot's domain behavior."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable, Sequence
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from typing import Protocol, cast

import discord

from trubot.attention import AttentionTracker
from trubot.config import Settings
from trubot.conversation import ConversationMessage, ReplyMode, safety_identifier
from trubot.health import ReadinessFile
from trubot.history import (
    HistoryChannel,
    clamp_discord_message,
    collect_history,
    message_target,
)
from trubot.participation import (
    Observation,
    ParticipationTracker,
    SchedulingAction,
)

logger = logging.getLogger(__name__)

_DIRECT_EMOJI = "🤖"
_VISIBLE_FAILURE = "Something broke. Probably Tim's fault."

Clock = Callable[[], datetime]
Sleeper = Callable[[float], Awaitable[None]]
DiscordChannel = discord.TextChannel | discord.Thread


class Responder(Protocol):
    async def reply(
        self,
        messages: Sequence[ConversationMessage],
        *,
        mode: ReplyMode,
        safety_id: str,
        target: str | None = None,
    ) -> str | None: ...

    async def close(self) -> None: ...


class TruBotClient(discord.Client):
    def __init__(
        self,
        *,
        settings: Settings,
        responder: Responder,
        participation: ParticipationTracker,
        attention: AttentionTracker,
        readiness: ReadinessFile,
        intents: discord.Intents,
        allowed_mentions: discord.AllowedMentions | None = None,
        clock: Clock | None = None,
        sleeper: Sleeper = asyncio.sleep,
    ) -> None:
        super().__init__(intents=intents, allowed_mentions=allowed_mentions)
        self._settings = settings
        self._responder = responder
        self._participation = participation
        self._attention = attention
        self._readiness = readiness
        self._clock = clock or (lambda: datetime.now(UTC))
        self._sleeper = sleeper
        self._ambient_tasks: dict[int, asyncio.Task[None]] = {}
        self._response_locks: defaultdict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._closing = False

    async def on_ready(self) -> None:
        await self._readiness.start()
        user = self.user
        logger.info(
            "Connected to Discord user=%s user_id=%s guilds=%d",
            user,
            getattr(user, "id", "unknown"),
            len(self.guilds),
        )

    async def on_disconnect(self) -> None:
        await self._readiness.stop()
        logger.warning("Disconnected from Discord")

    async def on_resumed(self) -> None:
        await self._readiness.start()
        logger.info("Discord session resumed")

    async def on_message(self, message: discord.Message) -> None:
        if not self._accept_message(message):
            return

        channel = cast(DiscordChannel, message.channel)
        now = self._clock()
        direct = self._is_direct_trigger(message)
        followup = not direct and self._attention.is_active(channel.id, now)
        observation = self._participation.observe(
            channel.id,
            message.author.id,
            now,
            allow_ambient=not (direct or followup),
        )
        self._apply_observation(channel.id, observation)

        if direct:
            self._attention.activate(channel.id, now)
            logger.info(
                "Direct Trubot trigger channel_id=%d guild_id=%s user_id=%d",
                channel.id,
                getattr(channel.guild, "id", "unknown"),
                message.author.id,
            )
            await self._respond(
                channel,
                mode=ReplyMode.DIRECT,
                requester_user_id=message.author.id,
                anchor=message,
                target=message_target(message),
            )
        elif followup:
            logger.info(
                "Possible Trubot follow-up channel_id=%d guild_id=%s user_id=%d",
                channel.id,
                getattr(channel.guild, "id", "unknown"),
                message.author.id,
            )
            await self._respond(
                channel,
                mode=ReplyMode.FOLLOW_UP,
                requester_user_id=message.author.id,
                anchor=message,
                target=message_target(message),
            )

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        user = self.user
        if user is None or payload.user_id == user.id:
            return
        if payload.channel_id not in self._settings.allowed_channel_ids:
            return
        if payload.emoji.name not in self._settings.reaction_emoji_names:
            return
        if payload.member is not None and payload.member.bot:
            return

        channel = self.get_channel(payload.channel_id)
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            logger.warning("Reaction channel is unavailable channel_id=%d", payload.channel_id)
            return

        self._cancel_ambient(channel.id)
        self._participation.invalidate(channel.id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.HTTPException:
            logger.exception(
                "Unable to fetch reaction target channel_id=%d message_id=%d",
                channel.id,
                payload.message_id,
            )
            return

        logger.info(
            "Reaction Trubot trigger channel_id=%d message_id=%d user_id=%d emoji=%s",
            channel.id,
            payload.message_id,
            payload.user_id,
            payload.emoji.name,
        )
        self._attention.activate(channel.id, self._clock())
        await self._respond(
            channel,
            mode=ReplyMode.REACTION,
            requester_user_id=payload.user_id,
            anchor=message,
            target=message_target(message),
        )

    async def close(self) -> None:
        if self._closing:
            return
        self._closing = True
        tasks = list(self._ambient_tasks.values())
        self._ambient_tasks.clear()
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        await self._readiness.stop()
        await self._responder.close()
        await super().close()

    def _accept_message(self, message: discord.Message) -> bool:
        return (
            not message.author.bot
            and message.channel.id in self._settings.allowed_channel_ids
            and isinstance(message.channel, (discord.TextChannel, discord.Thread))
        )

    def _is_direct_trigger(self, message: discord.Message) -> bool:
        user = self.user
        mentioned = user is not None and any(mention.id == user.id for mention in message.mentions)
        return mentioned or _DIRECT_EMOJI in message.content or self._is_reply_to_trubot(message)

    def _is_reply_to_trubot(self, message: discord.Message) -> bool:
        user = self.user
        reference = message.reference
        resolved = getattr(reference, "resolved", None)
        author = getattr(resolved, "author", None)
        return user is not None and getattr(author, "id", None) == user.id

    def _apply_observation(self, channel_id: int, observation: Observation) -> None:
        if observation.action is SchedulingAction.SCHEDULE:
            self._schedule_ambient(channel_id, observation.revision)
        else:
            self._cancel_ambient(channel_id)

    def _schedule_ambient(self, channel_id: int, revision: int) -> None:
        self._cancel_ambient(channel_id)
        task = asyncio.create_task(
            self._run_ambient(channel_id, revision),
            name=f"ambient-reply:{channel_id}:{revision}",
        )
        task.add_done_callback(self._consume_task_result)
        self._ambient_tasks[channel_id] = task

    def _cancel_ambient(self, channel_id: int) -> None:
        task = self._ambient_tasks.pop(channel_id, None)
        if task is not None:
            task.cancel()

    async def _run_ambient(self, channel_id: int, revision: int) -> None:
        try:
            await self._sleeper(self._participation.policy.delay.total_seconds())
            eligibility = self._participation.ambient_eligibility(
                channel_id,
                revision,
                self._clock(),
            )
            if eligibility is None:
                return
            channel = self.get_channel(channel_id)
            if not isinstance(channel, (discord.TextChannel, discord.Thread)):
                logger.warning("Ambient channel is unavailable channel_id=%d", channel_id)
                return

            logger.info("Ambient Trubot trigger channel_id=%d revision=%d", channel_id, revision)
            await self._respond(
                channel,
                mode=ReplyMode.AMBIENT,
                requester_user_id=eligibility.requester_user_id,
            )
        except asyncio.CancelledError:
            logger.debug("Ambient reply cancelled channel_id=%d revision=%d", channel_id, revision)
            raise
        except Exception:
            logger.exception("Ambient reply failed channel_id=%d revision=%d", channel_id, revision)
        finally:
            if self._ambient_tasks.get(channel_id) is asyncio.current_task():
                self._ambient_tasks.pop(channel_id, None)

    async def _respond(
        self,
        channel: DiscordChannel,
        *,
        mode: ReplyMode,
        requester_user_id: int,
        anchor: discord.Message | None = None,
        target: str | None = None,
    ) -> bool:
        user = self.user
        if user is None:
            return False

        async with self._response_locks[channel.id]:
            request_at = self._clock()
            try:
                history = await collect_history(
                    cast(HistoryChannel, channel),
                    bot_user_id=user.id,
                    limit=self._settings.history_limit,
                    before=anchor,
                    after=request_at - timedelta(seconds=self._settings.history_window_seconds),
                )
                if not history and target is None:
                    logger.warning("No usable history for response channel_id=%d", channel.id)
                    return False

                guild_id = channel.guild.id
                async with channel.typing():
                    reply = await self._responder.reply(
                        history,
                        mode=mode,
                        safety_id=safety_identifier(guild_id, requester_user_id),
                        target=target,
                    )
                if reply is None:
                    logger.info(
                        "Skipped Trubot response channel_id=%d mode=%s",
                        channel.id,
                        mode.value,
                    )
                    return False
                output = clamp_discord_message(reply)
                await channel.send(output)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception(
                    "Trubot response failed channel_id=%d mode=%s",
                    channel.id,
                    mode.value,
                )
                if mode in {ReplyMode.DIRECT, ReplyMode.REACTION}:
                    with suppress(discord.HTTPException):
                        await channel.send(_VISIBLE_FAILURE)
                return False

            self._participation.record_reply(
                channel.id,
                self._clock(),
                ambient=mode is ReplyMode.AMBIENT,
            )
            if mode is not ReplyMode.AMBIENT:
                self._attention.activate(channel.id, self._clock())
            logger.info(
                "Posted Trubot response channel_id=%d mode=%s characters=%d",
                channel.id,
                mode.value,
                len(output),
            )
            return True

    @staticmethod
    def _consume_task_result(task: asyncio.Task[None]) -> None:
        with suppress(asyncio.CancelledError):
            error = task.exception()
            if error is not None:
                logger.error(
                    "Unhandled ambient task error task=%s",
                    task.get_name(),
                    exc_info=error,
                )
