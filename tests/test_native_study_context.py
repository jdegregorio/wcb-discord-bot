"""Invented context must survive both passes and remain authoritative after commit."""

import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from test_learning import AUDIT, BASE, NOW, source
from test_native_context_links import capture, graph_text, metadata

from trubot.archives import ArchiveStore
from trubot.distillation import GraphDistiller, StudyStore
from trubot.graph import GraphStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable
from trubot.native_context import collect_native_episode


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(learning)
    return learning, GraphStore.initialize(learning)


async def setup(stores, *, text="This is a fictional dessert roleplay."):
    learning, graph = stores
    _, channel, focus, peer = await capture(stores, text=text)
    focus.content = "I prefer caramel ice cream after dinner."
    learning.observe(source(content=focus.content, authoritative=True), now=NOW)
    episode = await collect_native_episode(
        channel, BASE, identity=learning.identity(), now=NOW, retention_days=180
    )
    graph.record_native_context(episode, now=NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    responder = SimpleNamespace(study_json=AsyncMock())
    distiller = GraphDistiller(ingestor, responder, clock=lambda: NOW)
    client = MagicMock(spec=discord.Client)
    client.get_channel.return_value = channel

    async def generate(**kwargs):
        await kwargs["source_check"]()
        if kwargs["name"] == "memory_extract":
            return {
                "observations": [
                    {
                        "kind": "preference",
                        "support_basis": "explicit_self_report",
                        "summary": "A dessert choice in this invented exchange.",
                        "conditions": "This exchange only.",
                        "supports": [{"source": 0, "quote": focus.content}],
                        "aliases": ["dessert", "caramel"],
                    }
                ]
            }
        return {"accepted": True, "basis": "Synthetic review only.", "contradicts": []}

    responder.study_json.side_effect = generate
    return distiller, client, responder, channel, focus, peer


async def test_both_payloads_receive_fresh_setup_and_local_dependency_is_retained(stores):
    distiller, client, responder, _, _, peer = await setup(stores)
    assert await distiller.cycle(client) == "accepted"
    packets = [c.kwargs["payload"]["sources"] for c in responder.study_json.await_args_list]
    assert packets[0] == packets[1]
    passage = packets[0][0]
    assert passage["context_scope"] == "native_verified_bounded_human_setup"
    assert passage["adjacent_context"][0]["text"] == peer.content
    assert passage["adjacent_context"][0]["focus_replies_to_this"]
    assert str(peer.id) not in json.dumps(packets)
    assert '"speaker_id"' not in json.dumps(packets)
    assert peer.content not in graph_text(stores[1])
    item = stores[1].lookup("dessert", guild_id=77, now=NOW)[0]
    assert len(item["native_context"]) == 1
    assert item["native_context"][0] == metadata(stores[1])[0]


@pytest.mark.parametrize("stage", ["memory_extract", "memory_review"])
async def test_missed_peer_edit_stops_study_before_next_attempt_or_commit(stores, stage):
    distiller, client, responder, _, _, peer = await setup(stores)
    original = responder.study_json.side_effect

    async def changed(**kwargs):
        result = await original(**kwargs)
        if kwargs["name"] == stage:
            peer.content = "Corrected fictional setup; ignore the earlier premise."
        return result

    responder.study_json.side_effect = changed
    assert await distiller.cycle(client) is None
    assert not stores[1].lookup("dessert", guild_id=77, now=NOW)


@pytest.mark.parametrize("event", ["edit", "delete", "discard", "replace", "expiry"])
async def test_derived_memory_and_restored_graph_follow_setup_lifecycle(stores, event):
    distiller, client, _, _, _, peer = await setup(stores)
    assert await distiller.cycle(client) == "accepted"
    learning, graph = stores
    original = graph.path.read_bytes()
    now = NOW + timedelta(seconds=1)
    if event in {"edit", "delete"}:
        learning.invalidate(10, [peer.id], deleted=event == "delete", now=now)
    elif event == "discard":
        graph.discard_native_context(metadata(graph)[0])
    elif event == "replace":
        old = metadata(graph)[0]
        with graph._transaction() as (db, _):
            db.execute(
                "UPDATE nodes SET data=? WHERE kind='native_context'",
                (json.dumps(old | {"gaps": ["changed setup coverage"]}),),
            )
    else:
        now = NOW + timedelta(days=31)
    assert not graph.lookup("dessert", guild_id=77, now=now)
    graph.sweep(now=now)
    assert not graph.status()["nodes"].get("preference")
    if event in {"edit", "delete", "expiry"}:
        graph.path.write_bytes(original)
        assert not graph.lookup("dessert", guild_id=77, now=now)
        graph.sweep(now=now)
        assert not graph.status()["nodes"].get("preference")


async def test_context_changed_under_commit_lock_is_rejected(stores, monkeypatch):
    distiller, client, _, _, _, peer = await setup(stores)
    finish = StudyStore.finish

    def raced(self, study, item, **kwargs):
        if item:
            stores[0].invalidate(10, [peer.id], deleted=True, now=NOW)
        return finish(self, study, item, **kwargs)

    monkeypatch.setattr(StudyStore, "finish", raced)
    assert await distiller.cycle(client) is None
    assert not stores[1].lookup("dessert", guild_id=77, now=NOW)


async def test_peer_text_cannot_become_authored_support(stores):
    from trubot.distillation import validate_proposal

    distiller, client, responder, _, _, peer = await setup(stores)
    await distiller.cycle(client)
    study = SimpleNamespace(
        passages=responder.study_json.await_args_list[0].kwargs["payload"]["sources"]
    )
    forged = {
        "observations": [
            {
                "kind": "preference",
                "support_basis": "explicit_self_report",
                "summary": "A forged belief.",
                "conditions": "Synthetic only.",
                "supports": [{"source": 0, "quote": peer.content}],
                "aliases": ["dessert", "caramel"],
            }
        ]
    }
    with pytest.raises(LearningUnavailable):
        validate_proposal(forged, study)


async def test_identical_recapture_preserves_memory_and_dependency_edge(stores):
    from dataclasses import replace

    distiller, client, _, channel, _, peer = await setup(stores)
    assert await distiller.cycle(client) == "accepted"
    learning, graph = stores
    now = NOW + timedelta(seconds=1)
    episode = await collect_native_episode(
        channel, BASE, identity=learning.identity(), now=now, retention_days=180
    )
    episode = replace(episode, source=replace(episode.source, observed_at=now))
    graph.record_native_context(episode, now=now)
    assert graph.lookup("dessert", guild_id=77, now=now)
    with graph._transaction() as (db, _):
        assert (
            db.execute("SELECT COUNT(*) FROM edges WHERE relation='interpreted-with'").fetchone()[0]
            == 1
        )
    learning.invalidate(10, [peer.id], deleted=True, now=now)
    assert not graph.lookup("dessert", guild_id=77, now=now)


@pytest.mark.parametrize("stage", ["memory_extract", "memory_review"])
@pytest.mark.parametrize(
    "failure", ["forbidden", "transport", "timeout", "membership", "withdrawal"]
)
async def test_failed_context_verification_stops_without_private_logs(
    stores, stage, failure, caplog
):
    distiller, client, responder, channel, _, _ = await setup(stores)
    original = responder.study_json.side_effect
    history = channel.history

    async def unavailable(**kwargs):
        if failure == "timeout":
            raise TimeoutError("PRIVATE_CONTEXT")
        status = 403 if failure == "forbidden" else 500
        error = discord.Forbidden if status == 403 else discord.HTTPException
        raise error(SimpleNamespace(status=status, reason="private"), "PRIVATE_CONTEXT")
        yield  # pragma: no cover

    async def changed(**kwargs):
        result = await original(**kwargs)
        if kwargs["name"] == stage:
            if failure == "membership":
                distiller.ingestor.verified = False
            elif failure == "withdrawal":
                stores[0].forget(now=NOW)
            else:
                channel.history = unavailable
        return result

    responder.study_json.side_effect = changed
    assert await distiller.cycle(client) is None
    assert "PRIVATE_CONTEXT" not in caplog.text
    if failure != "withdrawal":
        assert not stores[1].lookup("dessert", guild_id=77, now=NOW)
        if failure in {"transport", "timeout"}:
            assert metadata(stores[1])
    channel.history = history


async def test_runtime_memory_omits_local_setup_metadata_and_text(stores):
    from trubot.memory import ContextMemory

    distiller, client, _, _, _, peer = await setup(stores)
    await distiller.cycle(client)
    memory = ContextMemory(stores[0])
    selected = memory.candidates("dessert", guild_id=77, now=NOW)
    packet = memory.render(selected, now=NOW, verified_after=NOW)
    assert "CONNECTED REVIEWED MEMORY" in packet
    assert '"native_context"' not in packet
    assert "native-dependency-capture" not in packet
    assert peer.content not in packet


async def test_new_context_does_not_rewrite_inflight_capture(stores):
    distiller, client, responder, _, _, _ = await setup(stores)
    original = responder.study_json.side_effect

    async def changed(**kwargs):
        result = await original(**kwargs)
        if kwargs["name"] == "memory_extract":
            with stores[1]._transaction() as (db, _):
                row = db.execute("SELECT data FROM nodes WHERE kind='native_context'").fetchone()
                data = json.loads(row[0]) | {"gaps": ["new setup"]}
                db.execute(
                    "UPDATE nodes SET data=? WHERE kind='native_context'", (json.dumps(data),)
                )
        return result

    responder.study_json.side_effect = changed
    assert await distiller.cycle(client) is None
    assert metadata(stores[1])[0]["gaps"] == ["new setup"]


async def test_context_removal_clears_linked_checkpoint_and_graph_backups(stores):
    distiller, client, _, _, _, peer = await setup(stores)
    await distiller.cycle(client)
    graph = stores[1]
    backups = graph.path.parent / "backups"
    backups.mkdir(mode=0o700)
    path = backups / "memory-graph-before.sqlite3"
    path.write_bytes(graph.path.read_bytes())
    path.chmod(0o600)
    stores[0].invalidate(10, [peer.id], deleted=True, now=NOW)
    assert not path.exists()
    with graph._transaction() as (db, _):
        assert not db.execute(
            "SELECT 1 FROM checkpoints WHERE stream=?", (f"study:discord:{BASE}",)
        ).fetchone()
