"""Synthetic dependency lifecycle through the actual native collector and handlers."""

import json
import sqlite3
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

import discord
import pytest
from test_discord_client import make_client
from test_learning import AUDIT, BASE, NOW, source
from test_native_context import channel_with, message

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory
from trubot.native_context import collect_native_episode


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(learning)
    graph = GraphStore.initialize(learning)
    return learning, graph


async def capture(stores, *, peer=9, text="Only pretend: invite the dragon.", extra=None, now=NOW):
    learning, _ = stores
    focus_source = source(content="The dragon roster idea sounds great.")
    learning.observe(focus_source, now=now)
    channel, focus = channel_with()
    focus.id, focus.created_at, focus.content = BASE, focus_source.created_at, focus_source.content
    row = message(channel, BASE - 1, author=peer, text=text, created_at=focus.created_at)
    if extra:
        for key, value in extra.items():
            setattr(row, key, value)
    focus.reference = discord.MessageReference(message_id=row.id, channel_id=10, guild_id=77)

    async def history(**_kwargs):
        yield row
        yield focus

    channel.history = history
    channel.fetch_message.return_value = focus
    episode = await collect_native_episode(
        channel, focus.id, identity=learning.identity(), now=now, retention_days=180
    )
    return episode, channel, focus, row


def metadata(graph):
    with graph._transaction() as (db, _):
        return [
            json.loads(row[0])
            for row in db.execute("SELECT data FROM nodes WHERE kind='native_context'")
        ]


def graph_text(graph):
    with sqlite3.connect(graph.path) as db:
        return " ".join(row[0] for row in db.execute("SELECT data FROM nodes")) + " ".join(
            row[0] for row in db.execute("SELECT evidence FROM edges")
        )


async def test_source_connected_metadata_survives_restart_without_raw_text(stores):
    learning, graph = stores
    episode, _, _, row = await capture(stores)
    assert graph.record_native_context(episode, now=NOW)
    reopened = GraphStore(LearningStore(learning.path))
    data = metadata(reopened)[0]
    assert data["ref"]["message_id"] == BASE
    assert data["dependencies"][0]["message_id"] == row.id
    assert data["dependencies"][0]["speaker_id"] == 9
    assert data["dependencies"][0]["focus_replies_to_this"]
    assert data["source_time"] == source().created_at.isoformat()
    assert data["captured_at"] == NOW.isoformat()
    assert "fresh reads required" in data["visibility"]
    assert row.content not in graph_text(graph)
    assert episode.source_text not in graph_text(graph)
    assert row.content not in repr(episode)
    assert graph.status()["nodes"]["native_context_dependency"] == 1
    with graph._transaction() as (db, _):
        assert (
            db.execute("SELECT COUNT(*) FROM edges WHERE relation='context-for'").fetchone()[0] == 1
        )
        assert (
            db.execute("SELECT COUNT(*) FROM edges WHERE relation='depends-on'").fetchone()[0] == 1
        )
    assert graph.path.stat().st_mode & 0o077 == 0


@pytest.mark.parametrize("deleted", [False, True])
async def test_peer_event_erases_context_and_backup_and_blocks_restored_capture(stores, deleted):
    learning, graph = stores
    episode, _, _, row = await capture(stores)
    graph.record_native_context(episode, now=NOW)
    old_graph = graph.path.read_bytes()
    backups = graph.path.parent / "backups"
    backups.mkdir(mode=0o700)
    backup = backups / "memory-graph-previous.sqlite3"
    backup.write_bytes(old_graph)
    backup.chmod(0o600)
    learning.invalidate(10, [row.id], deleted=deleted, now=NOW + timedelta(seconds=1))
    assert not metadata(graph)
    assert not graph.status()["nodes"].get("native_context_dependency")
    assert not backup.exists()
    graph.path.write_bytes(old_graph)
    assert graph.sweep(now=NOW + timedelta(seconds=2)) == 1
    assert not metadata(graph)


@pytest.mark.parametrize("deleted", [False, True])
async def test_inflight_peer_invalidation_cannot_commit(stores, deleted):
    learning, graph = stores
    episode, _, _, row = await capture(stores)
    learning.invalidate(10, [row.id], deleted=deleted, now=NOW)
    with pytest.raises(LearningUnavailable, match="invalidated"):
        graph.record_native_context(episode, now=NOW)
    assert not metadata(graph)


async def test_fresh_capture_after_known_peer_edit_and_old_capture_cannot_overwrite(stores):
    learning, graph = stores
    old, _, _, row = await capture(stores)
    learning.invalidate(10, [row.id], deleted=False, now=NOW + timedelta(seconds=1))
    fresh, _, _, _ = await capture(
        stores, text="A corrected setup.", now=NOW + timedelta(seconds=2)
    )
    assert graph.record_native_context(fresh, now=NOW + timedelta(seconds=2))
    before = metadata(graph)
    with pytest.raises(LearningUnavailable):
        graph.record_native_context(old, now=NOW + timedelta(seconds=2))
    assert metadata(graph) == before
    assert "A corrected setup." not in graph_text(graph)


@pytest.mark.parametrize("kind", ["edited", "deleted", "retention", "capture_expiry"])
async def test_focus_lifecycle_and_capture_retention(stores, kind):
    learning, graph = stores
    episode, _, _, _ = await capture(stores)
    graph.record_native_context(episode, now=NOW)
    if kind == "edited":
        learning.observe(source(content="Actually no.", edited_at=NOW, authoritative=True), now=NOW)
    elif kind == "deleted":
        learning.invalidate(10, [BASE], deleted=True, now=NOW)
    elif kind == "retention":
        learning.prune(now=NOW + timedelta(days=181))
    else:
        graph.sweep(now=NOW + timedelta(days=31))
    assert not metadata(graph)
    assert not graph.status()["nodes"].get("native_context_dependency")


async def test_target_neighbor_change_invalidates_restored_metadata_after_edit_marker_cleared(
    stores,
):
    learning, graph = stores
    episode, _, _, row = await capture(stores, peer=42)
    learning.observe(source(-1, content=row.content), now=NOW)
    graph.record_native_context(episode, now=NOW)
    old = graph.path.read_bytes()
    learning.invalidate(10, [row.id], deleted=False, now=NOW)
    learning.observe(
        source(-1, content="A new target setup.", edited_at=NOW, authoritative=True), now=NOW
    )
    graph.path.write_bytes(old)
    graph.sweep(now=NOW)
    assert not metadata(graph)


@pytest.mark.parametrize(
    "problem",
    [
        "text",
        "guild",
        "channel",
        "future",
        "duplicate",
        "oversized_set",
        "hash",
        "bot_source",
        "peer_source",
        "stale_source",
        "missing_source",
    ],
)
async def test_forged_or_unbounded_capture_is_rejected(stores, problem):
    _, graph = stores
    episode, _, _, _ = await capture(stores)
    row = dict(episode.dependencies[0])
    if problem == "text":
        row["text"] = "Never persist this private text."
    elif problem in ("guild", "channel"):
        row[problem + "_id"] = 999
    elif problem == "future":
        row["created_at"] = (NOW + timedelta(days=1)).isoformat()
    elif problem == "hash":
        row["content_sha256"] = "private text"
    elif problem == "bot_source":
        episode = replace(episode, source=replace(episode.source, bot=True))
    elif problem == "peer_source":
        episode = replace(episode, source=replace(episode.source, author_id=9))
    elif problem == "stale_source":
        episode = replace(
            episode, source=replace(episode.source, observed_at=NOW - timedelta(seconds=31))
        )
    elif problem == "missing_source":
        episode = replace(episode, source=None)
    deps = (row,) * (6 if problem == "oversized_set" else 2 if problem == "duplicate" else 1)
    episode = replace(episode, dependencies=deps)
    with pytest.raises(LearningUnavailable):
        graph.record_native_context(episode, now=NOW)
    assert not metadata(graph)
    assert "Never persist" not in graph_text(graph)


async def test_oversized_setup_tracks_dependency_without_persisting_a_prefix(stores):
    _, graph = stores
    episode, _, _, row = await capture(stores, text="Never persist this prefix " + "x" * 600)
    assert not episode.neighbors
    assert len(episode.dependencies) == 1
    graph.record_native_context(episode, now=NOW)
    assert metadata(graph)[0]["dependencies"][0]["message_id"] == row.id
    assert "omitted for size" in metadata(graph)[0]["gaps"][0]
    assert "Never persist this prefix" not in graph_text(graph)


async def test_real_memory_handler_captures_links_and_reply_survives_missing_graph(stores):
    learning, graph = stores
    _, channel, focus, row = await capture(stores)
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._learning = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    client._learning.verified = True
    client._memory = ContextMemory(learning)
    with patch.object(client, "get_channel", return_value=channel):
        packet = await client._memory_context(
            channel, "Tim: What did Andrew say recently about the dragon roster?", []
        )
        assert row.content in packet
        assert len(metadata(graph)) == 1
        graph.path.unlink()
        packet = await client._memory_context(
            channel, "Tim: What did Andrew say recently about the dragon roster?", []
        )
        assert focus.content in packet
    assert learning.status()["messages"] == 1
    await client.close()


async def test_denied_context_replaces_old_dependencies_with_gap(stores):
    _, graph = stores
    episode, channel, focus, _ = await capture(stores)
    graph.record_native_context(episode, now=NOW)

    async def denied(**_kwargs):
        raise discord.Forbidden(SimpleNamespace(status=403, reason="Denied"), "Denied")
        yield  # pragma: no cover

    channel.history = denied
    gap = await collect_native_episode(
        channel, focus.id, identity=stores[0].identity(), now=NOW, retention_days=180
    )
    graph.record_native_context(gap, now=NOW)
    assert metadata(graph)[0]["dependencies"] == []
    assert metadata(graph)[0]["gaps"] == ["nearby human context unavailable"]
    assert not graph.status()["nodes"].get("native_context_dependency")


async def test_withdrawal_removes_context_and_never_creates_missing_state(stores):
    learning, graph = stores
    episode, _, _, _ = await capture(stores)
    graph.record_native_context(episode, now=NOW)
    learning.forget(now=NOW)
    assert not graph.path.exists()
    with pytest.raises(LearningUnavailable):
        graph.record_native_context(episode, now=NOW)
    assert not graph.path.exists()


async def test_bounded_capture_eviction_and_shared_dependencies(stores):
    learning, graph = stores
    episode, _, _, _ = await capture(stores)
    for index in range(101):
        learning.observe(source(index, content=episode.source_text), now=NOW)
        current = replace(episode, source=replace(episode.source, id=BASE + index))
        graph.record_native_context(current, now=NOW)
    assert len(metadata(graph)) == 100
    assert graph.status()["nodes"]["native_context_dependency"] == 1
    assert BASE not in {data["ref"]["message_id"] for data in metadata(graph)}


async def test_old_collector_cannot_overwrite_newer_capture(stores):
    _, graph = stores
    old, _, _, _ = await capture(stores)
    new, _, _, _ = await capture(stores, now=NOW + timedelta(seconds=1))
    graph.record_native_context(new, now=NOW + timedelta(seconds=1))
    assert not graph.record_native_context(old, now=NOW + timedelta(seconds=1))
    assert metadata(graph)[0]["captured_at"] == (NOW + timedelta(seconds=1)).isoformat()


async def test_graph_storage_limit_rolls_capture_back_atomically(stores, monkeypatch):
    _, graph = stores
    episode, _, _, _ = await capture(stores)
    monkeypatch.setattr("trubot.graph.MAX_NODES", 1)
    with pytest.raises(LearningUnavailable, match="node limit"):
        graph.record_native_context(episode, now=NOW)
    assert graph.status()["nodes"] == {}
