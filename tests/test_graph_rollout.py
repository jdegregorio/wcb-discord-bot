"""Reviewed memory rollouts use invented evidence and the real administration path."""

import json
from datetime import datetime
from unittest.mock import patch

import pytest
from test_graph import observation
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore, main
from trubot.learning import LearningStore, LearningUnavailable


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def prepare(stores):
    learning, _, graph = stores
    learning.observe(source(content="I order salted caramel after dinner."), now=NOW)
    ref = {"kind": "discord", "message_id": source().id}
    graph.import_observation(observation(ref), now=NOW)
    backups = learning.path.parent / "backups"
    backups.mkdir(mode=0o700)
    backup = backups / "memory-graph-before.sqlite3"
    backup.write_bytes(graph.path.read_bytes())
    backup.chmod(0o600)
    return learning, graph, ref, backup


def rows(graph):
    with graph._transaction() as (db, _):
        return {
            name: [tuple(row) for row in db.execute(query)]
            for name, query in {
                "nodes": "SELECT * FROM nodes ORDER BY 1,2",
                "edges": "SELECT * FROM edges ORDER BY 1,2",
                "checkpoints": "SELECT * FROM checkpoints ORDER BY 1,2",
            }.items()
        }


@pytest.mark.parametrize("failure", ["provenance", "source", "contradiction", "duplicates"])
def test_rejected_later_item_restores_existing_beliefs_edges_and_backups(stores, failure):
    _, graph, ref, backup = prepare(stores)
    before, saved = rows(graph), backup.read_bytes()
    replacement = observation(ref, summary="A changed tentative dessert description.")
    invalid = observation(ref, id="new", reviewed_by_operator=False)
    if failure == "source":
        invalid = observation({"kind": "discord", "message_id": 123}, id="new")
    elif failure == "contradiction":
        invalid = observation(ref, id="new", contradicts=["unavailable"])
    elif failure == "duplicates":
        invalid = observation(ref)
    with pytest.raises(LearningUnavailable):
        graph.import_observations([replacement, invalid], now=NOW)
    assert rows(GraphStore(stores[0])) == before
    assert backup.read_bytes() == saved


@pytest.mark.parametrize("items", [[], [{}], [{"id": ""}], [{"id": 1}], "invalid", [{}] * 101])
def test_invalid_rollout_envelope_does_not_change_state(stores, items):
    _, graph, _, backup = prepare(stores)
    before = rows(graph)
    with pytest.raises(LearningUnavailable):
        graph.import_observations(items, now=NOW)
    assert rows(graph) == before and backup.exists()


def test_complete_batch_commits_replacement_and_conflict_and_removes_old_backup(stores):
    learning, graph, ref, backup = prepare(stores)
    graph.import_observations(
        [
            observation(ref, summary="A revised qualified dessert description."),
            observation(ref, id="conflict", contradicts=["dessert"]),
        ],
        now=NOW,
    )
    observations = GraphStore(learning).lookup("dessert", guild_id=77, now=NOW)
    assert len(observations) == 2
    assert all(item["status"] == "contested" for item in observations)
    assert not backup.exists()


def test_actual_cli_rejected_batch_is_atomic(stores, monkeypatch, capsys):
    learning, graph, ref, backup = prepare(stores)
    before = rows(graph)
    manifest = learning.path.parent / "reviewed.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": 1,
                "observations": [
                    observation(ref, summary="Replacement that must roll back."),
                    observation(ref, id="new", reviewed_by_operator=False),
                ],
            }
        )
    )
    manifest.chmod(0o600)
    monkeypatch.setattr(
        "sys.argv",
        [
            "trubot-graph",
            "import",
            "--learning-path",
            str(learning.path),
            "--manifest",
            str(manifest),
        ],
    )
    with patch("trubot.graph.datetime") as clock:
        clock.now.return_value = NOW
        clock.fromisoformat.side_effect = datetime.fromisoformat
        with pytest.raises(SystemExit) as error:
            main()
    assert error.value.code == 2
    assert rows(graph) == before and backup.exists()
    output = capsys.readouterr()
    assert "Replacement" not in output.err and output.out == ""


def test_withdrawal_blocks_entire_rollout(stores):
    learning, graph, ref, _ = prepare(stores)
    learning.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        graph.import_observations([observation(ref), observation(ref, id="new")], now=NOW)
    assert learning.is_withdrawn() and not graph.path.exists()
