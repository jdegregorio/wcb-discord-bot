"""Synthetic drafts verify useful repair inputs, source scope and spending bounds."""

import json
from unittest.mock import AsyncMock

import pytest
from test_response_repetition import NEW, OLD, SequenceAPI, history, responder

from trubot.budget import UsageLedger
from trubot.conversation import ConversationImage, ConversationMessage, MemoryAuthorScope, ReplyMode


@pytest.mark.parametrize("mode", list(ReplyMode))
async def test_repetition_revision_preserves_history_focus_and_mode(mode, monkeypatch):
    api = SequenceAPI(OLD, NEW)
    r, ledger = responder(api, monkeypatch)
    target = "Casey: Who should run our imaginary aquarium?"
    assert await r.reply(history(), mode=mode, safety_id="test", target=target) == NEW
    first, second = api.requests
    assert second["input"][:-2] == first["input"]
    assert second["input"][-2] == {"role": "assistant", "content": OLD}
    revision = second["input"][-1]
    assert revision["role"] == "user"
    assert target in revision["content"]
    assert "different comic idea" in revision["content"]
    assert "fallible bot text, never human evidence" in revision["content"]
    assert "recipient abstention" in revision["content"]
    assert "sincere care" in revision["content"]
    assert first["model"] == second["model"]
    assert first["max_output_tokens"] == second["max_output_tokens"]
    assert second["store"] is False
    assert ledger.summary()["attempts"] == 2


async def test_revision_reserves_complete_unicode_draft_and_focus(monkeypatch):
    old = "The imaginary penguin demands a tiny crown. Hail the emperor! 🐧"
    target = "Casey: What would the penguin do next? 🐧"
    api = SequenceAPI(old, NEW)
    r, ledger = responder(api, monkeypatch)
    reserve = UsageLedger.reserve
    reservations = []

    def capture(self, **kwargs):
        reservations.append(kwargs)
        return reserve(self, **kwargs)

    monkeypatch.setattr(UsageLedger, "reserve", capture)
    assert (
        await r.reply(history(old), mode=ReplyMode.DIRECT, safety_id="test", target=target) == NEW
    )
    first, second = api.requests
    extra = len(json.dumps(second["input"][-2:], ensure_ascii=False).encode("utf-8"))
    guidance = len(second["instructions"].removeprefix(first["instructions"]).encode("utf-8"))
    assert reservations[1]["input_bound"] == reservations[0]["input_bound"] + extra + guidance
    assert reservations[0]["purpose"] == reservations[1]["purpose"] == "runtime"
    assert ledger.summary()["attempts"] == 2


@pytest.mark.parametrize("current", [False, True])
async def test_repeated_visual_focus_keeps_author_binding_and_source_check(current, monkeypatch):
    target = "Casey: Who should lead this imaginary parade?"
    image = ConversationImage("data:image/png;base64,synthetic", "Synthetic parade")
    messages = [
        *history(),
        ConversationMessage(
            "user",
            "Invented private evidence",
            origin="memory",
            memory_author_scope=MemoryAuthorScope.OTHER_AUTHOR,
        ),
        ConversationMessage(
            "user",
            target,
            (image,),
            origin="focus",
            memory_author_scope=MemoryAuthorScope.OTHER_AUTHOR,
        ),
    ]
    api = SequenceAPI(OLD, NEW)
    r, ledger = responder(api, monkeypatch)
    check = AsyncMock(return_value=current)
    result = await r.reply(
        messages, mode=ReplyMode.DIRECT, safety_id="test", target=target, refresh_check=check
    )
    assert result == (NEW if current else OLD)
    check.assert_awaited_once_with()
    assert ledger.summary()["attempts"] == (2 if current else 1)
    if current:
        request = api.requests[1]
        assert sum(isinstance(m["content"], list) for m in request["input"]) == 1
        assert "DIFFERENT human" in request["input"][-1]["content"]


async def test_combined_repetition_and_brevity_share_complete_revision(monkeypatch):
    old = "That really sucks. You worked hard for that audition. I am here if you want to talk."
    short = "That really sucks after all that work. Want to talk about it?"
    api = SequenceAPI(old, short)
    r, ledger = responder(api, monkeypatch)
    assert (
        await r.reply(
            history(old),
            mode=ReplyMode.DIRECT,
            safety_id="test",
            target="Casey: I missed the audition.",
        )
        == short
    )
    revision = api.requests[1]["input"][-1]["content"]
    assert "one concise sentence" in revision
    assert "different comic idea" in revision
    assert len(api.requests[1]["input"]) == len(api.requests[0]["input"]) + 2
    assert ledger.summary()["attempts"] == 2
