import asyncio
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import httpx2 as httpx
import pytest
from openai import APIConnectionError, AsyncOpenAI

from trubot.budget import BudgetExceeded, BudgetUnavailable, UsageLedger
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import OpenAITruaxResponder

OLD = "Oh, you mean TJ! I thought you meant God."
NEW = "Obviously TJ. God handles the paperwork."


class SequenceAPI:
    def __init__(self, *outputs: str):
        self.outputs = iter(outputs)
        self.requests: list[dict[str, Any]] = []
        self.responses = self

    def with_options(self, **_kwargs: object):
        return self

    async def create(self, **request: Any):
        self.requests.append(request)
        output = next(self.outputs)
        if isinstance(output, BaseException):
            raise output
        return SimpleNamespace(
            output_text=output,
            usage=SimpleNamespace(
                input_tokens=1000,
                input_tokens_details=SimpleNamespace(cached_tokens=0),
                output_tokens=20,
            ),
        )


def history(old: str = OLD):
    return [
        ConversationMessage("user", "Casey: Not TJ?"),
        ConversationMessage("assistant", old),
        ConversationMessage("user", "Casey: Who runs the universe?"),
        ConversationMessage("assistant", "Usually God. Unless the commissioner is very tall."),
    ]


def responder(api: SequenceAPI, monkeypatch: pytest.MonkeyPatch):
    import os

    ledger = UsageLedger(Path(os.environ["TRUBOT_USAGE_LEDGER_PATH"]))
    return OpenAITruaxResponder(
        cast(AsyncOpenAI, api), model="gpt-6-luna", max_output_tokens=512, budget=ledger
    ), ledger


@pytest.mark.parametrize("mode", [ReplyMode.DIRECT, ReplyMode.FOLLOW_UP, ReplyMode.REACTION])
async def test_old_echo_gets_one_accounted_fresh_attempt(mode, monkeypatch):
    api = SequenceAPI(OLD, NEW)
    r, ledger = responder(api, monkeypatch)
    before = ledger.summary()["attempts"]
    result = await r.reply(history(), mode=mode, safety_id="test", target="Casey: Not TJ?")
    assert result == NEW
    assert len(api.requests) == 2
    assert ledger.summary()["attempts"] == before + 2
    first, second = api.requests
    assert first["input"] == second["input"]
    assert second["store"] is False
    assert second["model"] == first["model"]
    assert "earlier bot reply" in second["instructions"]
    assert "care" in second["instructions"]


async def test_repeated_second_output_never_creates_a_third_call(monkeypatch):
    api = SequenceAPI(OLD, OLD)
    r, _ = responder(api, monkeypatch)
    assert (
        await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target="Casey: TJ?")
        == OLD
    )
    assert len(api.requests) == 2


@pytest.mark.parametrize(
    "target",
    [
        "Casey: Repeat that old reply verbatim.",
        "Casey: Quote your earlier answer.",
        "Casey: What exactly did you say earlier?",
    ],
)
async def test_requested_literal_reuse_needs_no_extra_call(target, monkeypatch):
    api = SequenceAPI(OLD)
    r, _ = responder(api, monkeypatch)
    assert await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target=target) == OLD
    assert len(api.requests) == 1


@pytest.mark.parametrize("output", ["Nice", "Usually God. Unless the commissioner is very tall."])
async def test_short_or_immediate_reuse_keeps_continuity(output, monkeypatch):
    api = SequenceAPI(output)
    r, _ = responder(api, monkeypatch)
    assert (
        await r.reply(
            history("Nice"), mode=ReplyMode.DIRECT, safety_id="test", target="Casey: Again?"
        )
        == output
    )
    assert len(api.requests) == 1


async def test_explicit_reference_preserves_verbatim_context(monkeypatch):
    api = SequenceAPI(OLD)
    r, _ = responder(api, monkeypatch)
    messages = [*history(), ConversationMessage("user", OLD, origin="reference")]
    assert (
        await r.reply(messages, mode=ReplyMode.DIRECT, safety_id="test", target="Casey: That one")
        == OLD
    )
    assert len(api.requests) == 1


async def test_abstention_is_never_retried(monkeypatch):
    api = SequenceAPI("<NO_REPLY>")
    r, _ = responder(api, monkeypatch)
    assert (
        await r.reply(
            history(), mode=ReplyMode.FOLLOW_UP, safety_id="test", target="Casey: Alex, reply"
        )
        is None
    )
    assert len(api.requests) == 1


@pytest.mark.parametrize("error", [BudgetExceeded("limit"), BudgetUnavailable("state")])
async def test_optional_reservation_failure_keeps_accounted_draft(error, monkeypatch):
    api = SequenceAPI(OLD)
    r, ledger = responder(api, monkeypatch)
    reserve = UsageLedger.reserve
    calls = []

    def limited(self, **kwargs):
        calls.append(kwargs)
        if len(calls) == 2:
            raise error
        return reserve(self, **kwargs)

    monkeypatch.setattr(UsageLedger, "reserve", limited)
    assert (
        await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target="Casey: TJ?")
        == OLD
    )
    assert len(api.requests) == 1
    assert len(calls) == 2
    assert calls[0]["purpose"] == calls[1]["purpose"] == "runtime"
    assert calls[1]["input_bound"] > calls[0]["input_bound"]
    assert calls[1]["output_bound"] == calls[0]["output_bound"]
    assert ledger.summary()["attempts"] == 1


async def test_optional_provider_failure_is_accounted_without_transport_retry(monkeypatch):
    api = SequenceAPI(
        OLD, APIConnectionError(request=httpx.Request("POST", "https://example.test"))
    )
    r, ledger = responder(api, monkeypatch)
    r._max_retries = 4
    assert (
        await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target="Casey: TJ?")
        == OLD
    )
    assert len(api.requests) == 2
    assert ledger.summary()["unsettled_attempts"] == 1


async def test_optional_cancel_propagates_and_keeps_reservation(monkeypatch):
    api = SequenceAPI(OLD, asyncio.CancelledError())
    r, ledger = responder(api, monkeypatch)
    with pytest.raises(asyncio.CancelledError):
        await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target="Casey: TJ?")
    assert len(api.requests) == 2
    assert ledger.summary()["unsettled_attempts"] == 1


async def test_optional_empty_output_preserves_draft(monkeypatch):
    api = SequenceAPI(OLD, "   ")
    r, ledger = responder(api, monkeypatch)
    assert (
        await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target="Casey: TJ?")
        == OLD
    )
    assert ledger.summary()["attempts"] == 2
    assert ledger.summary()["unsettled_attempts"] == 0


async def test_optional_incomplete_output_preserves_draft(monkeypatch):
    api = SequenceAPI(OLD, NEW)
    create = api.create

    async def incomplete(**kwargs):
        output = await create(**kwargs)
        if len(api.requests) == 2:
            output.status = "incomplete"
        return output

    monkeypatch.setattr(api, "create", incomplete)
    r, _ = responder(api, monkeypatch)
    assert (
        await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target="Casey: TJ?")
        == OLD
    )
    assert len(api.requests) == 2


async def test_fresh_followup_decline_remains_authoritative(monkeypatch):
    api = SequenceAPI(OLD, "<NO_REPLY>")
    r, ledger = responder(api, monkeypatch)
    assert (
        await r.reply(
            history(), mode=ReplyMode.FOLLOW_UP, safety_id="test", target="Casey: Alex, reply"
        )
        is None
    )
    assert ledger.summary()["attempts"] == 2


@pytest.mark.parametrize("mode", list(ReplyMode))
async def test_without_explicit_focus_does_not_refresh(mode, monkeypatch):
    api = SequenceAPI(OLD)
    r, _ = responder(api, monkeypatch)
    assert await r.reply(history(), mode=mode, safety_id="test") == OLD
    assert len(api.requests) == 1


@pytest.mark.parametrize("origin", ["memory", "reference", "focus"])
async def test_only_conversation_bot_turns_trigger_refresh(origin, monkeypatch):
    from dataclasses import replace

    messages = [replace(m, origin=origin) if m.role == "assistant" else m for m in history()]
    api = SequenceAPI(OLD)
    r, _ = responder(api, monkeypatch)
    assert (
        await r.reply(messages, mode=ReplyMode.DIRECT, safety_id="test", target="Casey: TJ?") == OLD
    )
    assert len(api.requests) == 1


async def test_human_quote_cannot_trigger_refresh(monkeypatch):
    from dataclasses import replace

    messages = [replace(m, role="user") if m.content == OLD else m for m in history()]
    api = SequenceAPI(OLD)
    r, _ = responder(api, monkeypatch)
    assert (
        await r.reply(messages, mode=ReplyMode.DIRECT, safety_id="test", target="Casey: TJ?") == OLD
    )
    assert len(api.requests) == 1


async def test_exact_echo_normalizes_case_prefix_and_spacing(monkeypatch):
    api = SequenceAPI("Trubot:  OH, you mean TJ!   I thought you meant God.", NEW)
    r, _ = responder(api, monkeypatch)
    assert (
        await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target="Casey: TJ?")
        == NEW
    )
    assert len(api.requests) == 2


async def test_maintenance_refresh_uses_existing_maintenance_purpose(monkeypatch):
    api = SequenceAPI(OLD, NEW)
    r, ledger = responder(api, monkeypatch)
    r._purpose = "maintenance"
    assert (
        await r.reply(history(), mode=ReplyMode.DIRECT, safety_id="test", target="Casey: TJ?")
        == NEW
    )
    assert ledger.summary()["runtime_usd"] == 0
    assert ledger.summary()["maintenance_usd"] > 0
