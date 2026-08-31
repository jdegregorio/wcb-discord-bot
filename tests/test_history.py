from collections.abc import AsyncIterator
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast

import discord
import pytest

from trubot.history import (
    HistoryChannel,
    clamp_discord_message,
    collect_history,
    convert_message,
    message_target,
)


def fake_message(
    content: str,
    *,
    author_id: int = 1,
    author_bot: bool = False,
    display_name: str = "Tim",
) -> discord.Message:
    return cast(
        discord.Message,
        SimpleNamespace(
            clean_content=content,
            author=SimpleNamespace(
                id=author_id,
                bot=author_bot,
                display_name=display_name,
            ),
        ),
    )


def test_human_messages_get_a_readable_speaker_prefix() -> None:
    converted = convert_message(fake_message(" hello "), bot_user_id=99)
    assert converted is not None
    assert converted.role == "user"
    assert converted.content == "Tim: hello"


def test_own_messages_are_assistant_context_without_a_prefix() -> None:
    converted = convert_message(
        fake_message(" Hot ", author_id=99, author_bot=True, display_name="Trubot"),
        bot_user_id=99,
    )
    assert converted is not None
    assert converted.role == "assistant"
    assert converted.content == "Hot"


def test_other_bots_and_empty_messages_are_ignored() -> None:
    assert convert_message(fake_message("noise", author_bot=True), bot_user_id=99) is None
    assert convert_message(fake_message("   "), bot_user_id=99) is None


def test_long_history_items_are_bounded() -> None:
    converted = convert_message(fake_message("x" * 5_000), bot_user_id=99)
    assert converted is not None
    assert len(converted.content) <= 4_005  # speaker prefix plus bounded body
    assert converted.content.endswith("…")


class FakeChannel:
    def __init__(self, messages: list[discord.Message]) -> None:
        self.messages = messages
        self.request: tuple[int, bool, discord.Message | None, datetime] | None = None

    async def history(
        self,
        *,
        limit: int,
        oldest_first: bool,
        before: discord.Message | None,
        after: datetime,
    ) -> AsyncIterator[discord.Message]:
        self.request = (limit, oldest_first, before, after)
        for message in self.messages:
            yield message


@pytest.mark.asyncio
async def test_collect_history_preserves_chronological_order() -> None:
    anchor = fake_message("current", author_id=2, display_name="Jim")
    cutoff = datetime(2026, 8, 30, 6, tzinfo=UTC)
    channel = FakeChannel(
        [
            fake_message("reply", author_id=99, author_bot=True, display_name="Trubot"),
            fake_message("ignored", author_id=50, author_bot=True, display_name="OtherBot"),
            fake_message("first", author_id=1, display_name="Tim"),
        ]
    )
    result = await collect_history(
        cast(HistoryChannel, channel),
        bot_user_id=99,
        limit=15,
        before=anchor,
        after=cutoff,
    )

    assert [message.content for message in result] == ["Tim: first", "reply"]
    assert channel.request == (15, False, anchor, cutoff)


def test_message_target_includes_author_and_handles_no_text() -> None:
    assert message_target(fake_message("trade this")) == "Tim: trade this"
    assert message_target(fake_message(" ", display_name="")) == "Friend: [message with no text]"


def test_discord_output_is_trimmed_at_a_word_boundary() -> None:
    assert clamp_discord_message(" short ") == "short"
    output = clamp_discord_message("word " * 500, limit=100)
    assert len(output) <= 100
    assert output.endswith("…")
    assert clamp_discord_message("x" * 150, limit=100) == ("x" * 99) + "…"
