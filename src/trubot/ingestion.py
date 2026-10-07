"""Bounded background ingestion using the existing Discord client and allowlist."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime

import discord

from trubot.learning import LearningStore, LearningUnavailable, SourceMessage

logger = logging.getLogger(__name__)
Channel = discord.TextChannel | discord.Thread


class MessageIngestor:
    def __init__(
        self,
        store: LearningStore,
        allowed_channel_ids: frozenset[int],
        *,
        batch_size: int = 50,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.store = store
        self.identity = store.identity()
        self.channel_ids = allowed_channel_ids & self.identity.channel_ids
        self.batch_size = batch_size
        self.clock = clock or (lambda: datetime.now(UTC))
        self.verified = False

    def accepts(self, channel: Channel) -> bool:
        return channel.id in self.channel_ids and channel.guild.id == self.identity.guild_id

    async def verify_member(self, client: discord.Client) -> None:
        # A failed lookup pauses learning. Names never remap the pinned stable ID.
        self.verified = False
        guild = client.get_guild(self.identity.guild_id)
        if guild is None:
            raise LearningUnavailable("Verified guild unavailable")
        member = await guild.fetch_member(self.identity.user_id)
        if member.id != self.identity.user_id or member.bot:
            raise LearningUnavailable("Pinned member is no longer a human guild member")
        self.verified = True

    async def observe(self, message: discord.Message) -> None:
        if not self.verified or not isinstance(
            message.channel, (discord.TextChannel, discord.Thread)
        ):
            return
        if not self.accepts(message.channel):
            return
        now = self.clock()
        await asyncio.to_thread(
            self.store.observe, SourceMessage.from_discord(message, observed_at=now), now=now
        )

    async def catch_up(self, channel: Channel) -> int:
        if not self.verified or not self.accepts(channel):
            return 0
        now = self.clock()
        cursor = await asyncio.to_thread(self.store.cursor, channel.id, now=now)
        # Fetch the oldest page after the checkpoint. Live events never advance it.
        messages = [
            SourceMessage.from_discord(message, observed_at=now, authoritative=True)
            async for message in channel.history(
                limit=self.batch_size, after=discord.Object(id=cursor), oldest_first=True
            )
        ]
        await asyncio.to_thread(self.store.commit_batch, channel.id, messages, now=self.clock())
        return len(messages)

    async def refresh(self, channel: Channel, message_id: int) -> None:
        if not self.verified or not self.accepts(channel):
            return
        started = self.clock()
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await self.invalidate(channel.id, [message_id], deleted=True)
            return
        # Permission/network failures never imply deletion and never restore old text.
        await asyncio.to_thread(
            self.store.observe,
            SourceMessage.from_discord(message, observed_at=started, authoritative=True),
            now=self.clock(),
        )

    async def invalidate(self, channel_id: int, ids: list[int], *, deleted: bool) -> None:
        if channel_id in self.channel_ids:
            await asyncio.to_thread(
                self.store.invalidate, channel_id, ids, deleted=deleted, now=self.clock()
            )

    async def reconcile(self, channel: Channel) -> None:
        if not self.verified or not self.accepts(channel):
            return
        ids = await asyncio.to_thread(self.store.verification_targets, channel.id)
        for message_id in ids:
            await self.refresh(channel, message_id)

    async def cycle(self, client: discord.Client) -> None:
        if await asyncio.to_thread(self.store.is_withdrawn):
            self.verified = False
            return
        await self.verify_member(client)
        await asyncio.to_thread(self.store.prune, now=self.clock())
        for channel_id in sorted(self.channel_ids):
            channel = client.get_channel(channel_id)
            if not isinstance(channel, (discord.TextChannel, discord.Thread)):
                continue
            # Isolate permission/transport failures to their channel. Never log payloads.
            try:
                count = await self.catch_up(channel)
                await self.reconcile(channel)
                logger.info("Learning batch completed scanned=%d", count)
            except (discord.HTTPException, LearningUnavailable):
                logger.warning("Learning channel paused; source or private storage unavailable")
