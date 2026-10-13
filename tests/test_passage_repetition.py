"""Invented stale passages and deliberate continuity exercise the actual adapter."""

from dataclasses import replace

import pytest
from test_response_repetition import SequenceAPI, responder

from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import _stale_bot_echo

STOCK = "Rough weeks are rough, and I am here if you want to talk."
OLD = "I am sorry, man. " + STOCK
DRAFT = "That sounds exhausting. " + STOCK
FRESH = "That is a lot to carry. Want some company tonight?"
FOCUS = "Casey: A fictional friend has had an exhausting week."


def history():
    return [
        ConversationMessage("user", "Casey: A fictional friend is having a hard time."),
        ConversationMessage("assistant", OLD),
        ConversationMessage("user", "Casey: Invent a roster job for a pastry chef."),
        ConversationMessage("assistant", "He handles the turnovers."),
    ]


@pytest.mark.parametrize("mode", [ReplyMode.DIRECT, ReplyMode.REACTION, ReplyMode.FOLLOW_UP])
async def test_reused_passage_inside_changed_reply_gets_one_accounted_refresh(mode, monkeypatch):
    api = SequenceAPI(DRAFT, FRESH)
    r, ledger = responder(api, monkeypatch)
    before = ledger.summary()["attempts"]
    assert await r.reply(history(), mode=mode, safety_id="test", target=FOCUS) == FRESH
    assert len(api.requests) == 2
    assert ledger.summary()["attempts"] == before + 2
    assert api.requests[0]["input"] == api.requests[1]["input"]


def test_passage_normalizes_punctuation_case_and_apostrophes():
    old = "I\u2019m here to listen when you\u2019re ready, and there\u2019s no hurry to answer."
    draft = "Hey. I'M here to listen when YOU'RE ready; and there's no hurry to answer!"
    messages = [ConversationMessage("assistant", old), ConversationMessage("assistant", "Nice.")]
    assert _stale_bot_echo(draft, messages, FOCUS)


@pytest.mark.parametrize(
    "messages,target,draft",
    [
        (history(), "Casey: Repeat that earlier answer.", DRAFT),
        (history(), "Casey: Quote what you told them.", DRAFT),
        ([*history(), ConversationMessage("user", OLD, origin="reference")], FOCUS, DRAFT),
        ([*history(), ConversationMessage("assistant", "Take it easy. " + STOCK)], FOCUS, DRAFT),
        (history(), FOCUS, "I am here if you want to talk."),
        (history(), FOCUS, "It is a rough week, but I can listen whenever you need."),
        (history(), None, DRAFT),
        ([replace(m, role="user") for m in history()], FOCUS, DRAFT),
        ([replace(m, origin="memory") for m in history()], FOCUS, DRAFT),
    ],
    ids=[
        "repeat",
        "quote",
        "reference",
        "immediate",
        "short",
        "paraphrase",
        "ambient",
        "human",
        "memory",
    ],
)
def test_intentional_or_unrelated_passages_do_not_trigger(messages, target, draft):
    assert not _stale_bot_echo(draft, messages, target)


def test_partial_latest_reuse_does_not_hide_a_different_old_passage():
    messages = [*history(), ConversationMessage("assistant", "That sounds exhausting.")]
    assert _stale_bot_echo(DRAFT, messages, FOCUS)


@pytest.mark.parametrize("current", [False, True])
async def test_passage_refresh_revalidates_private_packet(current, monkeypatch):
    from unittest.mock import AsyncMock

    api = SequenceAPI(DRAFT, FRESH)
    r, ledger = responder(api, monkeypatch)
    check = AsyncMock(return_value=current)
    messages = [
        *history(),
        ConversationMessage("user", "Invented private support.", origin="memory"),
    ]
    assert await r.reply(
        messages, mode=ReplyMode.DIRECT, safety_id="test", target=FOCUS, refresh_check=check
    ) == (FRESH if current else DRAFT)
    check.assert_awaited_once_with()
    assert len(api.requests) == ledger.summary()["attempts"] == (2 if current else 1)


async def test_second_passage_echo_has_no_third_attempt(monkeypatch):
    api = SequenceAPI(DRAFT, DRAFT)
    r, _ = responder(api, monkeypatch)
    assert await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target=FOCUS) == DRAFT
    assert len(api.requests) == 2
