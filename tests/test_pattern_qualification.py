"""Synthetic patterns must qualify before they can guide a character reply."""

import json
from datetime import timedelta

import pytest
from test_graph import observation
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.episode_memory import PATTERN_KINDS
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(learning)
    graph = GraphStore.initialize(learning)
    for i in range(3):
        learning.observe(
            source(
                i,
                content=f"Invented independent episode {i}",
                created_at=NOW - timedelta(days=i + 1),
            ),
            now=NOW,
        )
    refs = [{"kind": "discord", "message_id": source(i).id} for i in range(3)]
    return learning, graph, refs


def pattern(refs, kind):
    return observation(
        refs[0],
        kind=kind,
        supports=refs[:2],
        summary="SYNTHETIC_PATTERN_GUIDANCE",
        abstraction={
            "conditions": "Invited invented dessert banter.",
            "limitations": "Use sincere care in serious contexts.",
            "counterexamples": refs[2:],
        },
    )


@pytest.mark.parametrize("kind", PATTERN_KINDS)
@pytest.mark.parametrize("support_count", [1, 2])
def test_new_pattern_without_conditions_is_rejected_atomically(stores, kind, support_count):
    _learning, graph, refs = stores
    item = pattern(refs, kind)
    del item["abstraction"]
    item["supports"] = refs[:support_count]
    before = graph.status()
    for dry_run in (True, False):
        with pytest.raises(LearningUnavailable, match="conditional abstraction"):
            graph.import_observations([item], now=NOW, dry_run=dry_run)
        assert graph.status() == before


@pytest.mark.parametrize("kind", PATTERN_KINDS)
@pytest.mark.parametrize(
    "damage",
    [
        "missing",
        "empty_condition",
        "one_support",
        "shared_episode",
        "malformed",
        "duplicate_content",
    ],
)
def test_restored_unqualified_patterns_are_hidden_and_swept(stores, kind, damage):
    learning, graph, refs = stores
    graph.import_observation(pattern(refs, kind), now=NOW)
    graph.import_observation(observation(refs[0], id="literal"), now=NOW)
    memory = ContextMemory(learning)
    old_candidates = memory.candidates("dessert", guild_id=77, now=NOW)
    with graph._transaction() as (db, _):
        data = json.loads(
            db.execute("SELECT data FROM nodes WHERE id='observation:dessert'").fetchone()[0]
        )
        if damage == "missing":
            del data["abstraction"]
            # Old records may lack the newer domain field too. Row kind remains authoritative.
            del data["kind"]
        elif damage == "empty_condition":
            data["abstraction"]["conditions"] = ""
        elif damage == "one_support":
            data["supports"] = data["supports"][:1]
        elif damage == "shared_episode":
            data["supports"] = [data["supports"][0], data["supports"][0]]
        elif damage == "malformed":
            data["abstraction"] = None
        else:
            data["supports"][1]["content_hash"] = data["supports"][0]["content_hash"]
        db.execute("UPDATE nodes SET data=? WHERE id='observation:dessert'", (json.dumps(data),))
    backups = graph.path.parent / "backups"
    backups.mkdir(mode=0o700)
    backup = backups / "memory-graph-synthetic.sqlite3"
    backup.write_bytes(graph.path.read_bytes())
    backup.chmod(0o600)
    assert {
        item["id"] for item in GraphStore(learning).lookup("dessert", guild_id=77, now=NOW)
    } == {"observation:literal"}
    assert graph.describe(["observation:dessert"], now=NOW, verified_after=None) == []
    assert "SYNTHETIC_PATTERN_GUIDANCE" not in memory.render(old_candidates, now=NOW)
    assert graph.sweep(now=NOW) >= 1
    assert graph.status()["nodes"].get(kind, 0) == 0
    assert not backup.exists()


@pytest.mark.parametrize("kind", PATTERN_KINDS)
def test_qualified_legacy_pattern_and_literal_memory_remain_usable(stores, kind):
    learning, graph, refs = stores
    graph.import_observation(pattern(refs, kind), now=NOW)
    graph.import_observation(observation(refs[0], id="literal"), now=NOW)
    with graph._transaction() as (db, _):
        data = json.loads(
            db.execute("SELECT data FROM nodes WHERE id='observation:dessert'").fetchone()[0]
        )
        del data["kind"]
        db.execute("UPDATE nodes SET data=? WHERE id='observation:dessert'", (json.dumps(data),))
    items = GraphStore(learning).lookup("dessert", guild_id=77, now=NOW)
    assert {item["id"] for item in items} == {"observation:dessert", "observation:literal"}
    text = ContextMemory(learning).render(
        ContextMemory(learning).candidates("dessert", guild_id=77, now=NOW), now=NOW
    )
    assert "SYNTHETIC_PATTERN_GUIDANCE" in text and "caramel dessert" in text
