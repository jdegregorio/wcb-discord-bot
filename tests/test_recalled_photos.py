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
