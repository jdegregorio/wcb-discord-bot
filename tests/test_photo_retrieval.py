"""Recovered originals reach the photo action with source lifecycle controls."""

import base64
import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from test_context_tools import call
from test_discord_client import fake_channel, fake_message, make_client
from test_learning import NOW
from test_photos import captured, photo_bytes, ready
from test_photos import photos as photo_fixture

from trubot.conversation import ReplyMode
from trubot.photo_action import NAME
from trubot.vision import decode_image

photos = photo_fixture


def permissions(channel, client):
    client.user = SimpleNamespace(id=999)
    channel.guild.fetch_member = AsyncMock(return_value=object())
    channel.permissions_for.return_value = SimpleNamespace(
        view_channel=True, read_message_history=True
    )


async def test_old_caption_supported_original_is_searchable_without_distillation(photos):
    memory, channel, client, responder = photos
    permissions(channel, client)
    _, row = await captured(
        photos, text="Old stone bridge across the creek.", created_at=NOW - timedelta(days=700)
    )
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())):
        evidence = await memory.recall("stone bridge creek", recipient=43)
        assert evidence and await evidence.current()
    assert evidence.images == (decode_image(photo_bytes()),)
    assert "stone bridge" in evidence.text
    assert row["state"] == "pending"
    responder.study_json.assert_not_awaited()
    assert channel.guild.fetch_member.await_count == 4


async def test_only_qualified_pixel_profiles_supply_search_terms(photos):
    memory, channel, client, responder = photos
    permissions(channel, client)
    _, row = await captured(photos, text="")
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())):
        assert await memory.recall("woodland clearing") is None
        ready(memory, row)
        assert await memory.recall("woodland clearing")
        assert await memory.recall("snowplow") is None
        assert await memory.recall("show original photo you shared") is None
    responder.study_json.assert_not_awaited()


@pytest.mark.parametrize(
    "change", ["edit", "delete", "withdraw", "permission", "pixels", "profile", "author", "access"]
)
async def test_fixed_source_changes_revoke_inflight_photo(photos, change):
    memory, channel, client, _ = photos
    permissions(channel, client)
    msg, row = await captured(photos, text="Stone bridge creek")
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())) as download:
        evidence = await memory.recall("stone bridge", recipient=43)
        assert evidence
        if change == "edit":
            msg.content = "Corrected."
        elif change == "delete":
            memory.store.drop(10, [msg.id], deleted=True, now=NOW)
        elif change == "withdraw":
            memory.learning.store.forget(now=NOW)
        elif change == "permission":
            channel.permissions_for.return_value.read_message_history = False
        elif change == "pixels":
            download.return_value = b"changed bytes"
        elif change == "profile":
            ready(memory, row)
        elif change == "author":
            msg.author.id = 43
        else:
            channel.fetch_message.side_effect = TimeoutError
        assert not await evidence.current()


async def test_peer_captions_cannot_supply_character_originals(photos):
    memory, channel, client, _ = photos
    permissions(channel, client)
    await captured(photos, author=43, text="Stone bridge creek")
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())) as fetch:
        assert await memory.recall("stone bridge") is None
        fetch.assert_not_awaited()


async def test_handler_sends_original_then_discards_changed_source(photos):
    memory, channel, photo_client, _ = photos
    permissions(channel, photo_client)
    msg, _ = await captured(photos, text="Stone bridge creek", created_at=NOW - timedelta(days=700))
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._photos = memory.learning, memory
    target_channel = fake_channel()
    target_channel.guild.id = 77
    target_channel.send.return_value = SimpleNamespace(
        id=900,
        guild=target_channel.guild,
        channel=target_channel,
        content="Here's the bridge.",
        edited_at=None,
        attachments=[],
    )
    focus = fake_message(target_channel)

    async def reply(messages, **kwargs):
        action = kwargs["photo_action"]
        assert await action.prepare(call(name=NAME, arguments='{"query":"stone bridge"}'))
        return action.decide(json.dumps({"attach": True, "reply": "Here's the bridge."}))

    responder.reply = reply
    with (
        patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())),
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "_memory_context", AsyncMock(return_value="")),
        patch.object(client, "_photo_request_current", AsyncMock(return_value=True)),
    ):
        assert await client._respond(
            target_channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=43,
            anchor=focus,
            target="Show the bridge photo.",
        )
        files = target_channel.send.call_args.kwargs["files"]
        assert len(files) == 1
        files[0].fp.seek(0)
        assert files[0].fp.read() == base64.b64decode(
            decode_image(photo_bytes()).data_url.split(",", 1)[1]
        )
        target_channel.send.reset_mock()

        async def change(messages, **kwargs):
            result = await reply(messages, **kwargs)
            msg.content = "Changed while composing."
            return result

        responder.reply = change
        assert not await client._respond(
            target_channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=43,
            anchor=focus,
            target="Show the bridge photo.",
        )
        target_channel.send.assert_not_awaited()
    client._learning = None
    await client.close()


async def test_rare_descriptive_term_beats_generic_related_scenery(photos):
    memory, _, _, _ = photos
    await captured(photos, text="Winter preparation at the dock on the water.", mid=300)
    await captured(photos, text="Winter preparation at the woodpile.", mid=400)
    await captured(
        photos, text="What the water looks like on the island this time of year.", mid=200
    )
    candidates = memory.recall_candidates("island winter water")
    assert candidates[0]["message"] == 200


async def test_candidate_checks_are_bounded_and_unavailable_pixels_never_fall_back_to_cache(photos):
    memory, channel, client, _ = photos
    permissions(channel, client)
    for i in range(5):
        await captured(photos, text="Stone bridge", mid=100 + i)
    memory.fresh = AsyncMock(return_value=None)
    assert await memory.recall("stone bridge") is None
    assert memory.fresh.await_count == 3


async def test_source_edit_during_pixel_read_never_reaches_continuation(photos):
    memory, channel, client, _ = photos
    permissions(channel, client)
    msg, _ = await captured(photos, text="Stone bridge")

    async def changed(url):
        msg.content = "Corrected."
        return photo_bytes()

    with patch("trubot.photos.download_image", changed):
        assert await memory.recall("stone bridge") is None


@pytest.mark.parametrize("requester", [42, 43])
async def test_action_preserves_requester_own_history_boundary(photos, requester):
    memory, _, _, _ = photos
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._photos = memory.learning, memory
    memory.recall = AsyncMock(return_value=None)
    channel = fake_channel()
    focus = fake_message(channel)
    focus.author.id = requester

    async def reply(messages, **kwargs):
        await kwargs["photo_action"].prepare(call(name=NAME, arguments='{"query":"stone bridge"}'))
        return "No photo."

    responder.reply = reply
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "_memory_context", AsyncMock(return_value="")),
        patch.object(client, "_photo_request_current", AsyncMock(return_value=True)),
    ):
        await client._respond(
            channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=requester,
            anchor=focus,
            target="Show my old messages about the stone bridge.",
        )
    assert memory.recall.await_count == (1 if requester == 42 else 0)
    client._learning = None
    await client.close()
