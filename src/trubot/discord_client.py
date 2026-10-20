"""Thin Discord adapter around Trubot's domain behavior."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import io
import json
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable, Sequence
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from typing import Protocol, cast

import discord

from trubot.attention import AttentionTracker
from trubot.aurora import morning_window
from trubot.aurora_feature import AuroraFeature
from trubot.budget import BudgetError
from trubot.config import Settings
from trubot.conversation import (
    REFERENCE_PREFIX,
    ConversationImage,
    ConversationMessage,
    MemoryAuthorScope,
    ReplyMode,
    safety_identifier,
)
from trubot.distillation import GraphDistiller
from trubot.graph import GraphStore
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
from trubot.memory import (
    ContextMemory,
    recent_context_unavailable,
    recent_recall,
    requester_context_unavailable,
    requester_recall,
    terms,
    years,
)
from trubot.native_context import NativeEpisode, collect_native_episode, source_media_episode
from trubot.outdoors import OutdoorFeature, posting_window
from trubot.participation import (
    Observation,
    ParticipationTracker,
    SchedulingAction,
)
from trubot.photo_action import PhotoAction, PhotoEvidence
from trubot.photos import PhotoMemory
from trubot.recall_reference import quotation_unavailable, recall_quotation
from trubot.reply_focus import memory_followup_query
from trubot.requested_scenes import (
    MAX_REQUEST_AGE,
    RequestedScenes,
    SceneRequest,
    operation_key,
    requested_region,
)
from trubot.vision import ImageCollector
from trubot.voice_memory import voice_context

logger = logging.getLogger(__name__)

_DIRECT_EMOJI = "🤖"
_VISIBLE_FAILURE = "Something broke. Probably Tim's fault."

Clock = Callable[[], datetime]
Sleeper = Callable[[float], Awaitable[None]]
DiscordChannel = discord.TextChannel | discord.Thread


class Responder(Protocol):
    async def allow_scheduled_share(self, messages: Sequence[str]) -> bool: ...

    async def reply(
        self,
        messages: Sequence[ConversationMessage],
        *,
        mode: ReplyMode,
        safety_id: str,
        target: str | None = None,
        requester_user_id: int | None = None,
        refresh_check: Callable[[], Awaitable[bool]] | None = None,
        photo_action: PhotoAction | None = None,
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
        aurora: AuroraFeature | OutdoorFeature | None = None,
        scenes: RequestedScenes | None = None,
        photos: PhotoMemory | None = None,
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
        self._photos = photos
        if photos is not None:
            photos.client = self
        self._scenes = scenes
        self._aurora = aurora
        self._aurora_task: asyncio.Task[None] | None = None

    async def on_ready(self) -> None:
        await self._readiness.start()
        self._start_learning()
        self._start_aurora()
        user = self.user
        logger.info(
            "Connected to Discord user=%s user_id=%s guilds=%d",
            user,
            getattr(user, "id", "unknown"),
            len(self.guilds),
        )

    async def on_disconnect(self) -> None:
        await self._stop_aurora()
        await self._stop_learning()
        await self._readiness.stop()
        logger.warning("Disconnected from Discord")

    async def on_resumed(self) -> None:
        await self._readiness.start()
        self._start_learning()
        self._start_aurora()
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
        await self._stop_aurora()
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

    def _start_aurora(self) -> None:
        if self._aurora is not None and (self._aurora_task is None or self._aurora_task.done()):
            self._aurora_task = asyncio.create_task(self._run_aurora(), name="outdoor-check-in")

    async def _stop_aurora(self) -> None:
        task, self._aurora_task = self._aurora_task, None
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    async def _run_aurora(self) -> None:
        while not self._closing:
            try:
                await self._aurora_cycle()
            except asyncio.CancelledError:
                raise
            except Exception as error:
                logger.warning("Aurora cycle unavailable error_type=%s", type(error).__name__)
            await asyncio.sleep(60)

    async def _outdoor_scope_current(self, channel: discord.TextChannel) -> bool:
        learning = self._learning
        if self._closing or learning is None or not learning.verified:
            return False
        identity = await asyncio.to_thread(learning.store.identity)
        if (
            identity != learning.identity
            or channel.guild.id != identity.guild_id
            or channel.id not in self._settings.allowed_channel_ids
        ):
            return False
        if isinstance(self._aurora, OutdoorFeature):
            # Fetch current permissions at each I/O/publication boundary, not a stale cache.
            fresh = await channel.guild.fetch_channel(channel.id)
            member = await channel.guild.fetch_member(self.user.id) if self.user else None
            if member is None or not isinstance(fresh, discord.TextChannel):
                return False
            permissions = fresh.permissions_for(member)
            if not (
                permissions.view_channel
                and permissions.read_message_history
                and permissions.send_messages
                and permissions.attach_files
            ):
                return False
        return True

    async def _aurora_channel_ready(self, channel: discord.TextChannel) -> bool:
        if not await self._outdoor_scope_current(channel):
            return False
        now = self._clock()
        in_window = (
            posting_window(now)
            if isinstance(self._aurora, OutdoorFeature)
            else morning_window(now) is not None
        )
        if not in_window or not self._participation.scheduled_eligible(channel.id, now):
            return False
        async for message in channel.history(limit=1):
            if now - message.created_at < timedelta(seconds=self._settings.auto_delay_seconds):
                return False
        if isinstance(self._aurora, OutdoorFeature):
            # The in-memory tracker can be empty after restart. Require a fully bounded
            # recent history before treating the shared reply cooldown as clear.
            recent = [
                message
                async for message in channel.history(
                    limit=101,
                    after=now - self._participation.policy.min_interval,
                )
            ]
            if len(recent) > 100 or any(
                self.user is not None and message.author.id == self.user.id for message in recent
            ):
                return False
        return True

    async def _aurora_cycle(self) -> bool:
        feature = self._aurora
        channel = self.get_channel(self._settings.aurora_channel_id)
        if feature is None or not isinstance(channel, discord.TextChannel):
            return False
        if isinstance(feature, OutdoorFeature):
            if not await asyncio.to_thread(feature.store.due, self._clock()):
                return False
        elif not await self._aurora_channel_ready(channel):
            return False

        timing_stamp: tuple[tuple[int, str, str], ...] | None = None

        async def before_generation() -> bool:
            nonlocal timing_stamp
            if isinstance(feature, OutdoorFeature):
                if not await self._aurora_channel_ready(channel):
                    return False
                timing_stamp = await self._outdoor_context_stamp(channel)
            return await self._aurora_timing_ok(channel)

        prepared = (
            await feature.prepare(
                now=self._clock(),
                before_generation=before_generation,
                before_check=lambda: self._outdoor_scope_current(channel),
            )
            if isinstance(feature, OutdoorFeature)
            else await feature.prepare(now=self._clock(), before_generation=before_generation)
        )
        if prepared is None:
            return False
        opportunity, image = prepared
        async with self._response_locks[channel.id]:
            if not await self._aurora_channel_ready(channel):
                await asyncio.to_thread(feature.store.finish, opportunity.morning, "deferred")
                return False
            if isinstance(feature, OutdoorFeature) and (
                timing_stamp is None or timing_stamp != await self._outdoor_context_stamp(channel)
            ):
                await asyncio.to_thread(feature.store.finish, opportunity.morning, "deferred")
                return False
            if image.source_check is not None and not await image.source_check():
                await asyncio.to_thread(feature.store.finish, opportunity.morning, "deferred")
                return False
            # Commit before sending. An ambiguous send or crash must never duplicate a claim.
            await asyncio.to_thread(feature.store.finish, opportunity.morning, "send_uncertain")
            attachment = discord.File(
                io.BytesIO(image.data),
                filename="trubot-outdoors-generated.png",
                description=image.description,
            )
            try:
                sent = await channel.send(
                    image.caption,
                    file=attachment,
                    allowed_mentions=discord.AllowedMentions.none(),
                    nonce=(
                        int(opportunity.morning[:15], 16)
                        if isinstance(feature, OutdoorFeature)
                        else opportunity.morning
                    ),
                )
            finally:
                attachment.close()
            await asyncio.to_thread(feature.store.finish, opportunity.morning, "posted", sent.id)
            self._cancel_ambient(channel.id)
            self._participation.record_reply(channel.id, self._clock(), ambient=True)
            logger.info("Posted generated outdoor scene")
            return True

    async def _outdoor_context_stamp(
        self, channel: discord.TextChannel
    ) -> tuple[tuple[int, str, str], ...]:
        # Ephemeral only. An edit/new sensitive exchange during generation invalidates timing.
        rows = []
        async for message in channel.history(
            limit=10, after=self._clock() - timedelta(hours=6), oldest_first=False
        ):
            rows.append(
                (
                    message.id,
                    str(message.edited_at),
                    repr(
                        (
                            message.content,
                            [(a.id, a.size) for a in message.attachments],
                            [e.to_dict() for e in message.embeds],
                        )
                    ),
                )
            )
        return tuple(rows)

    async def _aurora_timing_ok(self, channel: discord.TextChannel) -> bool:
        context = []
        async for message in channel.history(
            limit=10, after=self._clock() - timedelta(hours=6), oldest_first=False
        ):
            if message.author.bot or message.webhook_id is not None:
                continue
            # Unseen pixels or clipped text cannot establish a suitable emotional moment.
            if message.attachments or message.embeds or len(message.content) > 1_000:
                return False
            context.append(message.content)
        return await self._responder.allow_scheduled_share(list(reversed(context)))

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
                if self._photos is not None:
                    # Photo failures cannot revoke text-learning verification or stop replies.
                    try:
                        await self._photos.cycle(self)
                    except Exception:
                        logger.warning(
                            "Photo memory paused: private state, source or budget unavailable"
                        )
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
            if self._photos is not None:
                await asyncio.to_thread(
                    self._photos.store.drop,
                    payload.channel_id,
                    [payload.message_id],
                    deleted=False,
                    now=self._clock(),
                )
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
                if self._photos is not None:
                    await asyncio.to_thread(
                        self._photos.store.drop, channel_id, ids, deleted=True, now=self._clock()
                    )
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
                region = (
                    requested_region(anchor.content, bot_user_id=user.id)
                    if mode is ReplyMode.DIRECT and anchor is not None
                    else None
                )
                if (
                    region
                    and anchor is not None
                    and self._scenes is not None
                    and isinstance(channel, discord.TextChannel)
                ):
                    return await self._respond_scene(channel, anchor, region, requester_user_id)
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
                    history.append(
                        ConversationMessage(
                            focused.role,
                            focused.content,
                            focused.images,
                            origin="focus",
                            author_user_id=focused.author_user_id,
                        )
                    )
                    target = focused.content
                request = (target or "").split(": ", 1)[-1]
                if anchor is not None and requester_recall(request):
                    # A peer's own history cannot inherit the persona's old answers.
                    # IDs come only from Discord conversion, never speaker labels.
                    history = [
                        row
                        for row in history
                        if row.role == "user"
                        and row.origin in {"conversation", "focus"}
                        and row.author_user_id == anchor.author.id
                        and not anchor.author.bot
                    ]
                source_history = list(history)
                memory_pixels: list[ConversationImage] = []
                memory_image_limit = max(0, 2 - sum(len(m.images) for m in history))
                memory = await self._memory_context(
                    channel,
                    target,
                    history,
                    requester_user_id=requester_user_id,
                    focus_author_user_id=anchor.author.id if anchor is not None else None,
                    visual_sink=memory_pixels,
                    visual_limit=memory_image_limit,
                )
                memory_scope = None
                if memory and self._learning is not None:
                    try:
                        memory_scope = await self._memory_author_scope(anchor)
                    except LearningUnavailable:
                        # A withdrawal or changed identity cannot leave old evidence
                        # paired with a fresh or guessed author binding.
                        memory = ""
                if memory:
                    # Fresh source checks should follow old conversation, including stale
                    # bot denials. Keep a visual focus last so the responder attaches
                    # its pixels to the actual question instead of the memory packet.
                    position = (
                        len(history) - 1
                        if history and history[-1].content == target
                        else len(history)
                    )
                    history.insert(
                        position,
                        ConversationMessage(
                            "user",
                            memory,
                            tuple(memory_pixels),
                            origin="memory",
                            memory_author_scope=memory_scope,
                        ),
                    )
                if not history and target is None:
                    logger.warning("No usable history for response channel_id=%d", channel.id)
                    return False

                async def refresh_context_current() -> bool:
                    if self._closing:
                        return False
                    try:
                        refreshed = await self._memory_context(
                            channel,
                            target,
                            source_history,
                            requester_user_id=requester_user_id,
                            focus_author_user_id=anchor.author.id if anchor is not None else None,
                            visual_sink=[] if memory_pixels else None,
                            visual_limit=memory_image_limit,
                        )
                        if memory_scope is not None:
                            scope = await self._memory_author_scope(anchor)
                            if scope is not memory_scope:
                                return False
                    except (LearningUnavailable, discord.HTTPException, TimeoutError):
                        return False
                    return refreshed == memory

                photo_action = None
                if (
                    anchor is not None
                    and mode in {ReplyMode.DIRECT, ReplyMode.FOLLOW_UP}
                    and self._learning is not None
                ):
                    # Model-selected action, with no phrase or keyword intent gate.
                    frozen = SceneRequest(
                        anchor.id,
                        anchor.author.id,
                        anchor.content,
                        anchor.created_at,
                        anchor.edited_at,
                    )

                    async def retrieve_photo(query: str) -> PhotoEvidence | None:
                        if not await self._photo_request_current(
                            channel, frozen, requester_user_id
                        ):
                            return None
                        learning = self._learning
                        if learning is None:
                            return None
                        if requester_recall((target or "").split(": ", 1)[-1]) and (
                            frozen.author_id != learning.identity.user_id
                        ):
                            return None
                        if self._photos is not None:
                            recovered = await self._photos.recall(
                                query,
                                recipient=(
                                    requester_user_id
                                    if channel.guild.id == learning.identity.guild_id
                                    else None
                                ),
                            )
                            if recovered is not None:

                                async def recovered_current() -> bool:
                                    return (
                                        await self._photo_request_current(
                                            channel, frozen, requester_user_id
                                        )
                                        and await recovered.current()
                                    )

                                return PhotoEvidence(
                                    recovered.text,
                                    recovered.images,
                                    recovered_current,
                                    recovered.source_episode,
                                    recovered.source_stamp,
                                )
                        pixels: list[ConversationImage] = []
                        evidence = await self._memory_context(
                            channel,
                            target,
                            source_history,
                            requester_user_id=requester_user_id,
                            focus_author_user_id=frozen.author_id,
                            visual_sink=pixels,
                            visual_limit=1,
                            retrieval_query=query,
                            photo_recipient_user_id=requester_user_id,
                        )
                        if not pixels:
                            return None

                        async def current() -> bool:
                            if not await self._photo_request_current(
                                channel, frozen, requester_user_id
                            ):
                                return False
                            refreshed_pixels: list[ConversationImage] = []
                            refreshed = await self._memory_context(
                                channel,
                                target,
                                source_history,
                                requester_user_id=requester_user_id,
                                focus_author_user_id=frozen.author_id,
                                visual_sink=refreshed_pixels,
                                visual_limit=1,
                                retrieval_query=query,
                                photo_recipient_user_id=requester_user_id,
                            )
                            return refreshed == evidence and refreshed_pixels == pixels

                        return PhotoEvidence(evidence, tuple(pixels), current)

                    # Select only an existing scoped link, before provider I/O. Source
                    # existence is a capability hint, never permission or human evidence.
                    shown = None
                    reference = getattr(anchor, "reference", None)
                    if (
                        self._photos is not None
                        and not (
                            requester_recall(request)
                            and frozen.author_id != self._learning.identity.user_id
                        )
                        and (
                            not isinstance(reference, discord.MessageReference)
                            or (
                                reference.channel_id == channel.id
                                and reference.message_id is not None
                            )
                        )
                    ):
                        with suppress(LearningUnavailable):
                            shown = await asyncio.to_thread(
                                self._photos.store.shown,
                                channel.guild.id,
                                channel.id,
                                requester_user_id,
                                now=self._clock(),
                                sent=(
                                    reference.message_id
                                    if isinstance(reference, discord.MessageReference)
                                    else None
                                ),
                            )

                    async def inspect_photo() -> PhotoEvidence | None:
                        if not await self._photo_request_current(
                            channel, frozen, requester_user_id, attachment=False
                        ):
                            return None
                        learning, photos = self._learning, self._photos
                        if (
                            learning is None
                            or photos is None
                            or (
                                requester_recall(request)
                                and frozen.author_id != learning.identity.user_id
                            )
                        ):
                            return None
                        if shown is None:
                            return None
                        inspected = await photos.inspect_shown(
                            channel,
                            requester_user_id,
                            sent=shown["sent"],
                            recipient=(
                                requester_user_id
                                if channel.guild.id == learning.identity.guild_id
                                else None
                            ),
                        )
                        if inspected is None:
                            return None

                        async def inspection_current() -> bool:
                            return (
                                await self._photo_request_current(
                                    channel, frozen, requester_user_id, attachment=False
                                )
                                and await inspected.current()
                            )

                        return PhotoEvidence(inspected.text, inspected.images, inspection_current)

                    photo_action = PhotoAction(
                        retrieve_photo, inspect_photo if shown is not None else None
                    )

                guild_id = channel.guild.id
                async with channel.typing():
                    reply = await self._responder.reply(
                        history,
                        mode=mode,
                        safety_id=safety_identifier(guild_id, requester_user_id),
                        target=target,
                        requester_user_id=requester_user_id,
                        refresh_check=refresh_context_current if memory else None,
                        **({"photo_action": photo_action} if photo_action is not None else {}),
                    )
                if reply is None:
                    logger.info(
                        "Skipped Trubot response channel_id=%d mode=%s",
                        channel.id,
                        mode.value,
                    )
                    return False
                # Generation can outlive a correction, withdrawal or access change.
                # Reuse the same bounded source/author check before publishing any
                # private-memory draft, even when no quality retry was necessary.
                if memory and not await refresh_context_current():
                    logger.info(
                        "Discarded generated reply; private source context changed or unavailable "
                        "mode=%s",
                        mode.value,
                    )
                    return False
                output = clamp_discord_message(reply)
                if (
                    photo_action is not None
                    and photo_action.evidence is not None
                    and not await photo_action.current()
                ):
                    logger.info("Discarded photo reply; source or request changed")
                    return False
                if (
                    photo_action is not None
                    and photo_action.evidence is not None
                    and not photo_action.inspected
                ):
                    if anchor is None:
                        return False
                    attachments = [
                        discord.File(
                            io.BytesIO(base64.b64decode(image.data_url.split(",", 1)[1])),
                            filename=f"source-photo-{i + 1}.jpg",
                            description="Photo shared earlier in the league.",
                        )
                        for i, image in enumerate(photo_action.evidence.images)
                    ]
                    try:
                        posted = await channel.send(
                            output,
                            files=attachments,
                            allowed_mentions=discord.AllowedMentions.none(),
                            nonce=anchor.id,
                        )
                    finally:
                        for attachment in attachments:
                            attachment.close()
                    if self._photos is not None:
                        try:
                            await asyncio.to_thread(
                                self._photos.store.remember_shown,
                                photo_action.evidence,
                                posted,
                                requester_user_id,
                                now=self._clock(),
                            )
                        except LearningUnavailable:
                            # The post succeeded; unavailable continuity never sends again.
                            logger.warning("Photo posted; source continuity unavailable")
                else:
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

    async def _photo_request_current(
        self,
        channel: DiscordChannel,
        request: SceneRequest,
        requester: int,
        *,
        attachment: bool = True,
    ) -> bool:
        if not await self._scene_scope_current(channel, requester):
            return False
        try:
            async with asyncio.timeout(6):
                fresh_channel = await self.fetch_channel(channel.id)
                if not isinstance(fresh_channel, (discord.TextChannel, discord.Thread)):
                    return False
                if (
                    fresh_channel.guild.id != channel.guild.id
                    or not await self._scene_scope_current(fresh_channel, requester)
                ):
                    return False
                user = self.user
                if user is None:
                    return False
                member = await fresh_channel.guild.fetch_member(user.id)
                permissions = fresh_channel.permissions_for(member)
                if not (
                    permissions.view_channel
                    and permissions.send_messages
                    and (permissions.attach_files or not attachment)
                    and permissions.read_message_history
                ):
                    return False
                fresh = await fresh_channel.fetch_message(request.message_id)
                return (
                    fresh.author.id == requester == request.author_id
                    and not fresh.author.bot
                    and fresh.webhook_id is None
                    and fresh.content == request.content
                    and fresh.created_at == request.created_at
                    and fresh.edited_at == request.edited_at
                    and timedelta(0) <= self._clock() - fresh.created_at <= MAX_REQUEST_AGE
                )
        except (discord.HTTPException, TimeoutError, LearningUnavailable):
            return False

    async def _scene_scope_current(self, channel: DiscordChannel, requester: int) -> bool:
        learning = self._learning
        if self._closing or learning is None or not learning.verified:
            return False
        try:
            identity = await asyncio.to_thread(learning.store.identity)
        except LearningUnavailable:
            return False
        if identity != learning.identity or channel.id not in self._settings.allowed_channel_ids:
            return False
        return channel.guild.id == identity.guild_id or (
            bool(self._settings.development_guild_id)
            and channel.guild.id == self._settings.development_guild_id
            and requester == channel.guild.owner_id
        )

    async def _scene_request_current(
        self, channel: discord.TextChannel, request: SceneRequest, requester: int
    ) -> bool:
        user = self.user
        if user is None or not await self._scene_scope_current(channel, requester):
            return False
        try:
            async with asyncio.timeout(6):
                fresh_channel = await self.fetch_channel(channel.id)
                if (
                    not isinstance(fresh_channel, discord.TextChannel)
                    or fresh_channel.guild.id != channel.guild.id
                    or not await self._scene_scope_current(fresh_channel, requester)
                ):
                    return False
                member = await fresh_channel.guild.fetch_member(user.id)
                permissions = fresh_channel.permissions_for(member)
                if not all(
                    (
                        permissions.view_channel,
                        permissions.send_messages,
                        permissions.attach_files,
                        permissions.read_message_history,
                    )
                ):
                    return False
                fresh = await fresh_channel.fetch_message(request.message_id)
                if (
                    fresh.author.id != requester
                    or request.author_id != requester
                    or fresh.author.bot
                    or fresh.webhook_id is not None
                    or fresh.content != request.content
                    or fresh.edited_at != request.edited_at
                    or fresh.created_at != request.created_at
                    or fresh.attachments
                    or fresh.embeds
                    or not timedelta(0) <= self._clock() - fresh.created_at <= MAX_REQUEST_AGE
                    or not self._is_direct_trigger(fresh)
                ):
                    return False
                return await self._scene_scope_current(fresh_channel, requester)
        except (discord.HTTPException, TimeoutError, LearningUnavailable):
            return False

    async def _respond_scene(
        self, channel: discord.TextChannel, anchor: discord.Message, region: str, requester: int
    ) -> bool:
        # Discord can update its cached Message in place during an edit. Freeze
        # the authorization before the first await, so both checks use the original.
        request = SceneRequest(
            anchor.id, anchor.author.id, anchor.content, anchor.created_at, anchor.edited_at
        )
        feature = self._scenes
        if feature is None or not await self._scene_scope_current(channel, requester):
            return False
        request_key = operation_key(channel.guild.id, channel.id, request.message_id)
        async with channel.typing():
            claim, image = await feature.prepare(
                region,
                request_key=request_key,
                channel_key=operation_key(channel.guild.id, channel.id),
                now=self._clock(),
                before_generation=lambda: self._scene_request_current(channel, request, requester),
            )
            if claim in {"duplicate", "blocked"}:
                return False
            if image is None:
                if not await self._scene_request_current(channel, request, requester):
                    return False
                await channel.send(
                    "Give me a little time before another picture.",
                    allowed_mentions=discord.AllowedMentions.none(),
                    nonce=request.message_id,
                )
            else:
                if not await self._scene_request_current(channel, request, requester):
                    await asyncio.to_thread(feature.store.finish, request_key, "blocked")
                    return False
                if image.source_check is not None and not await image.source_check():
                    await asyncio.to_thread(feature.store.finish, request_key, "blocked")
                    return False
                # Commit before send. Discord.py also enforces nonce uniqueness for
                # its internal transport retries. A new process never reopens this claim.
                await asyncio.to_thread(feature.store.finish, request_key, "send_uncertain")
                attachment = discord.File(
                    io.BytesIO(image.data),
                    filename="trubot-outdoors-generated.png",
                    description=image.description,
                )
                try:
                    await channel.send(
                        image.caption,
                        file=attachment,
                        nonce=request.message_id,
                        allowed_mentions=discord.AllowedMentions.none(),
                    )
                except Exception as error:
                    logger.warning(
                        "Requested scene publication uncertain error_type=%s", type(error).__name__
                    )
                    return False
                finally:
                    attachment.close()
                try:
                    await asyncio.to_thread(feature.store.finish, request_key, "posted")
                except LearningUnavailable:
                    # Publication already succeeded. Keep the durable uncertain
                    # claim and never send a second failure message or attachment.
                    logger.warning("Requested scene posted; outcome receipt unavailable")
        self._cancel_ambient(channel.id)
        self._participation.record_reply(channel.id, self._clock(), ambient=False)
        self._attention.activate(channel.id, self._clock())
        logger.info("Posted requested scene response image=%s", image is not None)
        return True

    async def _memory_author_scope(self, anchor: discord.Message | None) -> MemoryAuthorScope:
        learning = self._learning
        if learning is None or not learning.verified:
            raise LearningUnavailable("Verified memory identity required")
        identity = await asyncio.to_thread(learning.store.identity)
        if identity != learning.identity:
            raise LearningUnavailable("Memory identity changed")
        if anchor is None or anchor.author.bot:
            return MemoryAuthorScope.UNKNOWN_AUTHOR
        return (
            MemoryAuthorScope.SOURCE_AUTHOR
            if anchor.author.id == identity.user_id
            else MemoryAuthorScope.OTHER_AUTHOR
        )

    async def _reference_context(
        self, anchor: discord.Message | None, images: ImageCollector
    ) -> ConversationMessage | None:
        if anchor is None or self.user is None:
            return None
        reference = getattr(anchor, "reference", None)
        if not isinstance(reference, discord.MessageReference):
            return None
        if reference.channel_id != anchor.channel.id or reference.message_id is None:
            return ConversationMessage(
                "user", "[Referenced message unavailable.]", origin="reference"
            )
        try:
            # Refresh even a resolved reference, since cached content can be edited.
            message = await anchor.channel.fetch_message(reference.message_id)
            converted = await visual_message(
                message, bot_user_id=self.user.id, images=images, target=True
            )
            if converted is not None:
                return ConversationMessage(
                    converted.role,
                    REFERENCE_PREFIX + converted.content,
                    converted.images,
                    origin="reference",
                    author_user_id=converted.author_user_id,
                )
        except discord.HTTPException:
            return ConversationMessage(
                "user", "[Referenced message unavailable.]", origin="reference"
            )
        return None

    async def _memory_context(
        self,
        channel: DiscordChannel,
        target: str | None,
        history: list[ConversationMessage],
        *,
        requester_user_id: int | None = None,
        focus_author_user_id: int | None = None,
        visual_sink: list[ConversationImage] | None = None,
        visual_limit: int = 2,
        retrieval_query: str | None = None,
        photo_recipient_user_id: int | None = None,
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
        # Use the focused topic. Bot prose cannot establish personal evidence.
        # A referential timing/source request may look up an earlier exact quotation,
        # but only current eligible authored source text can satisfy that lookup.
        # Strip the speaker label once, preserving punctuation in the actual request.
        request = (target or "").split(": ", 1)[-1]
        if requester_recall(request):
            try:
                # Recheck the authoritative store, including withdrawal, rather
                # than trusting the ingestor's cached verification flag.
                source_identity = await asyncio.to_thread(memory.learning.identity)
            except LearningUnavailable:
                return ""
            if focus_author_user_id != source_identity.user_id:
                # The private corpus is Andrew's authored history. A peer asking
                # about their own words cannot inherit it in the test guild either.
                # Live human context stays available; no character source, graph
                # abstraction or voice example is retrieved for this request.
                return requester_context_unavailable()
        query = (
            retrieval_query
            if retrieval_query is not None
            else memory_followup_query(request, history)
        )
        lookup = recall_quotation(request, history)
        if lookup == "":
            return quotation_unavailable()
        quotation = lookup or ""
        if target is None and not (terms(query) or years(query)):
            query += " " + " ".join(
                m.content.split(": ", 1)[-1] for m in history[-4:] if m.role == "user"
            )
        try:
            candidates = await asyncio.to_thread(
                memory.candidates,
                query,
                guild_id=source_guild_id,
                now=self._clock(),
                quotation=quotation,
            )
            verified = []
            native_episodes: dict[int, NativeEpisode] = {}
            refreshed_sources: list[tuple[DiscordChannel, int, discord.Message]] = []
            verification_started = self._clock()
            verification_deadline = asyncio.get_running_loop().time() + 6
            # A fresh bounded page shares transport for nearby selected sources.
            # Never persist unselected rows or infer deletion from page absence.
            grouped: dict[int, list[int]] = {}
            for candidate in candidates:
                if candidate.source["kind"] == "discord":
                    grouped.setdefault(candidate.source["channel_id"], []).append(
                        candidate.source["message_id"]
                    )
            page_sources: dict[tuple[int, int], discord.Message] = {}
            denied_channels: set[int] = set()
            for channel_id, message_ids in grouped.items():
                source_channel = self.get_channel(channel_id)
                if (
                    len(message_ids) < 2
                    or not isinstance(source_channel, (discord.TextChannel, discord.Thread))
                    or not learning.accepts(source_channel)
                ):
                    continue
                remaining = verification_deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    break
                try:
                    page = await asyncio.wait_for(
                        learning.refresh_page(source_channel, message_ids),
                        timeout=min(1.5, remaining),
                    )
                    page_sources.update(((channel_id, key), value) for key, value in page.items())
                except (discord.Forbidden, discord.NotFound):
                    # A denied channel is not a reason to try another access path.
                    denied_channels.add(channel_id)
                except (discord.HTTPException, TimeoutError):
                    # Transient page loss can use existing exact reads within the
                    # same deadline. It cannot authorize cached source reuse.
                    pass
            for candidate in candidates:
                if candidate.source["kind"] == "discord":
                    source_channel = self.get_channel(candidate.source["channel_id"])
                    if not isinstance(source_channel, (discord.TextChannel, discord.Thread)):
                        continue
                    if not learning.accepts(source_channel) or source_channel.id in denied_channels:
                        continue
                    refreshed = page_sources.get(
                        (source_channel.id, candidate.source["message_id"])
                    )
                    if refreshed is None:
                        remaining = verification_deadline - asyncio.get_running_loop().time()
                        if remaining <= 0:
                            break
                        try:
                            refreshed = await asyncio.wait_for(
                                learning.refresh(source_channel, candidate.source["message_id"]),
                                timeout=min(4, remaining),
                            )
                        except (discord.HTTPException, TimeoutError):
                            # No permission/network access ever revives cached evidence.
                            continue
                    if refreshed is not None:
                        refreshed_sources.append(
                            (source_channel, candidate.source["message_id"], refreshed)
                        )
                        # Mandatory fresh source reads already contain media
                        # presence. An optional neighborhood timeout must not
                        # erase it, including for sources beyond the setup cap.
                        if (source_episode := source_media_episode(refreshed)) is not None:
                            native_episodes[candidate.source["message_id"]] = source_episode
                verified.append(candidate)
            # Verify every selected source first. Optional setup must never spend
            # time that a later mandatory source refresh needs.
            for source_channel, message_id, refreshed in (
                refreshed_sources[:2] if retrieval_query is None else []
            ):
                remaining = verification_deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    break
                try:
                    episode = await asyncio.wait_for(
                        collect_native_episode(
                            source_channel,
                            message_id,
                            identity=learning.identity,
                            now=self._clock(),
                            retention_days=learning.store.retention_days,
                            focus=refreshed,
                        ),
                        timeout=min(1.5, remaining),
                    )
                    if episode is not None:
                        native_episodes[message_id] = episode
                        # Optional durable metadata never turns peers into persona
                        # evidence or grants automatic native pattern eligibility.
                        with suppress(LearningUnavailable):
                            await asyncio.to_thread(
                                GraphStore(learning.store).record_native_context,
                                episode,
                                now=self._clock(),
                            )
                except (discord.HTTPException, TimeoutError):
                    # Context is optional; never use stale or guessed neighbors.
                    pass
            if self._learning is not None and self._learning.verified:
                packet = await asyncio.to_thread(
                    memory.render_packet,
                    verified,
                    verified_after=verification_started,
                    now=self._clock(),
                    request=request,
                    quotation=quotation,
                    native_episodes=native_episodes,
                )
                voice = (
                    ""
                    if retrieval_query is not None
                    or recent_recall(request)
                    or lookup is not None
                    or not packet.allow_voice_examples
                    else await asyncio.to_thread(
                        voice_context, memory.learning, query, guild_id=source_guild_id
                    )
                )
                recalled = packet.text
                if visual_sink is not None and recalled and visual_limit:
                    # Recheck source pixels as well as text on every continuation/send.
                    # Historical media is bound to this exact source, never the current question.
                    collector = ImageCollector()
                    collector.attempts = 2 - min(2, visual_limit)
                    evidence = []
                    for source_channel, message_id, source in refreshed_sources:
                        if (
                            photo_recipient_user_id is not None
                            and channel.guild.id == source_guild_id
                        ):
                            try:
                                recipient = await source_channel.guild.fetch_member(
                                    photo_recipient_user_id
                                )
                                access = source_channel.permissions_for(recipient)
                                if not (access.view_channel and access.read_message_history):
                                    continue
                            except discord.HTTPException:
                                continue
                        pixels, _ = await collector.collect(source)
                        if pixels:
                            visual_sink.extend(pixels)
                            evidence.append(
                                {
                                    "source_message_id": message_id,
                                    "pixel_hashes": [
                                        hashlib.sha256(p.data_url.encode()).hexdigest()
                                        for p in pixels
                                    ],
                                }
                            )
                    if evidence:
                        recalled += "\nVERIFIED HISTORICAL SOURCE PIXELS: " + json.dumps(evidence)
                        recalled += (
                            " Supplied images are the historical post's actual pixels. "
                            "They supersede neighborhood flags about missing pixels. "
                            "Describe visible content naturally in first person. "
                            "The post date is posting time, not the camera capture date. "
                            "Do not claim a sighting today or narrate retrieval machinery."
                        )
                if lookup is not None and not recalled:
                    return quotation_unavailable()
                return "\n".join(part for part in (recalled, voice) if part)
            return ""
        except LearningUnavailable:
            logger.warning("Response memory unavailable; source verification required")
            return recent_context_unavailable() if recent_recall(request) else ""

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
