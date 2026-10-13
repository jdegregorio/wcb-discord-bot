"""Fresh bounded native context reads; stored captures never certify visibility."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import discord

from trubot.graph import GraphStore
from trubot.learning import LearningUnavailable, SourceMessage, _time
from trubot.native_context import (
    MAX_CONTEXT_BYTES,
    NativeEpisode,
    _context_row,
    _human,
    dependency_metadata,
)

if TYPE_CHECKING:
    from trubot.ingestion import MessageIngestor


async def _scope(ingestor: MessageIngestor, channel: discord.TextChannel | discord.Thread) -> None:
    # Withdrawal and identity are authoritative before every network stage.
    if (
        not ingestor.verified
        or not ingestor.accepts(channel)
        or await asyncio.to_thread(ingestor.store.identity) != ingestor.identity
    ):
        raise LearningUnavailable("Native context verification scope unavailable")


async def verify_native_context(
    ingestor: MessageIngestor, channel: discord.TextChannel | discord.Thread, data: dict[str, Any]
) -> NativeEpisode | None:
    """Bound the complete current-source/context verification to six seconds."""
    async with asyncio.timeout(6):
        return await _verify_native_context(ingestor, channel, data)


async def _verify_native_context(
    ingestor: MessageIngestor,
    channel: discord.TextChannel | discord.Thread,
    data: dict[str, Any],
) -> NativeEpisode | None:
    """Check retained dependencies against fresh reads. Text stays ephemeral.

    Callers must check again immediately before any future learning use. Adjacency
    is bounded, pixels are absent, and this does not open automatic pattern learning.
    Transport errors propagate without pretending the human message was deleted.
    """
    graph = GraphStore(ingestor.store)
    await _scope(ingestor, channel)
    if data["ref"]["channel_id"] != channel.id or len(data["dependencies"]) > 5:
        raise LearningUnavailable("Native context routing or size invalid")
    if not await asyncio.to_thread(graph.native_context_current, data, now=ingestor.clock()):
        return None
    observed = ingestor.clock()
    focus = await ingestor.refresh(channel, data["ref"]["message_id"])
    await _scope(ingestor, channel)
    floor = ingestor.clock() - timedelta(days=ingestor.store.retention_days)
    if (
        focus is None
        or focus.id != data["ref"]["message_id"]
        or not _human(focus, channel=channel, floor=floor)
        or focus.author.id != ingestor.identity.user_id
        or focus.created_at > ingestor.clock()
        or bool(getattr(focus, "attachments", ()) or getattr(focus, "embeds", ()))
        != any(gap.startswith("source media pixels not retrieved") for gap in data["gaps"])
        or not await asyncio.to_thread(graph.native_context_current, data, now=ingestor.clock())
    ):
        return None
    neighbors = []
    # Match only retained dependencies. New neighbors are never added to learning.
    current = {}
    if data["dependencies"]:
        await _scope(ingestor, channel)
        async for row in channel.history(limit=10, around=discord.Object(id=focus.id)):
            current[row.id] = row
    for dependency in data["dependencies"]:
        await _scope(ingestor, channel)
        if dependency["channel_id"] != channel.id or dependency["guild_id"] != channel.guild.id:
            raise LearningUnavailable("Native dependency outside scope")
        message = current.get(dependency["message_id"])
        if message is None and dependency["focus_replies_to_this"]:
            reference = getattr(focus, "reference", None)
            if (
                isinstance(reference, discord.MessageReference)
                and reference.channel_id == channel.id
                and reference.message_id == dependency["message_id"]
            ):
                message = await channel.fetch_message(dependency["message_id"])
        if message is None:
            return None
        if (
            message.id != dependency["message_id"]
            or not _human(message, channel=channel, floor=floor)
            or message.created_at > ingestor.clock()
            or dependency_metadata(message, focus, ingestor.identity) != dependency
        ):
            return None
        if len(message.content.encode()) <= MAX_CONTEXT_BYTES:
            neighbors.append(_context_row(message, focus, ingestor.identity))
    await _scope(ingestor, channel)
    if not await asyncio.to_thread(graph.native_context_current, data, now=ingestor.clock()):
        return None
    return NativeEpisode(
        focus.content[:4000],
        _time(focus.edited_at) if focus.edited_at else None,
        tuple(neighbors),
        tuple(data["gaps"]),
        source=SourceMessage.from_discord(focus, observed_at=observed, authoritative=True),
        dependencies=tuple(data["dependencies"]),
    )


async def reconcile_native_context(
    ingestor: MessageIngestor, client: discord.Client
) -> dict[str, int]:
    """At most two captures/six HTTP reads/six seconds per existing cycle."""
    result = {"verified": 0, "removed": 0, "unavailable": 0}
    if not ingestor.verified:
        return result
    graph = GraphStore(ingestor.store)
    try:
        async with asyncio.timeout(6):
            if await asyncio.to_thread(ingestor.store.identity) != ingestor.identity:
                raise LearningUnavailable("Native context identity changed")
            captures = await asyncio.to_thread(
                graph.native_context_targets, now=ingestor.clock(), channel_ids=ingestor.channel_ids
            )
            for data in captures:
                channel = client.get_channel(data["ref"]["channel_id"])
                if not isinstance(channel, (discord.TextChannel, discord.Thread)):
                    result["unavailable"] += 1
                    continue
                try:
                    episode = await verify_native_context(ingestor, channel, data)
                except (discord.NotFound, discord.Forbidden):
                    episode = None
                except (discord.HTTPException, TimeoutError):
                    # No current certificate. Retain observed metadata on transient failure.
                    result["unavailable"] += 1
                    continue
                if episode is None:
                    result["removed"] += int(
                        await asyncio.to_thread(graph.discard_native_context, data)
                    )
                else:
                    result["verified"] += 1
    except TimeoutError:
        result["unavailable"] += 1
    return result
