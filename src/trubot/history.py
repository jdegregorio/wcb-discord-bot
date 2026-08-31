"""Conversion between Discord messages and provider-neutral model context."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

import discord

from trubot.conversation import ConversationMessage

MAX_HISTORY_MESSAGE_CHARS = 4_000


class HistoryChannel(Protocol):
    def history(
        self,
        *,
        limit: int,
        oldest_first: bool,
    ) -> AsyncIterator[discord.Message]: ...


async def collect_history(
    channel: HistoryChannel,
    *,
    bot_user_id: int,
    limit: int,
) -> list[ConversationMessage]:
    messages: list[ConversationMessage] = []
    async for message in channel.history(limit=limit, oldest_first=True):
        converted = convert_message(message, bot_user_id=bot_user_id)
        if converted is not None:
            messages.append(converted)
    return messages


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
        return None
    content = _truncate(content, MAX_HISTORY_MESSAGE_CHARS)

    if author_id == bot_user_id:
        return ConversationMessage(role="assistant", content=content)

    display_name = message.author.display_name.strip() or "Friend"
    return ConversationMessage(role="user", content=f"{display_name}: {content}")


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
