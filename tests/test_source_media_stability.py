"""Mandatory fresh source metadata must survive optional neighborhood read loss."""

from unittest.mock import AsyncMock, patch

import pytest
from test_discord_client import fake_message, make_client
from test_learning import NOW
from test_native_reply_batch import setup as native_setup

from trubot.conversation import ReplyMode
from trubot.memory import ContextMemory
from trubot.native_context import NativeEpisode

setup = native_setup

MEDIA_GAP = "source media pixels not retrieved; do not interpret image-dependent meaning"


def source_metadata(selected):
    for row in selected:
        row.attachments, row.embeds = [], []
    selected[1].attachments = [object()]


@pytest.mark.parametrize("mode", list(ReplyMode))
@pytest.mark.parametrize("timeout_first", [True, False])
@pytest.mark.parametrize("quality_check", [True, False])
async def test_media_only_setup_loss_preserves_actual_handler_packet(
    setup, mode, timeout_first, quality_check
):
    store, learner, channel, selected, _ = setup
    source_metadata(selected)
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)
    calls, packets, reuse_checks = 0, [], []
    original = client._memory_context

    async def capture(*args, **kwargs):
        packet = await original(*args, **kwargs)
        packets.append(packet)
        return packet

    async def collect(_channel, _identifier, **kwargs):
        nonlocal calls
        calls += 1
        focus = kwargs["focus"]
        if calls % 2:
            return NativeEpisode(focus.content, None, ({"text": "Stable human setup."},))
        if (calls <= 2) is timeout_first:
            raise TimeoutError
        return NativeEpisode(focus.content, None, (), (MEDIA_GAP,))

    async def reply(messages, **kwargs):
        assert any("Stable human setup." in row.content for row in messages)
        assert any(MEDIA_GAP in row.content for row in messages)
        if quality_check:
            reuse_checks.append(await kwargs["refresh_check"]())
        return "A supported answer."

    responder.reply = reply
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch.object(client, "_memory_context", side_effect=capture),
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch("trubot.discord_client.collect_native_episode", side_effect=collect),
    ):
        assert await client._respond(
            channel,
            mode=mode,
            requester_user_id=1,
            anchor=fake_message(channel),
            target="Owner: Which baseball club do you support?",
        )
    assert len(set(packets)) == 1
    assert reuse_checks == ([True] if quality_check else [])
    channel.send.assert_awaited_once_with("A supported answer.")
    await client.close()


@pytest.mark.parametrize("source_index", [0, 3])
@pytest.mark.parametrize("change", ["appears", "removed", "unknown"])
async def test_fresh_media_changes_discard_even_without_optional_setup(setup, source_index, change):
    store, learner, channel, selected, _ = setup
    source_metadata(selected)
    focus = selected[source_index]
    if change == "removed":
        focus.embeds = [object()]
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)

    async def reply(messages, **kwargs):
        if change == "appears":
            focus.attachments = [object()]
        elif change == "removed":
            focus.embeds = []
        else:
            del focus.embeds
        return "A draft with obsolete media context."

    responder.reply = reply
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch("trubot.discord_client.collect_native_episode", AsyncMock(side_effect=TimeoutError)),
    ):
        assert not await client._respond(
            channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=1,
            anchor=fake_message(channel),
            target="Owner: Which baseball club do you support?",
        )
    channel.send.assert_not_awaited()
    await client.close()


async def test_source_only_metadata_is_ephemeral_and_never_a_durable_capture(setup):
    store, learner, channel, selected, requests = setup
    source_metadata(selected)
    # A source beyond the two-neighborhood cap still contributes fresh metadata.
    selected[4].embeds = [object()]
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch("trubot.discord_client.collect_native_episode", AsyncMock(side_effect=TimeoutError)),
        patch("trubot.discord_client.GraphStore.record_native_context") as record,
    ):
        packet = await client._memory_context(channel, "Owner: baseball mascot", [])
    assert packet.count(MEDIA_GAP) == 2
    assert "native setup and source media pixels not supplied" in packet
    assert len(requests) == 1
    record.assert_not_called()
    assert len(selected) == 5
    await client.close()


@pytest.mark.parametrize("invalid", ["content", "edited_at"])
def test_incomplete_source_metadata_cannot_supply_a_snapshot(invalid):
    from types import SimpleNamespace

    from trubot.native_context import source_media_episode

    row = SimpleNamespace(content="Complete source.", edited_at=None, attachments=[], embeds=[])
    setattr(row, invalid, object())
    assert source_media_episode(row) is None
