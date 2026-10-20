"""Fresh-joke requests must not silently exempt the immediately preceding punchline."""

from unittest.mock import AsyncMock

import pytest
from test_response_repetition import SequenceAPI, responder

from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import _stale_bot_echo

OLD = "The tray is for your belongings; the conveyor belt is for your playoff hopes."
NEW = "The metal detector only goes off for championship rings."
FOCUS = "Casey: Give me a different joke about that same scene."


def history():
    return [
        ConversationMessage("user", "Casey: Imagine airport security. Give me a joke."),
        ConversationMessage("assistant", OLD),
    ]


@pytest.mark.parametrize("mode", [ReplyMode.DIRECT, ReplyMode.FOLLOW_UP, ReplyMode.REACTION])
async def test_explicit_new_joke_repairs_an_immediate_echo_once(mode, monkeypatch):
    api = SequenceAPI(OLD, NEW)
    r, ledger = responder(api, monkeypatch)
    assert await r.reply(history(), mode=mode, safety_id="test", target=FOCUS) == NEW
    assert len(api.requests) == ledger.summary()["attempts"] == 2
    assert api.requests[0]["input"] == api.requests[1]["input"][:-2]
    assert api.requests[1]["input"][-2] == {"role": "assistant", "content": OLD}
    assert api.requests[1]["store"] is False
    assert api.requests[1]["model"] == api.requests[0]["model"]
    assert "different comic idea" in api.requests[1]["input"][-1]["content"]


@pytest.mark.parametrize(
    "focus_request",
    [
        "Give me a different joke about airport security.",
        "Could you tell us a fresh punchline?",
        "Another short joke, please.",
        "Try a new one-line quip.",
        "Please give me another joke.",
    ],
)
def test_clear_novelty_requests_detect_exact_and_partial_immediate_echoes(focus_request):
    assert _stale_bot_echo(OLD, history(), "Casey: " + focus_request)
    assert _stale_bot_echo("Well. " + OLD, history(), "Casey: " + focus_request)


@pytest.mark.parametrize(
    "focus_request",
    [
        "Again?",
        "Give me a different factual answer.",
        "What is your new favorite team?",
        "I heard a different joke yesterday.",
        "Don't give me another joke.",
        "Did I tell you a new joke?",
        "Another one?",
        "Another joke would be inappropriate.",
        "Another bit of advice, please.",
        "Give me a different bit of information.",
        "Quote a different joke you told earlier.",
        "Repeat that joke verbatim.",
        "Give me a different joke, then quote that earlier one.",
    ],
)
def test_ambiguous_factual_and_literal_requests_preserve_immediate_continuity(focus_request):
    assert not _stale_bot_echo(OLD, history(), "Casey: " + focus_request)


@pytest.mark.parametrize("origin", ["memory", "reference", "focus"])
def test_only_conversation_bot_words_can_be_an_echo(origin):
    assert not _stale_bot_echo(OLD, [ConversationMessage("assistant", OLD, origin=origin)], FOCUS)


def test_short_factual_human_and_explicit_reference_continuity_stays_intact():
    assert not _stale_bot_echo("White Sox", [ConversationMessage("assistant", "White Sox")], FOCUS)
    assert not _stale_bot_echo(OLD, [ConversationMessage("user", OLD)], FOCUS)
    assert not _stale_bot_echo(
        OLD, [*history(), ConversationMessage("user", OLD, origin="reference")], FOCUS
    )
    assert not _stale_bot_echo(OLD, history(), None)
    assert not _stale_bot_echo(NEW, history(), FOCUS)


@pytest.mark.parametrize("current", [False, True])
async def test_novelty_repair_requires_the_existing_fresh_private_packet(current, monkeypatch):
    api = SequenceAPI(OLD, NEW)
    r, ledger = responder(api, monkeypatch)
    check = AsyncMock(return_value=current)
    messages = [*history(), ConversationMessage("user", "Invented source.", origin="memory")]
    assert await r.reply(
        messages,
        mode=ReplyMode.FOLLOW_UP,
        safety_id="test",
        target=FOCUS,
        refresh_check=check,
    ) == (NEW if current else OLD)
    check.assert_awaited_once_with()
    assert len(api.requests) == ledger.summary()["attempts"] == (2 if current else 1)


async def test_unchanged_second_draft_never_loops(monkeypatch):
    api = SequenceAPI(OLD, OLD)
    r, ledger = responder(api, monkeypatch)
    assert await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target=FOCUS) == OLD
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_optional_failure_keeps_the_accounted_draft(monkeypatch):
    from trubot.budget import BudgetExceeded

    api = SequenceAPI(OLD, BudgetExceeded("maintenance limit"))
    r, _ = responder(api, monkeypatch)
    assert await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target=FOCUS) == OLD
    assert len(api.requests) == 2


async def test_repair_can_still_decline_another_recipient(monkeypatch):
    api = SequenceAPI(OLD, "<NO_REPLY>")
    r, ledger = responder(api, monkeypatch)
    assert (
        await r.reply(history(), mode=ReplyMode.FOLLOW_UP, safety_id="test", target=FOCUS) is None
    )
    assert len(api.requests) == ledger.summary()["attempts"] == 2


@pytest.mark.parametrize("followup", [False, True])
async def test_actual_message_handler_posts_the_repaired_joke(followup, monkeypatch):
    from test_discord_client import fake_channel, fake_message, make_client, message_for_history

    api = SequenceAPI(OLD, NEW)
    r, ledger = responder(api, monkeypatch)
    monkeypatch.setattr(api, "close", AsyncMock(), raising=False)
    client, _, _, _ = make_client(responder=r)
    channel = fake_channel()
    channel.history_messages[:] = [
        message_for_history("Imagine airport security. Give me one joke.", author_id=1),
        message_for_history(OLD, author_id=999, bot=True, name="Trubot"),
    ]
    message = fake_message(channel, direct=not followup)
    message.content = message.clean_content = (
        "" if followup else "🤖 "
    ) + "Give me a different joke about that same scene."
    if followup:
        client._attention.activate(channel.id, client._clock())
    try:
        await client.on_message(message)
        channel.send.assert_awaited_once_with(NEW)
        assert len(api.requests) == ledger.summary()["attempts"] == 2
    finally:
        await client.close()
