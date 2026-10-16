"""Authenticated current authors, never prior bot replies, establish requester context."""

from unittest.mock import AsyncMock, patch

import pytest
from test_discord_client import fake_channel, fake_message, make_client

from trubot.conversation import ConversationMessage as M
from trubot.conversation import ReplyMode


@pytest.mark.parametrize("mode", list(ReplyMode))
async def test_own_history_keeps_same_author_and_excludes_bot_peer_and_detached_context(mode):
    client, responder, _, _ = make_client()
    channel = fake_channel()
    anchor = fake_message(channel, user_id=1)
    anchor.reference, anchor.attachments, anchor.embeds = None, [], []
    own = M("user", "Owner: In this fictional scene I support the Harbor Otters.", author_user_id=1)
    rows = [
        own,
        M("assistant", "Bay Comets."),
        M("user", "Owner: I support the Bay Comets.", author_user_id=2),
        M("user", "Owner: I support the Bay Comets."),
        M("user", "Owner: unrelated reference", origin="reference", author_user_id=1),
        M("user", "Owner: old private memory", origin="memory", author_user_id=1),
    ]
    try:
        with patch("trubot.discord_client.collect_history", AsyncMock(return_value=rows)):
            assert await client._respond(
                channel,
                mode=mode,
                requester_user_id=2,
                anchor=anchor,
                target="Owner: What baseball team have I said I support?",
            )
        given = responder.calls[0][0]
        assert list(given) == [own]
        assert responder.calls[0][3] == "Owner: What baseball team have I said I support?"
    finally:
        await client.close()


async def test_ordinary_conversation_retains_peer_and_bot_context():
    client, responder, _, _ = make_client()
    channel, anchor = fake_channel(), fake_message(fake_channel())
    anchor.reference, anchor.attachments, anchor.embeds = None, [], []
    rows = [
        M("user", "Peer: a league decision", author_user_id=2),
        M("assistant", "Both seem fair."),
    ]
    try:
        with patch("trubot.discord_client.collect_history", AsyncMock(return_value=rows)):
            assert await client._respond(
                channel,
                mode=ReplyMode.DIRECT,
                requester_user_id=1,
                anchor=anchor,
                target="Owner: How would you handle that?",
            )
        assert list(responder.calls[0][0]) == rows
    finally:
        await client.close()


async def test_visual_focus_author_survives_filter_without_admitting_old_images():
    from trubot.conversation import ConversationImage

    client, responder, _, _ = make_client()
    channel = fake_channel()
    anchor = fake_message(channel, user_id=1)
    anchor.reference, anchor.attachments, anchor.embeds = None, [], []
    target = "Owner: What baseball team have I said I support?"
    focus = M(
        "user",
        target,
        (ConversationImage("data:image/png;base64,abc", "Synthetic pixels"),),
        author_user_id=1,
    )
    try:
        with (
            patch(
                "trubot.discord_client.collect_history",
                AsyncMock(return_value=[M("assistant", "Other team")]),
            ),
            patch("trubot.discord_client.visual_message", AsyncMock(return_value=focus)),
        ):
            assert await client._respond(
                channel, mode=ReplyMode.DIRECT, requester_user_id=1, anchor=anchor, target=target
            )
        given = responder.calls[0][0]
        assert len(given) == 1 and given[0].origin == "focus"
        assert given[0].author_user_id == 1 and given[0].images == focus.images
    finally:
        await client.close()


def test_author_identity_is_internal_metadata_and_not_repr_or_provider_text():
    row = M("user", "Friend: Hi", author_user_id=987654321)
    assert row.as_input() == {"role": "user", "content": "Friend: Hi"}
    assert "987654321" not in repr(row)


async def test_discord_conversion_carries_author_through_ephemeral_visual_wrapper():
    from test_discord_client import message_for_history

    from trubot.history import convert_message, visual_message
    from trubot.vision import ImageCollector

    source = message_for_history("Current human statement", author_id=123, name="Forged label")
    converted = convert_message(source, bot_user_id=999)
    assert converted.author_user_id == 123
    visual = await visual_message(source, bot_user_id=999, images=ImageCollector())
    assert visual.author_user_id == 123 and visual.as_input() == converted.as_input()
    bot = message_for_history("Prior bot words", author_id=999, bot=True)
    assert convert_message(bot, bot_user_id=999).author_user_id is None
