"""Explicit novelty can refresh a short unchanged punchline without broad rewriting."""

from unittest.mock import AsyncMock

import pytest
from test_response_repetition import SequenceAPI, responder

from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import _stale_bot_echo

FOCUS = "Casey: Give me a different joke about that same fictional scene."


def history(old):
    return [
        ConversationMessage("user", "Casey: A beaver runs the draft. Give me one short joke."),
        ConversationMessage("assistant", old),
    ]


@pytest.mark.parametrize(
    "old", ["Dam good draft.", "All dam upside.", "Hot", "A dam good draft, apparently."]
)
def test_explicit_novelty_detects_short_immediate_copy(old):
    assert _stale_bot_echo(old, history(old), FOCUS)


@pytest.mark.parametrize("followup", [False, True])
async def test_real_handler_refreshes_a_short_copied_punchline(followup, monkeypatch):
    from test_discord_client import fake_channel, fake_message, make_client, message_for_history

    old, new = "Dam good draft.", "He chewed through his entire draft board."
    api = SequenceAPI(old, new)
    r, ledger = responder(api, monkeypatch)
    monkeypatch.setattr(api, "close", AsyncMock(), raising=False)
    client, _, _, _ = make_client(responder=r)
    channel = fake_channel()
    channel.history_messages[:] = [
        message_for_history("A beaver runs the draft. Give me one short joke.", author_id=1),
        message_for_history(old, author_id=999, bot=True, name="Trubot"),
    ]
    message = fake_message(channel, direct=not followup)
    message.content = message.clean_content = ("" if followup else "🤖 ") + FOCUS.split(": ", 1)[1]
    if followup:
        client._attention.activate(channel.id, client._clock())
    try:
        await client.on_message(message)
        channel.send.assert_awaited_once_with(new)
        assert len(api.requests) == ledger.summary()["attempts"] == 2
    finally:
        await client.close()


@pytest.mark.parametrize(
    "target",
    [
        "Casey: Which fictional team was it?",
        "Casey: What did you just say?",
        "Casey: Repeat that joke verbatim.",
        "Casey: Give me a different factual answer.",
        "Casey: Don't give me another joke.",
        "Casey: Quote a different joke you told earlier.",
    ],
)
async def test_short_continuity_and_literal_requests_do_not_pay_for_novelty(target, monkeypatch):
    old = "Dam good draft."
    api = SequenceAPI(old)
    r, ledger = responder(api, monkeypatch)
    assert (
        await r.reply(history(old), mode=ReplyMode.DIRECT, safety_id="test", target=target) == old
    )
    assert len(api.requests) == ledger.summary()["attempts"] == 1


@pytest.mark.parametrize("current", [False, True])
async def test_short_novelty_keeps_the_existing_source_check(current, monkeypatch):
    old, new = "Dam good draft.", "He chewed through his draft board."
    api = SequenceAPI(old, new)
    r, ledger = responder(api, monkeypatch)
    check = AsyncMock(return_value=current)
    messages = [*history(old), ConversationMessage("user", "Invented evidence.", origin="memory")]
    assert await r.reply(
        messages, mode=ReplyMode.DIRECT, safety_id="test", target=FOCUS, refresh_check=check
    ) == (new if current else old)
    check.assert_awaited_once_with()
    assert len(api.requests) == ledger.summary()["attempts"] == (2 if current else 1)


@pytest.mark.parametrize("origin", ["memory", "reference", "focus"])
def test_short_novelty_never_treats_other_origins_as_old_bot_words(origin):
    old = "Dam good draft."
    assert not _stale_bot_echo(old, [ConversationMessage("assistant", old, origin=origin)], FOCUS)


async def test_short_failed_repair_and_shared_brevity_repair_never_loop(monkeypatch):
    old = "Dam. Good. Draft."
    api = SequenceAPI(old, old)
    r, ledger = responder(api, monkeypatch)
    assert await r.reply(history(old), mode=ReplyMode.DIRECT, safety_id="test", target=FOCUS) == old
    assert len(api.requests) == ledger.summary()["attempts"] == 2
    assert "copied wording" in api.requests[1]["instructions"]
    assert "conversational length" in api.requests[1]["instructions"]


async def test_short_novelty_repair_keeps_recipient_abstention(monkeypatch):
    api = SequenceAPI("Dam good draft.", "<NO_REPLY>")
    r, ledger = responder(api, monkeypatch)
    assert (
        await r.reply(
            history("Dam good draft."), mode=ReplyMode.FOLLOW_UP, safety_id="test", target=FOCUS
        )
        is None
    )
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_short_novelty_budget_failure_keeps_the_paid_draft(monkeypatch):
    from trubot.budget import BudgetExceeded

    old = "Dam good draft."
    api = SequenceAPI(old, BudgetExceeded("maintenance limit"))
    r, _ = responder(api, monkeypatch)
    assert await r.reply(history(old), mode=ReplyMode.DIRECT, safety_id="test", target=FOCUS) == old
    assert len(api.requests) == 2
