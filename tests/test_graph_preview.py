"""Reviewed rollout previews validate real writes without changing private state."""

import json
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from test_graph import observation
from test_graph_rollout import prepare, rows
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore, main
from trubot.learning import LearningStore, LearningUnavailable


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


@pytest.mark.parametrize("change", ["replacement", "conflict", "new"])
def test_valid_preview_preserves_graph_bytes_beliefs_and_backups(stores, change):
    learning, graph, ref, backup = prepare(stores)
    before, saved, graph_bytes = rows(graph), backup.read_bytes(), graph.path.read_bytes()
    item = observation(ref, summary="A revised qualified description.")
    if change == "new":
        item["id"] = "new"
    elif change == "conflict":
        item |= {"id": "conflict", "contradicts": ["dessert"]}
    graph.import_observations([item], now=NOW, dry_run=True)
    assert rows(GraphStore(learning)) == before
    assert graph.path.read_bytes() == graph_bytes
    assert backup.read_bytes() == saved
    graph.import_observations([item], now=NOW)
    assert rows(graph) != before and not backup.exists()


def test_preview_checks_later_failure_and_rechecks_sources_at_commit(stores):
    learning, graph, ref, backup = prepare(stores)
    before = rows(graph)
    item = observation(ref, summary="A revised qualified description.")
    with pytest.raises(LearningUnavailable):
        graph.import_observations(
            [item, observation(ref, id="invalid", contradicts=["missing"])],
            now=NOW,
            dry_run=True,
        )
    assert rows(graph) == before and backup.exists()
    graph.import_observations([item], now=NOW, dry_run=True)
    learning.invalidate(10, [ref["message_id"]], deleted=True, now=NOW)
    with pytest.raises(LearningUnavailable):
        graph.import_observations([item], now=NOW)
    assert not graph.lookup("dessert", guild_id=77, now=NOW)


def test_abstract_preview_rolls_back_support_and_contrary_relationships(stores):
    learning, _, graph = stores
    refs = []
    for i in range(3):
        message = source(i, content=f"Invented episode {i}", created_at=NOW - timedelta(days=i))
        learning.observe(message, now=NOW)
        refs.append({"kind": "discord", "message_id": message.id})
    item = observation(
        refs[0],
        kind="value",
        supports=refs[:2],
        abstraction={
            "conditions": "An invited invented decision.",
            "limitations": "Not a universal habit.",
            "counterexamples": refs[2:],
        },
        expires_at=(NOW + timedelta(days=30)).isoformat(),
    )
    before, saved = rows(graph), graph.path.read_bytes()
    graph.import_observations([item], now=NOW, dry_run=True)
    assert rows(graph) == before and graph.path.read_bytes() == saved
    assert not graph.lookup("dessert", guild_id=77, now=NOW)
    graph.import_observations([item], now=NOW)
    assert len(graph.lookup("dessert", guild_id=77, now=NOW)) == 1


@pytest.mark.parametrize("withdrawn", [False, True])
def test_preview_retains_provenance_and_withdrawal_gate(stores, withdrawn):
    learning, graph, ref, _ = prepare(stores)
    if withdrawn:
        learning.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        graph.import_observations(
            [observation(ref, reviewed_by_operator=False)], now=NOW, dry_run=True
        )


def test_actual_cli_preview_reports_only_content_free_counts(stores, monkeypatch, capsys):
    learning, graph, ref, backup = prepare(stores)
    before = rows(graph)
    manifest = learning.path.parent / "reviewed.json"
    manifest.write_text(json.dumps({"schema": 1, "observations": [observation(ref)]}))
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
            "--dry-run",
        ],
    )
    with patch("trubot.graph.datetime") as clock:
        clock.now.return_value = NOW
        clock.fromisoformat.side_effect = datetime.fromisoformat
        main()
    output = capsys.readouterr()
    assert json.loads(output.out)["batch"] == {"validated": 1, "committed": 0}
    assert "caramel" not in output.out and not output.err
    assert rows(graph) == before and backup.exists()


@pytest.mark.parametrize("command", ["populate", "status", "remove", "sweep", "init"])
def test_cli_refuses_misleading_preview_for_other_commands(command, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["trubot-graph", command, "--dry-run"])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    assert "only applies to import" in capsys.readouterr().err
