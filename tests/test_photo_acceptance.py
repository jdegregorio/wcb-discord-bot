"""A retrieved candidate is not permission to publish an unrelated attachment."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from test_context_tools import Provider, response
from test_context_tools import responder as real_responder
from test_discord_client import fake_channel, fake_message, make_client
from test_learning import NOW
from test_photo_action import photo_call
from test_recalled_photos import pixel

from trubot.context_tools import ToolProtocolError
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.photo_action import PhotoAction, PhotoEvidence, publication_format
from trubot.up_conditions import UPConditionsSkill
from trubot.vision import decode_image


@pytest.mark.parametrize("decision", [None, False, True])
async def test_handler_never_publishes_a_candidate_without_explicit_acceptance(decision):
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning = SimpleNamespace(verified=True)
    channel = fake_channel()
    focus = fake_message(channel)

    async def context(*args, visual_sink=None, retrieval_query=None, **kwargs):
        if retrieval_query is not None:
            visual_sink.append(decode_image(pixel("blue")))
            return "A different lake, not the requested place."
        return ""

    async def reply(messages, **kwargs):
        action = kwargs["photo_action"]
        assert await action.prepare(photo_call())
        if decision is not None:
            return action.decide(json.dumps({"attach": decision, "reply": "Photo response."}))
        return "I don't have that photo."

    responder.reply = reply
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "_memory_context", side_effect=context),
        patch.object(client, "_photo_request_current", AsyncMock(return_value=True)),
    ):
        assert await client._respond(
            channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=1,
            anchor=focus,
            target="Show that specific lake, or just say you don't have it.",
        )
    if decision is True:
        assert channel.send.call_args.args == ("Photo response.",)
        assert len(channel.send.call_args.kwargs["files"]) == 1
    else:
        channel.send.assert_awaited_once_with(
            "I don't have that photo." if decision is None else "Photo response."
        )
    client._learning = None
    await client.close()


@pytest.mark.parametrize("attach", [False, True])
async def test_provider_decision_controls_publication_with_two_accounted_turns(
    private_test_ledger, attach
):
    evidence = PhotoEvidence(
        "Synthetic source", (decode_image(pixel("blue")),), AsyncMock(return_value=True)
    )
    action = PhotoAction(AsyncMock(return_value=evidence))
    reply = "Here's the canoe." if attach else "I don't have that photo."
    provider = Provider(
        [response(calls=[photo_call()]), response(json.dumps({"attach": attach, "reply": reply}))]
    )
    model = real_responder(provider, private_test_ledger, UPConditionsSkill())
    answer = await model.reply(
        [ConversationMessage("user", "Show the canoe.")],
        mode=ReplyMode.DIRECT,
        safety_id="test",
        photo_action=action,
    )
    assert answer == reply
    assert action.publish is attach
    assert action.evidence is evidence
    assert len(provider.requests) == 2
    assert provider.requests[1]["text"]["format"] == publication_format()
    assert provider.requests[1]["tool_choice"] == "none"
    assert "tools" not in provider.requests[1]
    assert evidence.current.await_count == 2
    assert private_test_ledger.summary()["attempts"] == 2


@pytest.mark.parametrize(
    "text",
    [
        "not-json",
        "[]",
        "null",
        "{}",
        '{"attach":true}',
        '{"attach":"false","reply":"No."}',
        '{"attach":1,"reply":"Yes."}',
        '{"attach":false,"reply":1}',
        '{"attach":false,"reply":" "}',
        '{"attach":true,"reply":"<NO_REPLY>"}',
        '{"attach":true,"reply":"Yes.","extra":true}',
        json.dumps({"attach": True, "reply": "x" * 6001}),
    ],
)
async def test_invalid_photo_decision_fails_closed_without_third_turn(private_test_ledger, text):
    action = PhotoAction(
        AsyncMock(
            return_value=PhotoEvidence(
                "Synthetic source", (decode_image(pixel("blue")),), AsyncMock(return_value=True)
            )
        )
    )
    provider = Provider([response(calls=[photo_call()]), response(text)])
    model = real_responder(provider, private_test_ledger, UPConditionsSkill())
    with pytest.raises(ToolProtocolError, match="Invalid photo publication decision"):
        await model.reply(
            [ConversationMessage("user", "Show it.")],
            mode=ReplyMode.DIRECT,
            safety_id="test",
            photo_action=action,
        )
    assert not action.publish and len(provider.requests) == 2


@pytest.mark.parametrize("status", ["incomplete", "failed", "cancelled"])
async def test_incomplete_publication_never_approves_candidate(private_test_ledger, status):
    action = PhotoAction(
        AsyncMock(
            return_value=PhotoEvidence(
                "Synthetic source", (decode_image(pixel("blue")),), AsyncMock(return_value=True)
            )
        )
    )
    provider = Provider(
        [response(calls=[photo_call()]), response('{"attach":true,"reply":"Here."}', status=status)]
    )
    model = real_responder(provider, private_test_ledger, UPConditionsSkill())
    with pytest.raises(ToolProtocolError):
        await model.reply(
            [ConversationMessage("user", "Show it.")],
            mode=ReplyMode.DIRECT,
            safety_id="test",
            photo_action=action,
        )
    assert not action.publish and len(provider.requests) == 2


async def test_decision_cannot_be_replayed_or_used_for_inspection():
    evidence = PhotoEvidence(
        "Synthetic source", (decode_image(pixel("blue")),), AsyncMock(return_value=True)
    )
    action = PhotoAction(AsyncMock(return_value=evidence))
    with pytest.raises(ToolProtocolError):
        action.decide('{"attach":true,"reply":"Here."}')
    await action.prepare(photo_call())
    assert action.decide('{"attach":false,"reply":"No matching photo."}')
    with pytest.raises(ToolProtocolError):
        action.decide('{"attach":true,"reply":"Here."}')
    assert not action.publish
    from test_context_tools import call

    from trubot.photo_action import INSPECT_NAME

    inspected = PhotoAction(AsyncMock(), AsyncMock(return_value=evidence))
    await inspected.prepare(call(name=INSPECT_NAME, arguments="{}"))
    with pytest.raises(ToolProtocolError):
        inspected.decide('{"attach":true,"reply":"Here."}')
    assert not inspected.publish


async def test_rejected_photo_can_preserve_followup_recipient_abstention(private_test_ledger):
    action = PhotoAction(
        AsyncMock(
            return_value=PhotoEvidence(
                "Synthetic source", (decode_image(pixel("blue")),), AsyncMock(return_value=True)
            )
        )
    )
    provider = Provider(
        [response(calls=[photo_call()]), response('{"attach":false,"reply":"<NO_REPLY>"}')]
    )
    model = real_responder(provider, private_test_ledger, UPConditionsSkill())
    assert (
        await model.reply(
            [ConversationMessage("user", "Peer, can I see it?")],
            mode=ReplyMode.FOLLOW_UP,
            safety_id="test",
            photo_action=action,
        )
        is None
    )
    assert not action.publish
