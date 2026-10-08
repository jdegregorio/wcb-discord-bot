import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest
from test_learning import AUDIT, NOW, source

from trubot.learning import LearningStore, LearningUnavailable, main


def initialized(directory: Path) -> LearningStore:
    directory.mkdir(mode=0o700, exist_ok=True)
    return LearningStore.initialize(directory / "learning.sqlite3", AUDIT, now=NOW)


def backup(store: LearningStore, path: Path) -> None:
    with sqlite3.connect(store.path) as db, sqlite3.connect(path) as copy:
        db.backup(copy)
    path.chmod(0o600)


def test_withdrawal_erases_learning_and_known_copies_but_preserves_spending(tmp_path):
    store = initialized(tmp_path)
    store.observe(source(), now=NOW)
    audit = tmp_path / "identity-audit.json"
    audit.write_text(json.dumps(AUDIT))
    audit.chmod(0o600)
    copies = tmp_path / "backups"
    copies.mkdir(mode=0o700)
    learning_copy = copies / "learning-test.sqlite3"
    backup(store, learning_copy)
    usage = tmp_path / "usage.sqlite3"
    usage.write_bytes(b"synthetic spending history")
    usage_copy = copies / "usage-test.sqlite3"
    usage_copy.write_bytes(usage.read_bytes())

    store.forget(now=NOW)

    assert store.is_withdrawn()
    assert store.withdrawal_path.stat().st_mode & 0o777 == 0o600
    assert json.loads(store.withdrawal_path.read_text()) == {
        "schema": 1,
        "withdrawn_at": NOW.isoformat(),
    }
    assert not audit.exists()
    assert not learning_copy.exists()
    assert usage.read_bytes() == usage_copy.read_bytes() == b"synthetic spending history"
    assert store.status()["identity"] == "withdrawn by operator"
    assert store.status()["messages"] == store.status()["channels"] == 0
    with sqlite3.connect(store.path) as db:
        assert db.execute("SELECT COUNT(*) FROM identity").fetchone()[0] == 0
    # Explicit operator retry completes safely and preserves the original guard.
    marker = store.withdrawal_path.read_bytes()
    store.forget(now=NOW)
    assert store.withdrawal_path.read_bytes() == marker


def test_stale_backup_and_initialization_cannot_resurrect_withdrawn_identity(tmp_path):
    store = initialized(tmp_path)
    store.observe(source(), now=NOW)
    saved = tmp_path / "saved.sqlite3"
    backup(store, saved)
    store.forget(now=NOW)
    store.path.write_bytes(saved.read_bytes())
    reopened = LearningStore(store.path)
    assert reopened.is_withdrawn()
    with pytest.raises(LearningUnavailable):
        reopened.identity()
    with pytest.raises(LearningUnavailable):
        reopened.observe(source(1), now=NOW)
    with pytest.raises(LearningUnavailable):
        reopened.commit_batch(10, [source(1)], now=NOW)
    store.path.unlink()
    with pytest.raises(LearningUnavailable):
        LearningStore.initialize(store.path, AUDIT, now=NOW)
    assert not store.path.exists()


def test_cleanup_failure_leaves_guard_active_and_retry_completes(tmp_path):
    store = initialized(tmp_path)
    store.observe(source(), now=NOW)
    with (
        patch("trubot.learning.os.fsync", side_effect=OSError("disk failure")),
        pytest.raises(LearningUnavailable),
    ):
        store.forget(now=NOW)
    assert store.is_withdrawn()
    # The failed transaction retained content, but every learning access is blocked.
    with pytest.raises(LearningUnavailable):
        store.identity()
    store.forget(now=NOW)
    assert store.status()["messages"] == 0


@pytest.mark.parametrize(
    "copy_kind", ["public", "symlink", "directory", "backup_directory", "backup_file"]
)
def test_unsafe_cleanup_targets_are_preserved_while_learning_stays_blocked(tmp_path, copy_kind):
    store = initialized(tmp_path)
    outside = tmp_path / "unrelated.txt"
    outside.write_text("preserve")
    audit = tmp_path / "identity-audit.json"
    if copy_kind == "public":
        audit.write_text("sensitive audit")
        audit.chmod(0o644)
    elif copy_kind == "symlink":
        audit.symlink_to(outside)
    elif copy_kind == "directory":
        audit.mkdir(mode=0o700)
    elif copy_kind == "backup_directory":
        (tmp_path / "backups").mkdir(mode=0o755)
    else:
        (tmp_path / "backups").write_text("invalid directory")
        (tmp_path / "backups").chmod(0o600)
    with pytest.raises(LearningUnavailable):
        store.forget(now=NOW)
    assert store.is_withdrawn()
    assert outside.read_text() == "preserve"


def test_marker_symlink_blocks_initialization_and_forget_never_follows_it(tmp_path):
    store = initialized(tmp_path)
    outside = tmp_path / "private-marker"
    store.withdrawal_path.symlink_to(outside)
    assert store.is_withdrawn()
    with pytest.raises(LearningUnavailable):
        store.identity()
    with pytest.raises(LearningUnavailable):
        store.forget(now=NOW)
    assert not outside.exists()


def test_operator_cli_forget_and_status_are_content_free(tmp_path, monkeypatch, capsys):
    store = initialized(tmp_path)
    store.observe(source(), now=NOW)
    monkeypatch.setattr("sys.argv", ["trubot-learning", "forget", "--path", str(store.path)])
    main()
    output = capsys.readouterr().out
    assert json.loads(output)["identity"] == "withdrawn by operator"
    assert "synthetic-person" not in output
    assert "Sox enthusiasm" not in output
    monkeypatch.setattr("sys.argv", ["trubot-learning", "status", "--path", str(store.path)])
    main()
    assert json.loads(capsys.readouterr().out)["messages"] == 0
