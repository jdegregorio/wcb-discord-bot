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
from trubot.budget import BudgetError
from trubot.config import Settings
from trubot.conversation import ConversationMessage, ReplyMode, safety_identifier
from trubot.distillation import GraphDistiller
from trubot.health import ReadinessFile
from trubot.history import (
    HistoryChannel,
    clamp_discord_message,
    collect_history,
    message_target,
    visual_message,
)
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningUnavailable
from trubot.memory import ContextMemory, terms, years
from trubot.participation import (
    Observation,
    ParticipationTracker,
    SchedulingAction,
)
from trubot.vision import ImageCollector

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
        learning: MessageIngestor | None = None,
        distiller: GraphDistiller | None = None,
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
        self._learning = learning
        self._distiller = distiller
        self._memory = ContextMemory(learning.store) if learning is not None else None
        self._learning_task: asyncio.Task[None] | None = None

    async def on_ready(self) -> None:
        await self._readiness.start()
        self._start_learning()
        user = self.user
        logger.info(
            "Connected to Discord user=%s user_id=%s guilds=%d",
            user,
            getattr(user, "id", "unknown"),
            len(self.guilds),
        )

    async def on_disconnect(self) -> None:
        await self._stop_learning()
        await self._readiness.stop()
        logger.warning("Disconnected from Discord")

    async def on_resumed(self) -> None:
        await self._readiness.start()
        self._start_learning()
        logger.info("Discord session resumed")

    async def on_message(self, message: discord.Message) -> None:
        if not self._accept_message(message):
            return

        if self._learning is not None:
            try:
                await self._learning.observe(message)
            except LearningUnavailable:
                logger.warning("Learning observation paused: private state unavailable")
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
        await self._stop_learning()
        tasks = list(self._ambient_tasks.values())
        self._ambient_tasks.clear()
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        await self._readiness.stop()
        await self._responder.close()
        await super().close()

    def _start_learning(self) -> None:
        if (
            self._learning is not None
            and not self._closing
            and (self._learning_task is None or self._learning_task.done())
        ):
            self._learning_task = asyncio.create_task(self._run_learning(), name="private-learning")

    async def _stop_learning(self) -> None:
        task, self._learning_task = self._learning_task, None
        if self._learning is not None:
            self._learning.verified = False
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    async def _run_learning(self) -> None:
        assert self._learning is not None  # noqa: S101 - guarded when creating the task
        while True:
            try:
                await self._learning.cycle(self)
                if self._distiller is not None:
                    await self._distiller.cycle(self)
            except Exception:
                # Transport/library failures must pause and retry, never kill the worker
                # or expose exception payloads containing private source data.
                self._learning.verified = False
                logger.warning("Learning paused: pinned membership or private state unavailable")
            await asyncio.sleep(self._settings.learning_poll_seconds)

    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent) -> None:
        learning = self._learning
        if learning is None or payload.channel_id not in learning.channel_ids:
            return
        try:
            await learning.invalidate(payload.channel_id, [payload.message_id], deleted=False)
            channel = self.get_channel(payload.channel_id)
            if isinstance(channel, (discord.TextChannel, discord.Thread)):
                await learning.refresh(channel, payload.message_id)
        except (discord.HTTPException, LearningUnavailable):
            logger.warning("Learning correction pending: source or private storage unavailable")

    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        await self._delete_learning(payload.channel_id, [payload.message_id])

    async def on_raw_bulk_message_delete(self, payload: discord.RawBulkMessageDeleteEvent) -> None:
        await self._delete_learning(payload.channel_id, list(payload.message_ids))

    async def _delete_learning(self, channel_id: int, ids: list[int]) -> None:
        if self._learning is not None:
            try:
                await self._learning.invalidate(channel_id, ids, deleted=True)
            except LearningUnavailable:
                logger.warning("Learning deletion pending: private state unavailable")

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
                images = ImageCollector()
                focused = (
                    await visual_message(anchor, bot_user_id=user.id, images=images, target=True)
                    if anchor is not None
                    else None
                )
                reference_context = await self._reference_context(anchor, images)
                history = await collect_history(
                    cast(HistoryChannel, channel),
                    bot_user_id=user.id,
                    limit=self._settings.history_limit,
                    before=anchor,
                    after=request_at - timedelta(seconds=self._settings.history_window_seconds),
                    images=images,
                )
                if reference_context is not None:
                    history.append(reference_context)
                if focused is not None and (
                    focused.images or "image pixels unavailable" in focused.content
                ):
                    # Keep the focus last so the adapter retains its image parts.
                    history.append(focused)
                    target = focused.content
                memory = await self._memory_context(
                    channel, target, history, requester_user_id=requester_user_id
                )
                if memory:
                    history.insert(0, ConversationMessage("user", memory))
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
            except BudgetError as error:
                logger.warning(
                    "Generation paused reason=%s mode=%s", type(error).__name__, mode.value
                )
                if mode in {ReplyMode.DIRECT, ReplyMode.REACTION}:
                    with suppress(discord.HTTPException):
                        await channel.send("I'm taking a breather. Try me again later.")
                return False
            except Exception as error:
                # Provider exceptions can contain source text or image payloads.
                logger.error(
                    "Trubot response failed channel_id=%d mode=%s error_type=%s",
                    channel.id,
                    mode.value,
                    type(error).__name__,
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

    async def _reference_context(
        self, anchor: discord.Message | None, images: ImageCollector
    ) -> ConversationMessage | None:
        if anchor is None or self.user is None:
            return None
        reference = getattr(anchor, "reference", None)
        if not isinstance(reference, discord.MessageReference):
            return None
        if reference.channel_id != anchor.channel.id or reference.message_id is None:
            return None
        try:
            # Refresh even a resolved reference, since cached content can be edited.
            message = await anchor.channel.fetch_message(reference.message_id)
            converted = await visual_message(
                message, bot_user_id=self.user.id, images=images, target=True
            )
            if converted is not None:
                return ConversationMessage(
                    converted.role,
                    "REFERENCED MESSAGE (context only): " + converted.content,
                    converted.images,
                )
        except discord.HTTPException:
            return ConversationMessage("user", "[Referenced message unavailable.]")
        return None

    async def _memory_context(
        self,
        channel: DiscordChannel,
        target: str | None,
        history: list[ConversationMessage],
        *,
        requester_user_id: int | None = None,
    ) -> str:
        learning, memory = self._learning, self._memory
        if learning is None or memory is None or not learning.verified:
            return ""
        source_guild_id = channel.guild.id
        if source_guild_id != learning.identity.guild_id:
            # Joe's isolated development server may test the same private memory.
            # Authenticated ownership and the existing channel allowlist gate access;
            # this does not change learning.accepts or source attribution.
            if (
                not self._settings.development_guild_id
                or source_guild_id != self._settings.development_guild_id
                or channel.id not in self._settings.allowed_channel_ids
                or requester_user_id is None
                or requester_user_id != channel.guild.owner_id
            ):
                return ""
            source_guild_id = learning.identity.guild_id
        # Use the focused topic. Only a context-dependent follow-up needs nearby
        # human messages; prior bot prose must not become evidence or query bait.
        # Strip the speaker label once, preserving punctuation in the actual request.
        request = (target or "").split(": ", 1)[-1]
        query = request
        if not (terms(query) or years(query)):
            query += " " + " ".join(
                m.content.split(": ", 1)[-1] for m in history[-4:] if m.role == "user"
            )
        try:
            candidates = await asyncio.to_thread(
                memory.candidates, query, guild_id=source_guild_id, now=self._clock()
            )
            verified = []
            verification_started = self._clock()
            verification_deadline = asyncio.get_running_loop().time() + 6
            for candidate in candidates:
                if candidate.source["kind"] == "discord":
                    source_channel = self.get_channel(candidate.source["channel_id"])
                    if not isinstance(source_channel, (discord.TextChannel, discord.Thread)):
                        continue
                    if not learning.accepts(source_channel):
                        continue
                    remaining = verification_deadline - asyncio.get_running_loop().time()
                    if remaining <= 0:
                        break
                    try:
                        await asyncio.wait_for(
                            learning.refresh(source_channel, candidate.source["message_id"]),
                            timeout=min(4, remaining),
                        )
                    except (discord.HTTPException, TimeoutError):
                        # Missing permission or network access never revives cached evidence.
                        continue
                verified.append(candidate)
            if self._learning is not None and self._learning.verified:
                return await asyncio.to_thread(
                    memory.render,
                    verified,
                    verified_after=verification_started,
                    now=self._clock(),
                    request=request,
                )
            return ""
        except LearningUnavailable:
            logger.warning("Response memory unavailable; source verification required")
            return ""

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
