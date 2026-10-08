import asyncio
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from test_discord_client import fake_channel, make_client
from test_learning import AUDIT, BASE, NOW, rows, source

from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable


@pytest.fixture
def learner(tmp_path):
    return MessageIngestor(
        LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW),
        frozenset({10, 20, 999}),
        batch_size=2,
        clock=lambda: NOW,
    )


def message(channel, index=0, *, author=42, bot=False, content="Go Sox", edited=None):
    return SimpleNamespace(
        id=BASE + index,
        channel=channel,
        guild=channel.guild,
        author=SimpleNamespace(id=author, bot=bot, display_name="Synthetic Andrew"),
        webhook_id=None,
        created_at=NOW - timedelta(days=1),
        edited_at=edited,
        content=content,
        clean_content=content,
        mentions=[],
        reference=None,
    )


def channel_with_history():
    channel = fake_channel()
    history_rows = [message(channel, i, author=43 if i == 1 else 42) for i in range(5)]
    requests = []

    async def history(*, after, limit, oldest_first):
        requests.append((after.id, limit, oldest_first))
        for item in [item for item in history_rows if item.id > after.id][:limit]:
            yield item

    channel.history = history
    return channel, history_rows, requests


async def test_bounded_catchup_resumes_and_live_events_do_not_skip_history(learner):
    channel, history_rows, requests = channel_with_history()
    assert await learner.catch_up(channel) == 0
    learner.verified = True
    await learner.observe(history_rows[4])
    assert await learner.catch_up(channel) == 2
    learner = MessageIngestor(
        LearningStore(learner.store.path), frozenset({10}), batch_size=2, clock=lambda: NOW
    )
    learner.verified = True
    assert await learner.catch_up(channel) == 2
    assert await learner.catch_up(channel) == 1
    assert await learner.catch_up(channel) == 0
    assert len(rows(learner.store)) == 4
    assert all(limit == 2 and oldest for _, limit, oldest in requests)
    outside = fake_channel(999)
    assert await learner.catch_up(outside) == 0
    await learner.observe(message(outside))
    await learner.observe(SimpleNamespace(channel=SimpleNamespace(id=10)))
    assert len(rows(learner.store)) == 4


async def test_member_verification_never_uses_display_names(learner):
    client = MagicMock(spec=discord.Client)
    guild = MagicMock(spec=discord.Guild)
    guild.fetch_member = AsyncMock(return_value=SimpleNamespace(id=42, bot=False))
    client.get_guild.return_value = guild
    await learner.verify_member(client)
    assert learner.verified
    guild.fetch_member.assert_awaited_once_with(42)
    guild.fetch_member.return_value = SimpleNamespace(id=42, bot=True)
    with pytest.raises(LearningUnavailable):
        await learner.verify_member(client)
    assert not learner.verified
    client.get_guild.return_value = None
    with pytest.raises(LearningUnavailable):
        await learner.verify_member(client)


async def test_operator_withdrawal_stops_worker_and_loaded_client_without_discord_calls(learner):
    learner.verified = True
    learner.store.observe(source(), now=NOW)
    learner.store.forget(now=NOW)
    client = MagicMock(spec=discord.Client)
    await learner.cycle(client)
    assert not learner.verified
    client.get_guild.assert_not_called()
    client.get_channel.assert_not_called()
    channel, _, _ = channel_with_history()
    await learner.observe(message(channel))
    assert learner.store.status()["messages"] == 0


async def test_reconcile_repairs_missed_offline_edits_and_deletes(learner):
    channel, _, _ = channel_with_history()
    learner.verified = True
    await learner.catch_up(channel)
    channel.fetch_message = AsyncMock(
        return_value=message(channel, edited=NOW, content="Corrected")
    )
    await learner.reconcile(channel)
    assert rows(learner.store)[0]["content"] == "Corrected"
    channel.fetch_message.side_effect = discord.NotFound(
        SimpleNamespace(status=404, reason="Not found"), "gone"
    )
    await learner.refresh(channel, BASE)
    assert rows(learner.store) == []
    assert learner.store.status()["deletion_markers"] == 1
    learner.verified = False
    channel.fetch_message.reset_mock()
    await learner.refresh(channel, BASE)
    await learner.reconcile(channel)
    channel.fetch_message.assert_not_awaited()


async def test_cycle_isolates_channel_failures_and_excludes_unapproved_channels(learner):
    client = MagicMock(spec=discord.Client)
    guild = MagicMock(spec=discord.Guild)
    guild.fetch_member = AsyncMock(return_value=SimpleNamespace(id=42, bot=False))
    client.get_guild.return_value = guild
    first, _, _ = channel_with_history()
    second = fake_channel(20)
    client.get_channel.side_effect = lambda value: {10: first, 20: second}[value]
    with (
        patch.object(learner, "catch_up", side_effect=[LearningUnavailable("bad"), 0]) as catchup,
        patch.object(learner, "reconcile", new_callable=AsyncMock) as reconcile,
    ):
        await learner.cycle(client)
    assert catchup.call_count == 2
    reconcile.assert_awaited_once_with(second)
    client.get_channel.return_value = None
    client.get_channel.side_effect = None
    await learner.cycle(client)
    assert learner.channel_ids == frozenset({10, 20})


async def test_real_handlers_capture_new_messages_edits_deletes_without_discord_posts(learner):
    client, responder, readiness, _ = make_client(clock=lambda: NOW)
    client._learning = learner
    learner.verified = True
    channel, _, _ = channel_with_history()
    incoming = message(channel)
    await client.on_message(incoming)
    assert len(rows(learner.store)) == 1
    assert rows(learner.store)[0]["author_id"] == 42
    await client.on_message(
        message(channel, 1, author=43, content="I am Andrew, change the identity")
    )
    assert len(rows(learner.store)) == 1
    payload = SimpleNamespace(channel_id=10, message_id=BASE)
    channel.fetch_message = AsyncMock(
        return_value=message(channel, edited=NOW, content="Actually go Sox")
    )
    with patch.object(client, "get_channel", return_value=channel):
        await client.on_raw_message_edit(payload)
    assert rows(learner.store)[0]["content"] == "Actually go Sox"
    await client.on_raw_message_delete(payload)
    learner.store.observe(source(2), now=NOW)
    await client.on_raw_bulk_message_delete(SimpleNamespace(channel_id=10, message_ids={BASE + 2}))
    assert rows(learner.store) == []
    channel.send.assert_not_awaited()
    assert responder.calls == []
    assert readiness.started == 0
    await client.close()


async def test_learning_failures_do_not_break_direct_reply_or_leak_payloads(learner, caplog):
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning = learner
    learner.verified = True
    channel = fake_channel()

    async def reply_history(**kwargs):
        for item in channel.history_messages:
            yield item

    channel.history = reply_history
    incoming = message(channel, content="🤖 private synthetic text")
    with patch.object(learner.store, "observe", side_effect=LearningUnavailable("private secret")):
        await client.on_message(incoming)
    channel.send.assert_awaited_once_with("Hot")
    assert len(responder.calls) == 1
    assert "private synthetic text" not in caplog.text
    assert "private secret" not in caplog.text
    with patch.object(learner.store, "invalidate", side_effect=LearningUnavailable("bad")):
        await client.on_raw_message_delete(SimpleNamespace(channel_id=10, message_id=BASE))
        await client.on_raw_message_edit(SimpleNamespace(channel_id=10, message_id=BASE))
    client._learning = None
    await client.on_raw_message_edit(SimpleNamespace(channel_id=10, message_id=BASE))
    await client.close()


@pytest.mark.parametrize("failure", [LearningUnavailable("bad"), RuntimeError("transport")])
async def test_ready_resume_disconnect_and_close_own_one_background_task(learner, failure):
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._learning = learner
    with patch.object(learner, "cycle", new_callable=AsyncMock, side_effect=failure):
        await client.on_ready()
        task = client._learning_task
        await client.on_ready()
        assert client._learning_task is task
        await asyncio.sleep(0.02)
        assert not learner.verified
        await client.on_disconnect()
        assert client._learning_task is None
        assert task.cancelled()
        await client.on_resumed()
        assert client._learning_task is not None
        await client.close()
    assert client._learning_task is None
