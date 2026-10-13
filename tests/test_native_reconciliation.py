"""Offline human setup corrections through the actual collector and learning worker."""

import asyncio
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from test_learning import AUDIT, BASE, NOW, source
from test_native_context import message
from test_native_context_links import capture, graph_text, metadata

from trubot.archives import ArchiveStore
from trubot.episode_memory import automated_pattern_context
from trubot.graph import GraphStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable
from trubot.native_context import collect_native_episode
from trubot.native_reconciliation import verify_native_context


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(learning)
    return learning, GraphStore.initialize(learning)


async def prepared(stores):
    learning, graph = stores
    episode, channel, focus, peer = await capture(stores)
    graph.record_native_context(episode, now=NOW)
    channel.fetch_message = AsyncMock(side_effect=lambda mid: focus if mid == focus.id else peer)
    learner = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    client = MagicMock(spec=discord.Client)
    client.get_channel.return_value = channel
    return learner, client, channel, focus, peer


async def test_current_context_is_ephemeral_and_revalidated_each_time(stores):
    learner, client, channel, focus, peer = await prepared(stores)
    graph = stores[1]
    before = metadata(graph)
    verified = await verify_native_context(learner, channel, before[0])
    assert verified.neighbors[0]["text"] == peer.content
    assert verified.neighbors[0]["focus_replies_to_this"]
    assert verified.matches(focus.content, None)
    assert peer.content not in repr(verified)
    assert metadata(graph) == before  # No durable freshness certificate.
    assert (await learner.reconcile_native_context(client)) == {
        "verified": 1,
        "removed": 0,
        "unavailable": 0,
    }
    assert peer.content not in graph_text(graph)
    with graph._transaction() as (_, source_db):
        snapshot = graph._snapshot({"kind": "discord", "message_id": BASE}, source_db, now=NOW)
    assert not automated_pattern_context([snapshot])
    assert channel.fetch_message.await_count == 4


@pytest.mark.parametrize(
    "problem",
    [
        "edit",
        "unversioned_edit",
        "deleted",
        "denied",
        "bot",
        "webhook",
        "author",
        "guild",
        "channel",
        "old",
        "future",
        "created",
        "reference",
        "media",
        "wrong_id",
    ],
)
async def test_offline_dependency_changes_or_access_loss_erase_capture_and_backup(stores, problem):
    learner, client, channel, focus, peer = await prepared(stores)
    learning, graph = stores
    backup_dir = graph.path.parent / "backups"
    backup_dir.mkdir(mode=0o700)
    backup = backup_dir / "memory-graph-prior.sqlite3"
    backup.write_bytes(graph.path.read_bytes())
    backup.chmod(0o600)
    if problem in ("edit", "unversioned_edit"):
        peer.content = "The fictional invitation is withdrawn."
        if problem == "edit":
            peer.edited_at = NOW
    elif problem in ("deleted", "denied"):
        cls = discord.NotFound if problem == "deleted" else discord.Forbidden
        error = cls(
            SimpleNamespace(status=404 if problem == "deleted" else 403, reason="Gone"),
            "private payload",
        )
        channel.fetch_message.side_effect = lambda mid: (
            focus if mid == focus.id else (_ for _ in ()).throw(error)
        )
    elif problem == "bot":
        peer.author.bot = True
    elif problem == "webhook":
        peer.webhook_id = 1
    elif problem == "author":
        peer.author.id = 88
    elif problem == "guild":
        peer.guild = SimpleNamespace(id=88)
    elif problem == "channel":
        peer.channel = SimpleNamespace(id=88)
    elif problem == "old":
        peer.created_at = NOW - timedelta(days=181)
    elif problem == "future":
        peer.created_at = NOW + timedelta(days=1)
    elif problem == "created":
        peer.created_at += timedelta(seconds=1)
    elif problem == "reference":
        peer.reference = discord.MessageReference(message_id=123, channel_id=10, guild_id=77)
    elif problem == "media":
        peer.attachments = [object()]
    else:
        peer.id += 10
    # No gateway invalidation is provided; existing source sweep alone cannot repair a peer.
    graph.sweep(now=NOW)
    assert len(metadata(graph)) == 1
    result = await learner.reconcile_native_context(client)
    assert result["removed"] == 1
    assert not metadata(graph)
    assert not graph.status()["nodes"].get("native_context_dependency")
    assert not backup.exists()
    assert learning.status()["messages"] == 1


@pytest.mark.parametrize("problem", ["transport", "timeout"])
async def test_transient_failures_do_not_certify_or_imply_deletion(stores, problem, caplog):
    learner, client, channel, focus, _ = await prepared(stores)
    graph = stores[1]
    before = metadata(graph)
    error = (
        TimeoutError("private source")
        if problem == "timeout"
        else discord.HTTPException(
            SimpleNamespace(status=503, reason="Unavailable"), "private source"
        )
    )
    channel.fetch_message.side_effect = lambda mid: (
        focus if mid == focus.id else (_ for _ in ()).throw(error)
    )
    result = await learner.reconcile_native_context(client)
    assert result == {"verified": 0, "removed": 0, "unavailable": 1}
    assert metadata(graph) == before
    assert "private source" not in caplog.text


@pytest.mark.parametrize("problem", ["withdrawal", "identity", "verification", "scope"])
async def test_scope_loss_blocks_dependency_reads(stores, problem):
    learner, _client, channel, focus, _ = await prepared(stores)
    old = metadata(stores[1])[0]

    async def fetch(mid):
        assert mid == focus.id
        if problem == "withdrawal":
            learner.store.forget(now=NOW)
        elif problem == "identity":
            learner.identity = replace(learner.identity, user_id=99)
        elif problem == "verification":
            learner.verified = False
        else:
            learner.channel_ids = frozenset()
        return focus

    channel.fetch_message.side_effect = fetch
    with pytest.raises(LearningUnavailable):
        await verify_native_context(learner, channel, old)
    assert channel.fetch_message.await_count == 1


async def test_newer_capture_survives_raced_stale_verifier(stores):
    learner, client, channel, focus, peer = await prepared(stores)
    graph = stores[1]
    old = metadata(graph)[0]
    fresh, _, _, _ = await capture(
        stores, text="A corrected setup.", now=NOW + timedelta(seconds=1)
    )

    async def fetch(mid):
        if mid == focus.id:
            return focus
        graph.record_native_context(fresh, now=NOW + timedelta(seconds=1))
        peer.content = "A corrected setup."
        return peer

    channel.fetch_message.side_effect = fetch
    result = await learner.reconcile_native_context(client)
    assert result["verified"] == result["removed"] == 0
    assert len(metadata(graph)) == 1
    assert metadata(graph)[0]["captured_at"] == (NOW + timedelta(seconds=1)).isoformat()
    assert not graph.discard_native_context(old)


async def test_source_change_and_known_peer_events_fail_closed(stores):
    learner, client, channel, focus, _ = await prepared(stores)
    focus.content = "Actually, I oppose the dragon roster."
    focus.edited_at = NOW
    result = await learner.reconcile_native_context(client)
    assert result["verified"] == 0
    assert not metadata(stores[1])
    assert channel.fetch_message.await_count == 1


async def test_known_peer_event_during_reads_fails_final_locked_check(stores):
    learner, client, channel, focus, peer = await prepared(stores)

    async def fetch(mid):
        if mid == focus.id:
            return focus
        learner.store.invalidate(10, [peer.id], deleted=False, now=NOW)
        return peer

    channel.fetch_message.side_effect = fetch
    result = await learner.reconcile_native_context(client)
    assert result["verified"] == 0
    assert not metadata(stores[1])


async def test_rotation_survives_restart_and_scope_filter_is_authoritative(stores):
    await prepared(stores)
    learning, graph = stores
    original = (await capture(stores))[0]
    for index in (1, 2, 3):
        row = source(index, content=f"Invented source {index}")
        learning.observe(row, now=NOW)
        graph.record_native_context(replace(original, source=row, source_text=row.content), now=NOW)
    first = graph.native_context_targets(now=NOW, channel_ids=frozenset({10}))
    reopened = GraphStore(LearningStore(learning.path))
    second = reopened.native_context_targets(now=NOW, channel_ids=frozenset({10}))
    assert len(first) == len(second) == 2
    assert {x["ref"]["message_id"] for x in first}.isdisjoint(
        {x["ref"]["message_id"] for x in second}
    )
    assert reopened.native_context_targets(now=NOW, channel_ids=frozenset({999})) == []
    assert reopened.native_context_targets(now=NOW, channel_ids=frozenset({10})) == first
    with pytest.raises(LearningUnavailable):
        reopened.native_context_targets(now=NOW, channel_ids=frozenset({10}), limit=3)


async def test_missing_graph_does_not_interrupt_existing_learning_cycle(stores):
    learner, client, _, _, _ = await prepared(stores)
    stores[1].path.unlink()
    with (
        patch.object(learner, "verify_member", AsyncMock()),
        patch.object(learner, "catch_up", AsyncMock(return_value=0)),
        patch.object(learner, "reconcile", AsyncMock()),
    ):
        await learner.cycle(client)
    assert learner.verified


async def test_worker_owns_reconciliation_and_two_capture_bound(stores):
    learner, client, channel, _, _ = await prepared(stores)
    with (
        patch.object(learner, "verify_member", AsyncMock()),
        patch.object(learner, "catch_up", AsyncMock(return_value=0)),
        patch.object(learner, "reconcile", AsyncMock()),
        patch.object(
            learner,
            "reconcile_native_context",
            AsyncMock(return_value={"verified": 1, "removed": 0, "unavailable": 0}),
        ) as check,
    ):
        await learner.cycle(client)
    check.assert_awaited_once_with(client)
    learner.verified = False
    channel.fetch_message.reset_mock()
    assert (await learner.reconcile_native_context(client))["verified"] == 0
    channel.fetch_message.assert_not_awaited()


async def test_oversized_dependencies_remain_complete_fingerprints_without_text(stores):
    learning, graph = stores
    episode, channel, focus, peer = await capture(stores, text="x" * 601)
    graph.record_native_context(episode, now=NOW)
    learner = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    channel.fetch_message = AsyncMock(side_effect=lambda mid: focus if mid == focus.id else peer)
    current = await verify_native_context(learner, channel, metadata(graph)[0])
    assert current.neighbors == ()
    assert "omitted for size" in current.gaps[0]
    assert peer.content not in graph_text(graph)


async def test_request_timeout_is_bounded_and_retains_only_observed_metadata(stores):
    learner, client, channel, _, _ = await prepared(stores)

    async def blocked(_mid):
        await asyncio.sleep(2)

    channel.fetch_message.side_effect = blocked
    started = asyncio.get_running_loop().time()
    result = await learner.reconcile_native_context(client)
    assert asyncio.get_running_loop().time() - started < 1.6
    assert result["unavailable"] == 1
    assert len(metadata(stores[1])) == 1


async def two_full_captures(stores):
    learner, client, channel, _, _ = await prepared(stores)
    learning, graph = stores
    all_messages = {}
    for offset in (0, 10):
        native = source(offset, content=f"Invented roster response {offset}.")
        learning.observe(native, now=NOW)
        focus = message(channel, native.id, text=native.content, created_at=native.created_at)
        peers = [
            message(
                channel,
                native.id - n,
                author=9,
                text=f"Complete fictional setup {offset}:{n}",
                created_at=native.created_at,
            )
            for n in range(1, 6)
        ]

        async def history(captured=peers, **_kwargs):
            for peer in captured:
                yield peer

        channel.history = history
        episode = await collect_native_episode(
            channel, focus.id, identity=learner.identity, now=NOW, retention_days=180, focus=focus
        )
        graph.record_native_context(episode, now=NOW)
        all_messages[focus.id] = focus
        all_messages.update({peer.id: peer for peer in peers})
    channel.fetch_message = AsyncMock(side_effect=lambda mid: all_messages[mid])
    return learner, client, channel, all_messages


async def test_two_capture_twelve_fetch_ceiling(stores):
    learner, client, channel, _ = await two_full_captures(stores)
    result = await learner.reconcile_native_context(client)
    assert result == {"verified": 2, "removed": 0, "unavailable": 0}
    assert channel.fetch_message.await_count == 12


async def test_total_six_second_ceiling_preserves_unfinished_metadata(stores):
    learner, client, channel, messages = await two_full_captures(stores)

    async def fetch(mid):
        await asyncio.sleep(0.7)
        return messages[mid]

    channel.fetch_message.side_effect = fetch
    started = asyncio.get_running_loop().time()
    result = await learner.reconcile_native_context(client)
    elapsed = asyncio.get_running_loop().time() - started
    assert 5.9 <= elapsed < 6.7
    assert result == {"verified": 1, "removed": 0, "unavailable": 1}
    assert channel.fetch_message.await_count <= 12
    assert len(metadata(stores[1])) == 2


async def test_unavailable_channel_and_withdrawal_before_selection_do_not_read(stores):
    learner, client, channel, _, _ = await prepared(stores)
    client.get_channel.return_value = None
    assert (await learner.reconcile_native_context(client))["unavailable"] == 1
    channel.fetch_message.assert_not_awaited()
    learner.store.forget(now=NOW)
    client.get_channel.reset_mock()
    with pytest.raises(LearningUnavailable):
        await learner.reconcile_native_context(client)
    client.get_channel.assert_not_called()


async def test_cancellation_is_not_swallowed(stores):
    learner, client, channel, _, _ = await prepared(stores)
    channel.fetch_message.side_effect = asyncio.CancelledError()
    with pytest.raises(asyncio.CancelledError):
        await learner.reconcile_native_context(client)
    assert len(metadata(stores[1])) == 1


async def test_restored_obsolete_capture_is_rejected_on_fresh_dependency_read(stores):
    learner, client, channel, _, peer = await prepared(stores)
    graph = stores[1]
    old = graph.path.read_bytes()
    peer.content = "Corrected while the gateway was offline."
    await learner.reconcile_native_context(client)
    assert not metadata(graph)
    graph.path.write_bytes(old)
    # Restoring an old observed capture does not establish fresh visibility.
    assert await verify_native_context(learner, channel, metadata(graph)[0]) is None
    await learner.reconcile_native_context(client)
    assert not metadata(graph)


async def test_source_media_presence_change_invalidates_captured_setup(stores):
    learner, client, channel, focus, _ = await prepared(stores)
    focus.attachments = [object()]
    result = await learner.reconcile_native_context(client)
    assert result["verified"] == 0
    assert not metadata(stores[1])
    assert channel.fetch_message.await_count == 1
