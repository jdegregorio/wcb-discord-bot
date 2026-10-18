"""A recalled attachment must reach the handler and survive pre-send pixel checks."""

import io
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image
from test_discord_client import fake_channel, fake_message, make_client
from test_learning import AUDIT, NOW, source
from test_native_context import message

from trubot.archives import ArchiveStore
from trubot.conversation import ReplyMode
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore
from trubot.memory import ContextMemory
from trubot.vision import ImageCollector


def pixel(color):
    out = io.BytesIO()
    Image.new("RGB", (32, 32), color).save(out, format="PNG")
    return out.getvalue()


@pytest.mark.parametrize("changed", [False, True])
async def test_actual_handler_supplies_source_pixels_and_discards_changed_pixels(tmp_path, changed):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(store)
    human = source(0, content="Something interesting on the game cam at camp.")
    store.observe(human, now=NOW)
    learner = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    channel = fake_channel()
    src = message(channel, human.id, text=human.content)
    learner.refresh = AsyncMock(return_value=src)
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)
    count = 0

    async def collect(_self, actual_source):
        nonlocal count
        if actual_source is not src:
            return (), ""
        from trubot.vision import decode_image

        count += 1
        return (decode_image(pixel("red" if changed and count > 1 else "green")),), ""

    async def reply(messages, **kwargs):
        memory = next(m for m in messages if m.origin == "memory")
        assert len(memory.images) == 1
        assert "VERIFIED HISTORICAL SOURCE PIXELS" in memory.content
        assert "posting time" in memory.content
        return "Something finally wandered past my camera."

    responder.reply = reply
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch("trubot.discord_client.collect_native_episode", AsyncMock(return_value=None)),
        patch.object(ImageCollector, "collect", collect),
    ):
        result = await client._respond(
            channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=1,
            anchor=fake_message(channel),
            target="Owner: see anything cool in the UP recently?",
        )
    assert result is not changed
    if changed:
        channel.send.assert_not_awaited()
    else:
        channel.send.assert_awaited_once_with("Something finally wandered past my camera.")
    await client.close()


async def test_photo_action_freshness_excludes_optional_neighborhood_and_voice_drift(tmp_path):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(store)
    human = source(content="Something on the game cam at camp.")
    store.observe(human, now=NOW)
    learner = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    channel = fake_channel()
    actual = message(channel, human.id, text=human.content)
    learner.refresh = AsyncMock(return_value=actual)
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)

    async def collect(_self, _message):
        from trubot.vision import decode_image

        return (decode_image(pixel("green")),), ""

    rows = []
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch("trubot.discord_client.collect_native_episode", AsyncMock()) as optional,
        patch("trubot.discord_client.voice_context") as voice,
        patch.object(ImageCollector, "collect", collect),
    ):
        for _ in range(3):
            images = []
            rows.append(
                await client._memory_context(
                    channel,
                    "Owner: Can I see?!",
                    [],
                    requester_user_id=1,
                    focus_author_user_id=1,
                    visual_sink=images,
                    visual_limit=1,
                    retrieval_query="game cam at camp",
                )
            )
            assert len(images) == 1
    assert len(set(rows)) == 1
    optional.assert_not_awaited()
    voice.assert_not_called()
    await client.close()


async def test_photo_action_does_not_forward_a_source_the_recipient_cannot_read(tmp_path):
    from types import SimpleNamespace

    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(store)
    human = source(content="A game cam at camp.")
    store.observe(human, now=NOW)
    learner = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    channel = fake_channel()
    channel.guild.fetch_member = AsyncMock(return_value=object())
    channel.permissions_for.return_value = SimpleNamespace(
        view_channel=False, read_message_history=True
    )
    learner.refresh = AsyncMock(return_value=message(channel, human.id, text=human.content))
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)
    pixels = []
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch.object(ImageCollector, "collect", AsyncMock()) as collect,
    ):
        await client._memory_context(
            channel,
            "Owner: Can I see?!",
            [],
            requester_user_id=1,
            focus_author_user_id=1,
            visual_sink=pixels,
            visual_limit=1,
            retrieval_query="game cam",
            photo_recipient_user_id=1,
        )
    assert not pixels
    collect.assert_not_awaited()
    await client.close()
