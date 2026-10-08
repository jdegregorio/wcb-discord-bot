"""Conversion between Discord messages and provider-neutral model context."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Protocol

import discord

from trubot.conversation import ConversationMessage
from trubot.vision import ImageCollector, image_urls

MAX_HISTORY_MESSAGE_CHARS = 4_000


class HistoryChannel(Protocol):
    def history(
        self,
        *,
        limit: int,
        oldest_first: bool,
        before: discord.Message | None,
        after: datetime,
    ) -> AsyncIterator[discord.Message]: ...


async def collect_history(
    channel: HistoryChannel,
    *,
    bot_user_id: int,
    limit: int,
    before: discord.Message | None,
    after: datetime,
    images: ImageCollector | None = None,
) -> list[ConversationMessage]:
    # Discord returns the channel's oldest messages when oldest_first=True and
    # no lower cursor is supplied. Fetch the newest bounded slice, then reverse
    # it locally so the model still receives natural chronological context.
    recent = [
        message
        async for message in channel.history(
            limit=limit,
            oldest_first=False,
            before=before,
            after=after,
        )
    ]
    messages: list[ConversationMessage] = []
    for message in recent:
        converted = await visual_message(message, bot_user_id=bot_user_id, images=images)
        if converted is not None:
            messages.append(converted)
    return list(reversed(messages))


def convert_message(
    message: discord.Message,
    *,
    bot_user_id: int,
) -> ConversationMessage | None:
    author_id = message.author.id
    if message.author.bot and author_id != bot_user_id:
        return None

    content = message.clean_content.strip()
    if not content:
        if not image_urls(message) and not any(
            (a.content_type or "").startswith("image/") for a in getattr(message, "attachments", ())
        ):
            return None
        content = "[image attached]"
    content = _truncate(content, MAX_HISTORY_MESSAGE_CHARS)

    if author_id == bot_user_id:
        return ConversationMessage(role="assistant", content=content)

    display_name = message.author.display_name.strip() or "Friend"
    return ConversationMessage(role="user", content=f"{display_name}: {content}")


async def visual_message(
    message: discord.Message,
    *,
    bot_user_id: int,
    images: ImageCollector | None,
    target: bool = False,
) -> ConversationMessage | None:
    converted = convert_message(message, bot_user_id=bot_user_id)
    if target and (converted is None or message.author.bot):
        label = " [Bot source, not personal evidence.]" if message.author.bot else ""
        converted = ConversationMessage("user", message_target(message) + label)
    if converted is None or images is None or converted.role != "user":
        return converted
    pixels, notice = await images.collect(message)
    return ConversationMessage(converted.role, converted.content + notice, pixels)


def message_target(message: discord.Message) -> str:
    """Return a speaker-labelled Discord message for explicit model focus."""

    content = message.clean_content.strip() or "[message with no text]"
    display_name = message.author.display_name.strip() or "Friend"
    return f"{display_name}: {_truncate(content, MAX_HISTORY_MESSAGE_CHARS)}"


def clamp_discord_message(message: str, limit: int = 2_000) -> str:
    """Enforce Discord's message limit without splitting a one-liner into spam."""

    cleaned = message.strip()
    if len(cleaned) <= limit:
        return cleaned
    cutoff = cleaned.rfind(" ", 0, limit - 1)
    if cutoff < limit // 2:
        cutoff = limit - 1
    return f"{cleaned[:cutoff].rstrip()}…"


def _truncate(value: str, limit: int) -> str:
    return value if len(value) <= limit else f"{value[: limit - 1].rstrip()}…"
