"""Incomplete synthetic provider turns must never become Discord prose."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from test_response_repetition import SequenceAPI, responder

from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import ResponderError
from trubot.photo_action import PhotoAction

PARTIAL = "The squirrel commissioner opened the draft by explaining that"
COMPLETE = "The squirrel commissioner drafted a tree and called it roster depth."
TARGET = "Casey: Tell a fictional 300-word story about a squirrel commissioner."


class CompletionAPI(SequenceAPI):
    def __init__(self, *outputs, states=None):
        super().__init__(*outputs)
        self.states = iter(states or [("incomplete", "max_output_tokens"), ("completed", None)])

    async def create(self, **request):
        result = await super().create(**request)
        result.status, reason = next(self.states)
        result.incomplete_details = SimpleNamespace(reason=reason) if reason else None
        return result

    async def close(self):
        pass


@pytest.mark.parametrize("mode", list(ReplyMode))
@pytest.mark.parametrize("draft", [PARTIAL, "", "<NO_REPLY>"])
async def test_truncated_turn_gets_one_complete_accounted_rewrite(mode, draft, monkeypatch):
    api = CompletionAPI(draft, COMPLETE)
    r, ledger = responder(api, monkeypatch)
    assert await r.reply([], mode=mode, target=TARGET, safety_id="test") == COMPLETE
    assert len(api.requests) == ledger.summary()["attempts"] == 2
    first, second = api.requests
    assert second["input"][: len(first["input"])] == first["input"]
    assert second["model"] == first["model"]
    assert second["reasoning"] == first["reasoning"]
    assert second["max_output_tokens"] == first["max_output_tokens"]
    assert second["store"] is False
    assert "output limit" in second["instructions"]
    assert "fallible bot text" in second["input"][-1]["content"]
    assert "tools" not in second and second["tool_choice"] == "none"
    assert not any(
        item.get("role") == "assistant" and item.get("content") == draft for item in second["input"]
    )


async def test_unused_photo_offer_does_not_prevent_text_recovery(monkeypatch):
    api = CompletionAPI(PARTIAL, COMPLETE)
    r, _ = responder(api, monkeypatch)
    retrieve = AsyncMock()
    photo = PhotoAction(retrieve)
    assert (
        await r.reply(
            [], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test", photo_action=photo
        )
        == COMPLETE
    )
    assert "tools" in api.requests[0] and "tools" not in api.requests[1]
    retrieve.assert_not_awaited()
    assert not photo.used


@pytest.mark.parametrize("current", [False, True, None])
async def test_rewrite_rechecks_private_sources_before_spending(current, monkeypatch):
    api = CompletionAPI(PARTIAL, COMPLETE)
    r, ledger = responder(api, monkeypatch)
    check = AsyncMock(return_value=current) if current is not None else None
    result = await r.reply(
        [ConversationMessage("user", "Synthetic support", origin="memory")],
        mode=ReplyMode.DIRECT,
        target=TARGET,
        safety_id="test",
        refresh_check=check,
    )
    assert result == (COMPLETE if current else None)
    assert len(api.requests) == ledger.summary()["attempts"] == (2 if current else 1)
    if check:
        check.assert_awaited_once_with()


@pytest.mark.parametrize(
    "status,reason",
    [("failed", None), ("cancelled", None), ("incomplete", "content_filter"), ("incomplete", None)],
)
async def test_other_noncompleted_states_do_not_publish_or_retry(status, reason, monkeypatch):
    api = CompletionAPI(PARTIAL, states=[(status, reason)])
    r, ledger = responder(api, monkeypatch)
    with pytest.raises(ResponderError):
        await r.reply([], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test")
    assert len(api.requests) == ledger.summary()["attempts"] == 1


@pytest.mark.parametrize("candidate", [PARTIAL, "", "<NO_REPLY>"])
async def test_second_truncation_fails_closed_without_a_third_call(candidate, monkeypatch):
    api = CompletionAPI(PARTIAL, candidate, states=[("incomplete", "max_output_tokens")] * 2)
    r, ledger = responder(api, monkeypatch)
    with pytest.raises(ResponderError):
        await r.reply([], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test")
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_completed_rewrite_can_decline_a_followup(monkeypatch):
    api = CompletionAPI(PARTIAL, "<NO_REPLY>")
    r, _ = responder(api, monkeypatch)
    assert (
        await r.reply(
            [], mode=ReplyMode.FOLLOW_UP, target="Tim: Casey, your lineup?", safety_id="test"
        )
        is None
    )
    assert len(api.requests) == 2


async def test_truncation_shares_repetition_and_brevity_repair(monkeypatch):
    draft = (
        "One. Two. Three. Four. This is a substantial fictional sentence with enough "
        "words for detecting an old copied passage."
    )
    api = CompletionAPI(draft, COMPLETE)
    r, ledger = responder(api, monkeypatch)
    messages = [
        ConversationMessage("assistant", draft),
        ConversationMessage("assistant", "Another turn."),
    ]
    assert (
        await r.reply(
            messages, mode=ReplyMode.DIRECT, target="Casey: Say something.", safety_id="test"
        )
        == COMPLETE
    )
    assert len(api.requests) == ledger.summary()["attempts"] == 2
    assert "output limit" in api.requests[1]["instructions"]
    assert "earlier bot reply" in api.requests[1]["instructions"]
    assert "one or two brief sentences" in api.requests[1]["instructions"]


@pytest.mark.parametrize("failure", ["network", "budget"])
async def test_recovery_failure_never_returns_truncated_draft(failure, monkeypatch):
    import httpx2 as httpx
    from openai import APIConnectionError

    from trubot.budget import BudgetExceeded, UsageLedger

    error = APIConnectionError(request=httpx.Request("POST", "https://api.openai.com/v1/responses"))
    api = CompletionAPI(PARTIAL, error)
    r, ledger = responder(api, monkeypatch)
    if failure == "budget":
        reserve = UsageLedger.reserve

        def exhausted(self, **kwargs):
            if self.summary()["attempts"]:
                raise BudgetExceeded("Synthetic exhausted allowance")
            return reserve(self, **kwargs)

        monkeypatch.setattr(UsageLedger, "reserve", exhausted)
    with pytest.raises(APIConnectionError if failure == "network" else BudgetExceeded):
        await r.reply([], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test")
    assert len(api.requests) == (2 if failure == "network" else 1)
    assert ledger.summary()["attempts"] == len(api.requests)


async def test_handler_sends_only_complete_rewrite(monkeypatch):
    from test_discord_client import fake_channel, fake_message, make_client

    api = CompletionAPI(PARTIAL, COMPLETE)
    r, ledger = responder(api, monkeypatch)
    client, _, _, _ = make_client()
    client._responder = r
    channel = fake_channel()
    message = fake_message(channel)
    message.content = message.clean_content = "🤖 " + TARGET
    try:
        await client.on_message(message)
        channel.send.assert_awaited_once_with(COMPLETE)
        assert len(api.requests) == ledger.summary()["attempts"] == 2
    finally:
        await client.close()


@pytest.mark.parametrize("photo_offered", [False, True])
async def test_complete_initial_turn_keeps_one_request(photo_offered, monkeypatch):
    api = CompletionAPI(COMPLETE, states=[("completed", None)])
    r, ledger = responder(api, monkeypatch)
    retrieve = AsyncMock()
    photo = PhotoAction(retrieve) if photo_offered else None
    assert (
        await r.reply(
            [], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test", photo_action=photo
        )
        == COMPLETE
    )
    assert len(api.requests) == ledger.summary()["attempts"] == 1
    retrieve.assert_not_awaited()


async def test_selected_public_skill_truncation_does_not_read_or_retry(monkeypatch):
    from trubot.context_tools import ContextTools, ToolProtocolError
    from trubot.up_conditions import UPConditionsSkill

    api = CompletionAPI(PARTIAL)
    r, ledger = responder(api, monkeypatch)
    r._context_tools = ContextTools((UPConditionsSkill(),))
    with pytest.raises(ToolProtocolError):
        await r.reply(
            [],
            mode=ReplyMode.DIRECT,
            target="Casey: Check current Marquette sky conditions now?",
            safety_id="test",
        )
    assert len(api.requests) == ledger.summary()["attempts"] == 1


async def test_incomplete_tool_call_never_executes_or_retries(monkeypatch):
    from trubot.context_tools import ToolProtocolError

    api = CompletionAPI(PARTIAL)
    create = api.create

    async def call(**request):
        response = await create(**request)
        response.output = [
            SimpleNamespace(
                type="function_call", name="show_source_photo", arguments='{"query":"unfinished'
            )
        ]
        return response

    monkeypatch.setattr(api, "create", call)
    retrieve = AsyncMock()
    r, ledger = responder(api, monkeypatch)
    with pytest.raises(ToolProtocolError):
        await r.reply(
            [],
            mode=ReplyMode.DIRECT,
            target=TARGET,
            safety_id="test",
            photo_action=PhotoAction(retrieve),
        )
    assert len(api.requests) == ledger.summary()["attempts"] == 1
    retrieve.assert_not_awaited()


async def test_rewrite_preserves_author_images_and_maintenance_purpose(monkeypatch):
    from trubot.conversation import ConversationImage, MemoryAuthorScope

    api = CompletionAPI(PARTIAL, COMPLETE)
    r, ledger = responder(api, monkeypatch)
    r._purpose = "maintenance"
    image = ConversationImage("data:image/png;base64,synthetic", "Synthetic image")
    messages = [
        ConversationMessage(
            "user",
            "Synthetic attributed support",
            origin="memory",
            memory_author_scope=MemoryAuthorScope.OTHER_AUTHOR,
        ),
        ConversationMessage("user", TARGET, (image,)),
    ]
    assert (
        await r.reply(
            messages,
            mode=ReplyMode.DIRECT,
            target=TARGET,
            safety_id="test",
            refresh_check=AsyncMock(return_value=True),
        )
        == COMPLETE
    )
    first, second = api.requests
    assert second["input"][:-1] == first["input"]
    assert sum(isinstance(x.get("content"), list) for x in second["input"]) == 1
    assert "DIFFERENT human" in second["input"][-1]["content"]
    assert ledger.summary()["runtime_usd"] == 0
    assert ledger.summary()["maintenance_usd"] > 0


async def test_repair_source_change_before_final_handler_send_discards(monkeypatch):
    from test_discord_client import fake_channel, make_client

    api = CompletionAPI(PARTIAL, COMPLETE)
    r, ledger = responder(api, monkeypatch)
    client, _, _, _ = make_client()
    client._responder = r
    channel = fake_channel()
    memory = "Synthetic current memory"
    client._memory_context = AsyncMock(side_effect=[memory, memory, ""])
    try:
        assert not await client._respond(
            channel, mode=ReplyMode.DIRECT, requester_user_id=1, target=TARGET
        )
        channel.send.assert_not_awaited()
        assert len(api.requests) == ledger.summary()["attempts"] == 2
    finally:
        await client.close()


async def test_used_photo_transaction_cannot_enter_completion_repair(monkeypatch):
    from trubot.context_tools import ToolProtocolError

    api = CompletionAPI(PARTIAL)
    r, ledger = responder(api, monkeypatch)
    photo = PhotoAction(AsyncMock())
    photo.used = True
    with pytest.raises(ToolProtocolError):
        await r.reply(
            [], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test", photo_action=photo
        )
    assert len(api.requests) == ledger.summary()["attempts"] == 1


async def test_completed_empty_rewrite_fails_closed(monkeypatch):
    api = CompletionAPI(PARTIAL, "")
    r, ledger = responder(api, monkeypatch)
    with pytest.raises(ResponderError):
        await r.reply([], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test")
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_rewrite_cannot_return_tool_calls_despite_text(monkeypatch):
    api = CompletionAPI(PARTIAL, COMPLETE)
    create = api.create

    async def call(**request):
        response = await create(**request)
        if len(api.requests) == 2:
            response.output = [SimpleNamespace(type="function_call")]
        return response

    monkeypatch.setattr(api, "create", call)
    r, ledger = responder(api, monkeypatch)
    with pytest.raises(ResponderError):
        await r.reply([], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test")
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_cancellation_during_rewrite_keeps_reservation_and_never_returns_text(monkeypatch):
    import asyncio

    api = CompletionAPI(PARTIAL, asyncio.CancelledError())
    r, ledger = responder(api, monkeypatch)
    with pytest.raises(asyncio.CancelledError):
        await r.reply([], mode=ReplyMode.DIRECT, target=TARGET, safety_id="test")
    assert len(api.requests) == ledger.summary()["attempts"] == 2
    assert ledger.summary()["unsettled_attempts"] == 1


@pytest.mark.parametrize(
    "target",
    [
        "Casey: Repeat this passage verbatim.",
        "Casey: Quote the full source.",
        "Casey: Give the exact original words.",
    ],
)
async def test_truncated_literal_artifact_is_not_rewritten(monkeypatch, target):
    api = CompletionAPI(PARTIAL)
    r, ledger = responder(api, monkeypatch)
    with pytest.raises(ResponderError):
        await r.reply([], mode=ReplyMode.DIRECT, target=target, safety_id="test")
    assert len(api.requests) == ledger.summary()["attempts"] == 1


async def test_unfocused_ambient_recovers_from_original_history(monkeypatch):
    api = CompletionAPI(PARTIAL, COMPLETE)
    r, ledger = responder(api, monkeypatch)
    messages = [ConversationMessage("user", TARGET)]
    assert await r.reply(messages, mode=ReplyMode.AMBIENT, safety_id="test") == COMPLETE
    assert api.requests[1]["input"][0] == api.requests[0]["input"][0]
    assert len(api.requests) == ledger.summary()["attempts"] == 2


async def test_handler_never_sends_partial_after_failed_completion(monkeypatch):
    from test_discord_client import fake_channel, fake_message, make_client

    api = CompletionAPI(PARTIAL, PARTIAL, states=[("incomplete", "max_output_tokens")] * 2)
    r, _ = responder(api, monkeypatch)
    client, _, _, _ = make_client()
    client._responder = r
    channel = fake_channel()
    try:
        await client.on_message(fake_message(channel))
        channel.send.assert_awaited_once_with("Something broke. Probably Tim's fault.")
        assert len(api.requests) == 2
    finally:
        await client.close()
