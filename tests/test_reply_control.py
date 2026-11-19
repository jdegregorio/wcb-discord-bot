"""Private reply-control tokens must not escape as ordinary Discord speech."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from test_discord_client import fake_channel, fake_message, make_client
from test_response_repetition import SequenceAPI, responder

from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import ResponderError
from trubot.photo_action import PhotoAction

TARGET = "Casey: What dessert does the synthetic character prefer?"
ANSWER = "Caramel, according to that earlier conversation."
MARKER = "<NO_REPLY>"


@pytest.mark.parametrize("mode", [ReplyMode.DIRECT, ReplyMode.REACTION])
@pytest.mark.parametrize("draft", [MARKER, "<no_reply>", '"<NO_REPLY>"'])
async def test_addressed_control_output_gets_one_accounted_repair(mode, draft, monkeypatch):
    api = SequenceAPI(draft, ANSWER)
    r, ledger = responder(api, monkeypatch)
    assert await r.reply([], mode=mode, target=TARGET, safety_id="test") == ANSWER
    assert len(api.requests) == ledger.summary()["attempts"] == 2
    assert api.requests[1]["tool_choice"] == "none"
    assert "tools" not in api.requests[1]
    assert api.requests[1]["store"] is False
    assert api.requests[0]["model"] == api.requests[1]["model"]


@pytest.mark.parametrize("mode", [ReplyMode.FOLLOW_UP, ReplyMode.AMBIENT])
async def test_optional_participation_control_output_is_silent(mode, monkeypatch):
    api = SequenceAPI(MARKER)
    r, ledger = responder(api, monkeypatch)
    assert await r.reply([], mode=mode, target=TARGET, safety_id="test") is None
    assert len(api.requests) == ledger.summary()["attempts"] == 1


@pytest.mark.parametrize("current", [True, False, None])
async def test_control_repair_requires_current_private_memory(current, monkeypatch):
    api = SequenceAPI(MARKER, ANSWER)
    r, ledger = responder(api, monkeypatch)
    check = AsyncMock(return_value=current) if current is not None else None
    result = await r.reply(
        [ConversationMessage("user", "Synthetic support", origin="memory")],
        mode=ReplyMode.DIRECT,
        target=TARGET,
        safety_id="test",
        refresh_check=check,
    )
    assert result == (ANSWER if current else None)
    assert len(api.requests) == ledger.summary()["attempts"] == (2 if current else 1)


@pytest.mark.parametrize("candidate", [MARKER, "", RuntimeError("synthetic provider failure")])
async def test_failed_control_repair_cannot_publish_marker(candidate, monkeypatch):
    api = SequenceAPI(MARKER, candidate)
    r, ledger = responder(api, monkeypatch)
    with pytest.raises((ResponderError, RuntimeError)):
        await r.reply([], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test")
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_optional_quality_repair_cannot_replace_usable_draft_with_control(monkeypatch):
    draft = "That really sucks. You worked hard for that audition. I am here if you want to talk."
    api = SequenceAPI(draft, MARKER)
    r, _ = responder(api, monkeypatch)
    assert await r.reply([], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test") == draft
    assert len(api.requests) == 2


async def test_explicit_literal_control_request_is_preserved(monkeypatch):
    api = SequenceAPI(MARKER)
    r, _ = responder(api, monkeypatch)
    assert (
        await r.reply(
            [], mode=ReplyMode.DIRECT, target="Casey: Repeat <NO_REPLY> verbatim.", safety_id="test"
        )
        == MARKER
    )
    assert len(api.requests) == 1


async def test_unused_photo_offer_allows_control_repair_without_using_action(monkeypatch):
    api = SequenceAPI(MARKER, ANSWER)
    r, _ = responder(api, monkeypatch)
    retrieve = AsyncMock()
    photo = PhotoAction(retrieve)
    assert (
        await r.reply(
            [], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test", photo_action=photo
        )
        == ANSWER
    )
    retrieve.assert_not_awaited()
    assert len(api.requests) == 2


async def test_selected_context_cannot_add_control_repair(monkeypatch):
    api = SequenceAPI(MARKER)
    r, ledger = responder(api, monkeypatch)
    r._context_tools.select = lambda *_args, **_kwargs: [
        SimpleNamespace(name="synthetic", instructions="", definition=lambda: None)
    ]
    with pytest.raises(ResponderError):
        await r.reply([], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test")
    assert len(api.requests) == ledger.summary()["attempts"] == 1


@pytest.mark.parametrize("candidate", [ANSWER, MARKER])
@pytest.mark.parametrize("mode", ["direct", "reaction"])
async def test_actual_incoming_handlers_never_send_accidental_control(candidate, mode, monkeypatch):
    api = SequenceAPI(MARKER, candidate)
    api.close = AsyncMock()
    r, ledger = responder(api, monkeypatch)
    client, _, _, _ = make_client(responder=r)
    channel = fake_channel()
    message = fake_message(channel)
    message.id = 12345
    channel.fetch_message.return_value = message
    try:
        with patch.object(client, "get_channel", return_value=channel):
            if mode == "reaction":
                await client.on_raw_reaction_add(
                    SimpleNamespace(
                        channel_id=10,
                        user_id=1,
                        message_id=message.id,
                        emoji=SimpleNamespace(name="🍆"),
                        member=SimpleNamespace(bot=False),
                    )
                )
            else:
                await client.on_message(message)
        channel.send.assert_awaited_once()
        posted = channel.send.await_args.args[0]
        assert MARKER not in posted
        assert (posted == ANSWER) is (candidate == ANSWER)
        assert len(api.requests) == ledger.summary()["attempts"] == 2
    finally:
        await client.close()
