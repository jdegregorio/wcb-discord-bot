"""Invented conversational drafts exercise bounded adapter repair and its safeguards."""

from unittest.mock import AsyncMock

import pytest
from test_response_repetition import SequenceAPI, responder

from trubot.conversation import ConversationMessage, ReplyMode

LONG = "That really sucks. You worked hard for that audition. I am here if you want to talk."
SHORT = "That really sucks after all that work. Want to talk about it?"
TARGET = "Casey: A fictional friend missed the audition they worked toward. What would you say?"


@pytest.mark.parametrize("mode", [ReplyMode.DIRECT, ReplyMode.REACTION, ReplyMode.FOLLOW_UP])
async def test_three_part_care_gets_one_accounted_brief_attempt(mode, monkeypatch):
    api = SequenceAPI(LONG, SHORT)
    r, ledger = responder(api, monkeypatch)
    assert (
        await r.reply(
            [ConversationMessage("user", TARGET)], mode=mode, safety_id="test", target=TARGET
        )
        == SHORT
    )
    assert len(api.requests) == ledger.summary()["attempts"] == 2
    assert api.requests[0]["input"] == api.requests[1]["input"]
    assert api.requests[1]["store"] is False
    assert api.requests[0]["max_output_tokens"] == api.requests[1]["max_output_tokens"]


@pytest.mark.parametrize("current", [False, True])
async def test_brief_attempt_rechecks_private_memory_before_spending(current, monkeypatch):
    api = SequenceAPI(LONG, SHORT)
    r, ledger = responder(api, monkeypatch)
    check = AsyncMock(return_value=current)
    assert await r.reply(
        [ConversationMessage("user", "Invented support", origin="memory")],
        mode=ReplyMode.DIRECT,
        safety_id="test",
        target=TARGET,
        refresh_check=check,
    ) == (SHORT if current else LONG)
    check.assert_awaited_once_with()
    assert len(api.requests) == ledger.summary()["attempts"] == (2 if current else 1)


async def test_unchecked_memory_is_not_resent_to_shorten_reply(monkeypatch):
    api = SequenceAPI(LONG)
    r, ledger = responder(api, monkeypatch)
    assert (
        await r.reply(
            [ConversationMessage("user", "Invented support", origin="memory")],
            mode=ReplyMode.DIRECT,
            safety_id="test",
            target=TARGET,
        )
        == LONG
    )
    assert len(api.requests) == ledger.summary()["attempts"] == 1


async def test_quality_attempt_is_shared_with_repetition(monkeypatch):
    api = SequenceAPI(LONG, LONG)
    r, ledger = responder(api, monkeypatch)
    messages = [ConversationMessage("assistant", LONG), ConversationMessage("assistant", "Nice")]
    assert await r.reply(messages, mode=ReplyMode.DIRECT, safety_id="test", target=TARGET) == LONG
    assert len(api.requests) == ledger.summary()["attempts"] == 2
    assert "one or two brief sentences" in api.requests[1]["instructions"]
    assert "earlier bot reply" in api.requests[1]["instructions"]


@pytest.mark.parametrize(
    "target",
    [
        "Casey: Repeat your answer verbatim.",
        "Casey: Quote the full passage.",
        "Casey: Explain why this happened in detail.",
        "Casey: Give three examples.",
        "Casey: Show the evidence for that claim.",
        "Casey: List the steps.",
        "Casey: Tell an invented bedtime story.",
        "Casey: Write a poem about draft night.",
    ],
)
async def test_explicit_content_requests_preserve_complete_reply(target, monkeypatch):
    api = SequenceAPI(LONG)
    r, _ = responder(api, monkeypatch)
    assert await r.reply([], mode=ReplyMode.DIRECT, safety_id="test", target=target) == LONG
    assert len(api.requests) == 1


@pytest.mark.parametrize(
    "output",
    [
        SHORT,
        "The vet is Dr. Lee. That was a hard goodbye.",
        'He said "Sox Baseball!!!" and "White Sox!!!". Glad he enjoyed it.',
        "He scored 3.5 points. Rough night.",
        "Wait... seriously? Nice.",
    ],
)
async def test_short_replies_and_internal_punctuation_do_not_add_requests(output, monkeypatch):
    api = SequenceAPI(output)
    r, _ = responder(api, monkeypatch)
    assert await r.reply([], mode=ReplyMode.DIRECT, safety_id="test", target=TARGET) == output
    assert len(api.requests) == 1


async def test_reference_and_unfocused_ambient_keep_deliberate_runway(monkeypatch):
    for messages, target in [
        ([ConversationMessage("user", LONG, origin="reference")], TARGET),
        ([ConversationMessage("user", TARGET)], None),
    ]:
        api = SequenceAPI(LONG)
        r, _ = responder(api, monkeypatch)
        assert (
            await r.reply(messages, mode=ReplyMode.AMBIENT, safety_id="test", target=target) == LONG
        )
        assert len(api.requests) == 1


@pytest.mark.parametrize("candidate", ["", LONG, "No. " + LONG])
async def test_failed_compression_preserves_original_without_third_attempt(candidate, monkeypatch):
    api = SequenceAPI(LONG, candidate)
    r, ledger = responder(api, monkeypatch)
    assert await r.reply([], mode=ReplyMode.DIRECT, safety_id="test", target=TARGET) == LONG
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_unpunctuated_overlong_answer_gets_a_complete_rewrite(monkeypatch):
    long = " ".join(["An invented answer"] * 25)
    api = SequenceAPI(long, SHORT)
    r, ledger = responder(api, monkeypatch)
    assert await r.reply([], mode=ReplyMode.DIRECT, safety_id="test", target=TARGET) == SHORT
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_brevity_failure_retains_accounted_answer_without_retry(monkeypatch):
    import httpx2 as httpx
    from openai import APIConnectionError

    api = SequenceAPI(
        LONG, APIConnectionError(request=httpx.Request("POST", "https://example.test"))
    )
    r, ledger = responder(api, monkeypatch)
    r._max_retries = 4
    assert await r.reply([], mode=ReplyMode.DIRECT, safety_id="test", target=TARGET) == LONG
    assert len(api.requests) == 2
    assert ledger.summary()["unsettled_attempts"] == 1


async def test_cancelled_brevity_attempt_preserves_uncertain_reservation(monkeypatch):
    import asyncio

    api = SequenceAPI(LONG, asyncio.CancelledError())
    r, ledger = responder(api, monkeypatch)
    with pytest.raises(asyncio.CancelledError):
        await r.reply([], mode=ReplyMode.DIRECT, safety_id="test", target=TARGET)
    assert len(api.requests) == 2
    assert ledger.summary()["unsettled_attempts"] == 1


async def test_brief_followup_can_correct_recipient_and_abstain(monkeypatch):
    api = SequenceAPI(LONG, "<NO_REPLY>")
    r, ledger = responder(api, monkeypatch)
    assert await r.reply([], mode=ReplyMode.FOLLOW_UP, safety_id="test", target=TARGET) is None
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_incomplete_shorter_answer_keeps_original(monkeypatch):
    api = SequenceAPI(LONG, SHORT)
    create = api.create

    async def incomplete(**kwargs):
        response = await create(**kwargs)
        if len(api.requests) == 2:
            response.status = "incomplete"
        return response

    monkeypatch.setattr(api, "create", incomplete)
    r, ledger = responder(api, monkeypatch)
    assert await r.reply([], mode=ReplyMode.DIRECT, safety_id="test", target=TARGET) == LONG
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_exhausted_budget_keeps_draft_before_optional_network(monkeypatch):
    from trubot.budget import BudgetExceeded, UsageLedger

    api = SequenceAPI(LONG)
    r, ledger = responder(api, monkeypatch)
    reserve = UsageLedger.reserve
    calls = []

    def exhausted(self, **kwargs):
        calls.append(kwargs)
        if len(calls) == 2:
            raise BudgetExceeded("limit")
        return reserve(self, **kwargs)

    monkeypatch.setattr(UsageLedger, "reserve", exhausted)
    assert await r.reply([], mode=ReplyMode.DIRECT, safety_id="test", target=TARGET) == LONG
    assert len(api.requests) == ledger.summary()["attempts"] == 1
    assert calls[1]["input_bound"] > calls[0]["input_bound"]
    assert calls[0]["purpose"] == calls[1]["purpose"] == "runtime"


async def test_brevity_attempt_uses_existing_maintenance_purpose(monkeypatch):
    api = SequenceAPI(LONG, SHORT)
    r, ledger = responder(api, monkeypatch)
    r._purpose = "maintenance"
    assert await r.reply([], mode=ReplyMode.DIRECT, safety_id="test", target=TARGET) == SHORT
    assert ledger.summary()["runtime_usd"] == 0
    assert ledger.summary()["maintenance_usd"] > 0
