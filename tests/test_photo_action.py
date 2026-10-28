"""The model chooses photo intent; the harness enforces evidence and publication."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from test_context_tools import Provider, call, responder, response
from test_discord_client import fake_channel, fake_message, make_client
from test_learning import NOW
from test_recalled_photos import pixel

from trubot.context_tools import ToolProtocolError
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.photo_action import NAME, PhotoAction, PhotoEvidence
from trubot.up_conditions import UPConditionsSkill
from trubot.vision import decode_image


def photo_call(**kwargs):
    return call(name=NAME, arguments=json.dumps({"query": "trail camera at camp"}), **kwargs)


@pytest.mark.parametrize(
    "phrase",
    ["Can I see?!", "You've got to show me that.", "I'd love a look at what the camera caught."],
)
async def test_model_action_includes_real_pixels_in_continuation_without_phrase_gate(
    private_test_ledger, phrase
):
    image = decode_image(pixel("green"))
    evidence = PhotoEvidence(
        "Verified source photo context", (image,), AsyncMock(return_value=True)
    )
    retrieve = AsyncMock(return_value=evidence)
    action = PhotoAction(retrieve)
    provider = Provider(
        [
            response(calls=[photo_call()]),
            response(json.dumps({"attach": True, "reply": "Here you go."})),
        ]
    )
    model = responder(provider, private_test_ledger, UPConditionsSkill())
    text = await model.reply(
        [ConversationMessage("user", "Older source", (image,), origin="memory")],
        mode=ReplyMode.FOLLOW_UP,
        safety_id="test",
        target=phrase,
        photo_action=action,
    )
    assert text == "Here you go." and action.evidence is evidence
    retrieve.assert_awaited_once_with("trail camera at camp")
    assert any(t["name"] == NAME for t in provider.requests[0]["tools"])
    final = provider.requests[1]
    assert final["tool_choice"] == "none"
    images = [
        p
        for item in final["input"]
        if isinstance(item, dict)
        for p in item.get("content", [])
        if isinstance(p, dict) and p.get("type") == "input_image"
    ]
    assert len(images) == 1 and images[0]["image_url"] == image.data_url
    assert evidence.current.await_count == 2
    assert private_test_ledger.summary()["attempts"] == 2


async def test_no_model_action_means_no_photo_or_source_reads(private_test_ledger):
    retrieve = AsyncMock()
    action = PhotoAction(retrieve)
    provider = Provider([response("Hope things get better.")])
    model = responder(provider, private_test_ledger, UPConditionsSkill())
    assert await model.reply(
        [ConversationMessage("user", "A hard day.")],
        mode=ReplyMode.DIRECT,
        safety_id="test",
        photo_action=action,
    )
    retrieve.assert_not_awaited()
    assert action.evidence is None and not action.used


@pytest.mark.parametrize(
    "args", ["{}", '{"query":2}', '{"query":"","url":"https://bad.test"}', "[]"]
)
async def test_invalid_photo_tool_call_never_reads_sources(args):
    read = AsyncMock()
    action = PhotoAction(read)
    malformed = call(name=NAME, arguments=args)
    with pytest.raises(ToolProtocolError):
        await action.prepare(malformed)
    read.assert_not_awaited()


async def test_no_source_is_explicit_and_does_not_queue_an_attachment(private_test_ledger):
    action = PhotoAction(AsyncMock(return_value=None))
    provider = Provider([response(calls=[photo_call()]), response("I can't find that one.")])
    model = responder(provider, private_test_ledger, UPConditionsSkill())
    await model.reply(
        [ConversationMessage("user", "A picture?")],
        mode=ReplyMode.DIRECT,
        safety_id="test",
        photo_action=action,
    )
    assert action.evidence is None
    assert '"photo_queued":false' in json.dumps(provider.requests[1]["input"]).replace('\\"', '"')


async def test_source_change_prevents_caption_continuation(private_test_ledger):
    image = decode_image(pixel("green"))
    evidence = PhotoEvidence("source", (image,), AsyncMock(side_effect=[True, False]))
    action = PhotoAction(AsyncMock(return_value=evidence))
    provider = Provider([response(calls=[photo_call()])])
    model = responder(provider, private_test_ledger, UPConditionsSkill())
    with pytest.raises(ToolProtocolError):
        await model.reply(
            [ConversationMessage("user", "Show it")],
            mode=ReplyMode.DIRECT,
            safety_id="test",
            photo_action=action,
        )
    assert len(provider.requests) == 1


@pytest.mark.parametrize("changed", [False, True])
async def test_actual_handler_sends_photo_and_rechecks_before_send(changed):
    client, fake, _, _ = make_client(clock=lambda: NOW)
    client._learning = SimpleNamespace(verified=True)
    channel = fake_channel()
    focus = fake_message(channel)
    image = decode_image(pixel("green"))
    reads = 0

    async def context(*args, visual_sink=None, retrieval_query=None, **kwargs):
        nonlocal reads
        if retrieval_query is not None:
            reads += 1
            visual_sink.append(image)
            return "changed" if changed and reads > 2 else "verified source"
        return ""

    async def reply(messages, **kwargs):
        action = kwargs["photo_action"]
        assert await action.prepare(photo_call())
        return action.decide(json.dumps({"attach": True, "reply": "Here you go."}))

    fake.reply = reply
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "_memory_context", side_effect=context),
        patch.object(client, "_photo_request_current", AsyncMock(return_value=True)),
    ):
        result = await client._respond(
            channel, mode=ReplyMode.DIRECT, requester_user_id=1, anchor=focus, target="Can I see?!"
        )
    assert result is not changed
    if changed:
        channel.send.assert_not_awaited()
    else:
        assert channel.send.call_args.args == ("Here you go.",)
        attachments = channel.send.call_args.kwargs["files"]
        assert len(attachments) == 1 and attachments[0].filename == "source-photo-1.jpg"
    client._learning = None
    await client.close()


@pytest.mark.parametrize(
    "change",
    [
        "none",
        "attach_denied",
        "view_denied",
        "edited",
        "wrong_author",
        "expired",
        "withdrawn",
        "wrong_guild",
    ],
)
async def test_photo_publication_uses_current_request_permissions_and_withdrawal(tmp_path, change):
    from datetime import timedelta

    from test_learning import AUDIT

    from trubot.ingestion import MessageIngestor
    from trubot.learning import LearningStore
    from trubot.requested_scenes import SceneRequest

    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    learner = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._learning = learner
    client._connection.user = SimpleNamespace(id=999)
    channel = fake_channel()
    channel.guild = SimpleNamespace(
        id=77, owner_id=1, fetch_member=AsyncMock(return_value=object())
    )
    channel.permissions_for.return_value = SimpleNamespace(
        view_channel=True, send_messages=True, attach_files=True, read_message_history=True
    )
    fresh = SimpleNamespace(
        author=SimpleNamespace(id=1, bot=False),
        webhook_id=None,
        content="Can I see?!",
        created_at=NOW - timedelta(seconds=2),
        edited_at=None,
    )
    request = SceneRequest(100, 1, fresh.content, fresh.created_at, fresh.edited_at)
    channel.fetch_message.return_value = fresh
    if change == "attach_denied":
        channel.permissions_for.return_value.attach_files = False
    if change == "view_denied":
        channel.permissions_for.return_value.view_channel = False
    if change == "edited":
        fresh.content = "Do not send it."
    if change == "wrong_author":
        fresh.author.id = 2
    if change == "expired":
        fresh.created_at = NOW - timedelta(minutes=6)
        request = SceneRequest(100, 1, fresh.content, fresh.created_at, None)
    if change == "withdrawn":
        store.forget(now=NOW)
    if change == "wrong_guild":
        channel.guild.id = 88
    with patch.object(client, "fetch_channel", AsyncMock(return_value=channel)):
        assert await client._photo_request_current(channel, request, 1) is (change == "none")
    client._learning = None
    await client.close()
