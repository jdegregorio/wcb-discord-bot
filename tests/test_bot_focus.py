"""Authenticated bot-source attribution must survive text reaction conversion."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from test_discord_client import fake_channel, fake_message, make_client
from test_openai_responder import FakeOpenAI, make_responder

from trubot.conversation import ReplyMode

LABEL = "[Bot source, not personal evidence.]"


@pytest.mark.parametrize("author_id", [999, 50])
@pytest.mark.parametrize("display_name", ["Trubot", "Andrew Truax"])
async def test_text_reaction_keeps_authenticated_bot_source(author_id, display_name):
    client, responder, _, _ = make_client()
    channel = fake_channel()
    anchor = fake_message(channel, user_id=author_id)
    anchor.author.bot = True
    anchor.author.display_name = display_name
    anchor.clean_content = anchor.content = "I prefer invented caramel ice cream."
    anchor.attachments = []
    anchor.embeds = []
    channel.fetch_message.return_value = anchor
    payload = SimpleNamespace(
        channel_id=channel.id,
        user_id=1,
        message_id=123,
        emoji=SimpleNamespace(name="🍆"),
        member=SimpleNamespace(bot=False),
    )
    try:
        with patch.object(client, "get_channel", return_value=channel):
            await client.on_raw_reaction_add(payload)
        messages, mode, _, target = responder.calls[0]
        assert mode is ReplyMode.REACTION
        focus = [row for row in messages if row.origin == "focus"]
        assert len(focus) == 1
        assert focus[0].role == "user"
        assert focus[0].author_user_id is None
        assert focus[0].content == target == f"{display_name}: {anchor.content} {LABEL}"
        channel.send.assert_awaited_once_with("Hot")
    finally:
        await client.close()


@pytest.mark.parametrize("bot", [False, True])
async def test_full_handler_to_provider_retains_one_complete_text_focus(bot):
    api = FakeOpenAI()
    actual_responder = make_responder(api)
    client, _, _, _ = make_client(responder=actual_responder)
    channel = fake_channel()
    anchor = fake_message(channel, user_id=50)
    anchor.author.bot = bot
    anchor.author.display_name = "Andrew Truax"
    anchor.clean_content = anchor.content = "A completely fictional scene for discussion."
    anchor.attachments = []
    anchor.embeds = []
    original_target = f"Andrew Truax: {anchor.content}"
    try:
        assert await client._respond(
            channel,
            mode=ReplyMode.REACTION,
            requester_user_id=1,
            anchor=anchor,
            target=original_target,
        )
        request = api.responses.request
        assert request is not None
        expected_target = original_target + (f" {LABEL}" if bot else "")
        # The added focus replaces the formatted target rather than duplicating
        # text, so ordinary human input stays byte-for-byte compatible.
        assert request["input"] == [
            {"role": "user", "content": "Joe: Code 12346633"},
            {
                "role": "user",
                "content": "REACTION TARGET - answer this now; earlier messages are context only:\n"
                + expected_target,
            },
        ]
        assert request["store"] is False
        assert LABEL not in request["instructions"]
        channel.send.assert_awaited_once_with("Hot")
    finally:
        await client.close()
