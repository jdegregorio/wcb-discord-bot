"""Ephemeral, attributed human setup around a freshly verified native source."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import discord

from trubot.learning import Identity, SourceMessage, _time

# Context must be complete: silently clipped qualifications can reverse meaning.
MAX_CONTEXT_BYTES = 600


@dataclass(frozen=True, slots=True)
class NativeEpisode:
    # Never log raw human context through a dataclass representation.
    source_text: str = field(repr=False)
    source_edited_at: str | None = field(repr=False)
    neighbors: tuple[dict[str, Any], ...] = field(repr=False)
    gaps: tuple[str, ...] = ()
    source: SourceMessage | None = field(default=None, repr=False)
    dependencies: tuple[dict[str, Any], ...] = field(default=(), repr=False)

    def matches(self, text: str, edited_at: str | None) -> bool:
        return self.source_text == text and self.source_edited_at == edited_at

    def as_data(self) -> dict[str, Any]:
        return {"human_messages": list(self.neighbors), "gaps": list(self.gaps)}


def _human(
    message: discord.Message, *, channel: discord.TextChannel | discord.Thread, floor: datetime
) -> bool:
    return (
        message.channel.id == channel.id
        and message.guild is not None
        and message.guild.id == channel.guild.id
        and not message.author.bot
        and message.webhook_id is None
        and floor <= message.created_at
    )


def _context_row(
    message: discord.Message, focus: discord.Message, identity: Identity
) -> dict[str, Any]:
    reference = getattr(message, "reference", None)
    focus_reference = getattr(focus, "reference", None)
    reply_to = (
        reference.message_id
        if isinstance(reference, discord.MessageReference)
        and reference.channel_id == focus.channel.id
        else None
    )
    return {
        "message_id": message.id,
        "created_at": _time(message.created_at),
        "edited_at": _time(message.edited_at) if message.edited_at else None,
        "author": "verified Andrew (context only)"
        if message.author.id == identity.user_id
        else "peer (not persona evidence)",
        "speaker_id": message.author.id,
        "position": "before" if message.id < focus.id else "after",
        "reply_to_message_id": reply_to,
        "focus_replies_to_this": bool(
            isinstance(focus_reference, discord.MessageReference)
            and focus_reference.channel_id == focus.channel.id
            and focus_reference.message_id == message.id
        ),
        "text": message.content,
        "visual_context": "pixels not retrieved; do not interpret image-dependent meaning"
        if getattr(message, "attachments", ()) or getattr(message, "embeds", ())
        else "no captured media",
    }


async def collect_native_episode(
    channel: discord.TextChannel | discord.Thread,
    message_id: int,
    *,
    identity: Identity,
    now: datetime,
    retention_days: int,
    focus: discord.Message | None = None,
) -> NativeEpisode | None:
    """Read one bounded same-channel neighborhood. Never persist peer text or follow links."""
    if channel.guild.id != identity.guild_id or channel.id not in identity.channel_ids:
        return None
    floor = now - timedelta(days=retention_days)
    focus = focus or await channel.fetch_message(message_id)
    if (
        focus.id != message_id
        or not _human(focus, channel=channel, floor=floor)
        or focus.author.id != identity.user_id
        or focus.created_at > now
    ):
        return None
    neighbors: dict[int, dict[str, Any]] = {}
    dependencies: dict[int, dict[str, Any]] = {}
    gaps: list[str] = []
    oversized: set[int] = set()

    def admit(message: discord.Message) -> None:
        row = _context_row(message, focus, identity)
        # Persistable metadata includes omitted oversized humans, never their text.
        dependencies[message.id] = {
            key: row[key]
            for key in (
                "message_id",
                "created_at",
                "edited_at",
                "speaker_id",
                "position",
                "reply_to_message_id",
                "focus_replies_to_this",
            )
        } | {
            "channel_id": channel.id,
            "guild_id": channel.guild.id,
            "content_sha256": hashlib.sha256(message.content.encode()).hexdigest(),
            "media_present": bool(
                getattr(message, "attachments", ()) or getattr(message, "embeds", ())
            ),
        }
        if len(message.content.encode("utf-8")) > MAX_CONTEXT_BYTES:
            oversized.add(message.id)
        else:
            neighbors[message.id] = row

    if not hasattr(focus, "attachments") or not hasattr(focus, "embeds"):
        gaps.append("source media metadata unavailable")
    elif focus.attachments or focus.embeds:
        gaps.append("source media pixels not retrieved; do not interpret image-dependent meaning")
    try:
        async for message in channel.history(limit=5, around=discord.Object(id=message_id)):
            if (
                message.id != focus.id
                and _human(message, channel=channel, floor=floor)
                and message.created_at <= now
                and abs((message.created_at - focus.created_at).total_seconds()) <= 1800
            ):
                admit(message)
    except discord.HTTPException as error:
        gaps.append("nearby human context unavailable")
        if isinstance(error, discord.Forbidden):
            return NativeEpisode(
                focus.content[:4000],
                _time(focus.edited_at) if focus.edited_at else None,
                (),
                tuple(gaps),
                source=SourceMessage.from_discord(focus, observed_at=now, authoritative=True),
            )
    reference = getattr(focus, "reference", None)
    if isinstance(reference, discord.MessageReference) and reference.message_id is not None:
        if reference.channel_id != channel.id:
            gaps.append("cross-channel reference not followed")
        elif (
            reference.message_id not in neighbors
            and reference.message_id not in oversized
            and reference.message_id != focus.id
        ):
            try:
                message = await channel.fetch_message(reference.message_id)
                if (
                    message.id == reference.message_id
                    and _human(message, channel=channel, floor=floor)
                    and message.created_at <= focus.created_at
                ):
                    admit(message)
                else:
                    gaps.append("referenced human context outside scope")
            except discord.HTTPException:
                gaps.append("referenced human context unavailable")
    if oversized:
        gaps.append(
            f"{len(oversized)} human context messages omitted for size; "
            "their full meaning is unavailable"
        )
    return NativeEpisode(
        focus.content[:4000],
        _time(focus.edited_at) if focus.edited_at else None,
        tuple(neighbors[key] for key in sorted(neighbors)[:5]),
        tuple(gaps),
        source=SourceMessage.from_discord(focus, observed_at=now, authoritative=True),
        dependencies=tuple(dependencies[key] for key in sorted(dependencies)[:5]),
    )
