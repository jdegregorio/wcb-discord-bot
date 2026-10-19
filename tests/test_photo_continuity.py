"""Text inspection preserves exact shown sources without reattaching photos."""

import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import discord
import pytest
from test_context_tools import Provider, call, responder, response
from test_discord_client import fake_channel, fake_message, make_client
from test_learning import NOW
from test_photo_retrieval import permissions
from test_photos import captured, photo_bytes, ready
from test_photos import photos as photos_fixture

from trubot.context_tools import ToolProtocolError
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.learning import LearningUnavailable
from trubot.photo_action import INSPECT_NAME, NAME, PhotoAction, PhotoEvidence
from trubot.photos import MAX_SHOWN, SHOWN_RETENTION, PhotoMemory
from trubot.up_conditions import UPConditionsSkill
from trubot.vision import decode_image

photos = photos_fixture


def posted(channel, mid=900):
    return SimpleNamespace(
        id=mid,
        guild=channel.guild,
        channel=channel,
        content="A bot caption, not evidence.",
        edited_at=None,
        created_at=NOW,
        author=SimpleNamespace(id=999, bot=True),
        webhook_id=None,
        attachments=[SimpleNamespace(id=901, size=123, content_type="image/jpeg")],
    )


async def shown(photos):
    memory, source_channel, client, _ = photos
    permissions(source_channel, client)
    source, row = await captured(photos, text="The creek under the old stone bridge.")
    output = fake_channel(20)
    post = posted(output)
    output.fetch_message.return_value = post
    evidence = await memory.recall("stone bridge", recipient=43)
    assert evidence
    memory.store.remember_shown(evidence, post, 43, now=NOW)
    return source, row, output, post


async def test_restart_inspection_reads_exact_source_not_bot_caption_or_new_search(photos):
    memory, _, client, _ = photos
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())):
        source, _, output, _ = await shown(photos)
        restarted = PhotoMemory(memory.learning, memory.responder)
        restarted.client = client
        restarted.recall_candidates = lambda _: pytest.fail("Inspection must never search")
        evidence = await restarted.inspect_shown(output, 43, recipient=43)
        assert evidence and await evidence.current()
        assert source.content in evidence.text
        assert "A bot caption" not in evidence.text
        assert evidence.images == (decode_image(photo_bytes()),)
        assert restarted.store.shown(77, 20, 44, now=NOW) is None


@pytest.mark.parametrize(
    "change",
    [
        "edit",
        "delete",
        "withdraw",
        "pixels",
        "profile",
        "permission",
        "access",
        "sent_edit",
        "sent_delete",
        "sent_author",
        "sent_webhook",
        "sent_no_pixels",
        "expiry",
    ],
)
async def test_source_and_shown_message_changes_revoke_inspection(photos, change):
    memory, source_channel, _, _ = photos
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())) as download:
        source, row, output, post = await shown(photos)
        evidence = await memory.inspect_shown(output, 43, recipient=43)
        assert evidence
        if change == "edit":
            source.content = "Corrected caption"
        elif change == "delete":
            memory.store.drop(10, [source.id], deleted=True, now=NOW)
            assert memory.store.shown(77, 20, 43, now=NOW) is None
        elif change == "withdraw":
            memory.learning.store.forget(now=NOW)
        elif change == "pixels":
            download.return_value = b"changed"
        elif change == "profile":
            ready(memory, row)
        elif change == "permission":
            source_channel.permissions_for.return_value.read_message_history = False
        elif change == "access":
            source_channel.fetch_message.side_effect = TimeoutError
        elif change == "sent_edit":
            post.content = "Corrected bot post"
        elif change == "sent_delete":
            output.fetch_message.side_effect = TimeoutError
        elif change == "sent_author":
            post.author.id = 42
        elif change == "sent_webhook":
            post.webhook_id = 5
        elif change == "sent_no_pixels":
            post.attachments = []
        else:
            memory.learning.clock = lambda: NOW + SHOWN_RETENTION
        assert not await evidence.current()
        assert await memory.inspect_shown(output, 43, recipient=43) is None


async def test_explicit_reply_and_latest_selection_do_not_cross_requester_channel_or_guild(photos):
    memory, _, _, _ = photos
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())):
        _, _, output, post = await shown(photos)
        evidence = await memory.recall("stone bridge")
        newer = posted(output, 1000)
        memory.store.remember_shown(evidence, newer, 43, now=NOW + timedelta(seconds=1))
        now = NOW + timedelta(seconds=2)
        assert memory.store.shown(77, 20, 43, now=now)["sent"] == 1000
        assert memory.store.shown(77, 20, 43, now=now, sent=900)["sent"] == post.id
        assert memory.store.shown(77, 20, 43, now=now, sent=123) is None
        assert memory.store.shown(77, 20, 44, now=now, sent=900) is None
        assert memory.store.shown(77, 21, 43, now=now, sent=900) is None
        assert memory.store.shown(78, 20, 43, now=now, sent=900) is None
        assert memory.store.shown(77, 20, 43, now=NOW - timedelta(seconds=1)) is None


async def test_bounded_links_expire_and_withdraw_with_private_archive(photos):
    memory, _, _, _ = photos
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())):
        _, _, output, _ = await shown(photos)
        evidence = await memory.recall("stone bridge")
        for i in range(MAX_SHOWN + 2):
            memory.store.remember_shown(evidence, posted(output, 1000 + i), 43, now=NOW)
        with memory.store.archives._transaction() as db:
            assert db.execute("SELECT COUNT(*) FROM shown_photos").fetchone()[0] == MAX_SHOWN
        assert memory.store.shown(77, 20, 43, now=NOW, sent=900) is None
        assert memory.store.shown(77, 20, 43, now=NOW + SHOWN_RETENTION) is None
        with memory.store.archives._transaction() as db:
            assert db.execute("SELECT COUNT(*) FROM shown_photos").fetchone()[0] == 0
        memory.learning.store.forget(now=NOW)
        assert not memory.store.archives.path.exists()
        with pytest.raises(LearningUnavailable):
            memory.store.shown(77, 20, 43, now=NOW)


async def test_provider_inspection_has_pixels_one_continuation_and_no_attachment(
    private_test_ledger,
):
    image = decode_image(photo_bytes())
    evidence = PhotoEvidence("Exact original human source", (image,), AsyncMock(return_value=True))
    inspect = AsyncMock(return_value=evidence)
    read = AsyncMock()
    action = PhotoAction(read, inspect)
    provider = Provider(
        [
            response(calls=[call(name=INSPECT_NAME, arguments="{}")]),
            response("I said the creek was under the old bridge."),
        ]
    )
    model = responder(provider, private_test_ledger, UPConditionsSkill())
    answer = await model.reply(
        [ConversationMessage("user", "That photo.")],
        mode=ReplyMode.DIRECT,
        safety_id="test",
        target="What did you say? Text only.",
        photo_action=action,
    )
    assert answer and action.inspected and action.evidence is evidence
    inspect.assert_awaited_once_with()
    read.assert_not_awaited()
    output = next(
        i for i in provider.requests[1]["input"] if i.get("type") == "function_call_output"
    )
    assert json.loads(output["output"])["photo_queued"] is False
    assert provider.requests[1]["tool_choice"] == "none"
    assert len(provider.requests) == 2 and evidence.current.await_count == 2
    with pytest.raises(ToolProtocolError):
        await action.prepare(call(name=NAME, arguments='{"query":"bridge"}'))


@pytest.mark.parametrize("args", ['{"query":"bridge"}', "[]", "null", "not-json"])
async def test_inspection_only_accepts_strict_empty_arguments(args):
    inspect = AsyncMock()
    action = PhotoAction(AsyncMock(), inspect)
    with pytest.raises(ToolProtocolError):
        await action.prepare(call(name=INSPECT_NAME, arguments=args))
    inspect.assert_not_awaited()


@pytest.mark.parametrize("changed", [False, True])
async def test_handler_inspection_sends_only_text_and_discards_changed_source(changed):
    client, model, _, _ = make_client(clock=lambda: NOW)
    client._learning = SimpleNamespace(
        verified=True, identity=SimpleNamespace(user_id=42, guild_id=77)
    )
    channel = fake_channel()
    focus = fake_message(channel)
    evidence = PhotoEvidence(
        "Original human caption",
        (decode_image(photo_bytes()),),
        AsyncMock(side_effect=[True, not changed]),
    )
    client._photos = SimpleNamespace(
        inspect_shown=AsyncMock(return_value=evidence),
        store=SimpleNamespace(shown=Mock(return_value={"sent": 900})),
    )

    async def reply(messages, **kwargs):
        action = kwargs["photo_action"]
        await action.prepare(call(name=INSPECT_NAME, arguments="{}"))
        return "I said the creek was under the bridge."

    model.reply = reply
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "_memory_context", AsyncMock(return_value="")),
        patch.object(client, "_photo_request_current", AsyncMock(return_value=True)),
    ):
        result = await client._respond(
            channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=1,
            anchor=focus,
            target="What did you say about it? Text only.",
        )
    assert result is not changed
    if changed:
        channel.send.assert_not_awaited()
    else:
        assert channel.send.call_args.kwargs == {}
    client._learning = None
    await client.close()


@pytest.mark.parametrize("kind", ["explicit", "cross_channel", "own_history", "request_changed"])
async def test_handler_binds_reference_and_rejects_ineligible_inspection(kind):
    client, model, _, _ = make_client(clock=lambda: NOW)
    client._learning = SimpleNamespace(
        verified=True, identity=SimpleNamespace(user_id=42, guild_id=77)
    )
    client._photos = SimpleNamespace(
        inspect_shown=AsyncMock(return_value=None),
        store=SimpleNamespace(shown=Mock(return_value={"sent": 900})),
    )
    channel = fake_channel()
    focus = fake_message(channel)
    focus.reference = discord.MessageReference(
        message_id=900, channel_id=99 if kind == "cross_channel" else channel.id
    )

    async def reply(messages, **kwargs):
        action = kwargs["photo_action"]
        if kind in {"cross_channel", "own_history"}:
            assert action.inspect is None
        else:
            await action.prepare(call(name=INSPECT_NAME, arguments="{}"))
        return "Unavailable."

    model.reply = reply
    target = (
        "What did I say about that?" if kind == "own_history" else "What did you say about that?"
    )
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "_reference_context", AsyncMock(return_value=None)),
        patch.object(client, "_memory_context", AsyncMock(return_value="")),
        patch.object(
            client, "_photo_request_current", AsyncMock(return_value=kind != "request_changed")
        ),
    ):
        await client._respond(
            channel, mode=ReplyMode.DIRECT, requester_user_id=1, anchor=focus, target=target
        )
    if kind == "explicit":
        client._photos.inspect_shown.assert_awaited_once_with(channel, 1, sent=900, recipient=1)
    else:
        client._photos.inspect_shown.assert_not_awaited()
    client._learning = None
    await client.close()


@pytest.mark.parametrize("binding", ["available", "missing", "unavailable"])
async def test_source_inspection_capability_requires_an_existing_scoped_link(binding):
    client, model, _, _ = make_client(clock=lambda: NOW)
    client._learning = SimpleNamespace(verified=True)
    lookup = Mock(return_value={"sent": 900} if binding == "available" else None)
    if binding == "unavailable":
        lookup.side_effect = LearningUnavailable("Unavailable")
    client._photos = SimpleNamespace(store=SimpleNamespace(shown=lookup))
    channel = fake_channel()
    focus = fake_message(channel)

    async def reply(messages, **kwargs):
        action = kwargs["photo_action"]
        assert (action.inspect is not None) is (binding == "available")
        return "A reply."

    model.reply = reply
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "_memory_context", AsyncMock(return_value="")),
    ):
        assert await client._respond(
            channel, mode=ReplyMode.DIRECT, requester_user_id=1, anchor=focus, target="A question."
        )
    lookup.assert_called_once_with(77, 10, 1, now=NOW, sent=None)
    client._learning = None
    await client.close()


@pytest.mark.parametrize("available", [False, True])
async def test_only_existing_inspection_capability_announces_source_availability(
    private_test_ledger, available
):
    from trubot.photo_action import INSPECT_INSTRUCTIONS

    provider = Provider([response("A direct answer.")])
    model = responder(provider, private_test_ledger, UPConditionsSkill())
    action = PhotoAction(AsyncMock(), AsyncMock() if available else None)
    await model.reply(
        [ConversationMessage("user", "A question.")],
        mode=ReplyMode.DIRECT,
        safety_id="test",
        photo_action=action,
    )
    assert (INSPECT_INSTRUCTIONS in provider.requests[0]["instructions"]) is available


@pytest.mark.parametrize("available", [False, True])
@pytest.mark.parametrize("visual_focus", [False, True])
@pytest.mark.parametrize("scope", ["source_author", "other_author", "unknown_author"])
async def test_current_focus_preserves_authorship_and_discovers_scoped_source(
    private_test_ledger, available, visual_focus, scope
):
    from trubot.conversation import ConversationImage, MemoryAuthorScope
    from trubot.memory_author import author_guidance
    from trubot.photo_action import INSPECT_INSTRUCTIONS

    binding = MemoryAuthorScope(scope)
    target = "Friend: What was the original caption? Text only."
    image = ConversationImage("data:image/png;base64,AAAA", "Synthetic focus image")
    messages = [
        ConversationMessage("user", "Friend: Show that bridge photo."),
        ConversationMessage("assistant", "I cannot find its caption."),
        ConversationMessage(
            "user",
            "A text search has no exact quotation.",
            origin="memory",
            memory_author_scope=binding,
        ),
    ]
    if visual_focus:
        messages.append(ConversationMessage("user", target, (image,), origin="focus"))
    provider = Provider([response("A direct answer.")])
    model = responder(provider, private_test_ledger, UPConditionsSkill())
    await model.reply(
        messages,
        mode=ReplyMode.DIRECT,
        safety_id="synthetic",
        target=target,
        photo_action=PhotoAction(AsyncMock(), AsyncMock() if available else None),
    )
    request = provider.requests[0]
    focus = request["input"][-1]["content"]
    text = focus[0]["text"] if isinstance(focus, list) else focus
    assert target in text
    assert author_guidance(binding) in text
    assert (INSPECT_INSTRUCTIONS in text) is available
    if available:
        assert text.index(INSPECT_INSTRUCTIONS) > text.index(author_guidance(binding))
    assert request["input"][1]["content"] == messages[1].content
    assert request["input"][2]["content"] == messages[2].content
    assert request["store"] is False
    if visual_focus:
        assert focus[-1]["image_url"] == image.data_url
    assert len(provider.requests) == 1
