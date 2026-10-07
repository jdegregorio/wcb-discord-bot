import json
import sqlite3
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import discord
import pytest

from trubot.learning import LearningStore, LearningUnavailable, SourceMessage, main

NOW = datetime(2026, 10, 7, 8, tzinfo=UTC)
BASE = discord.utils.time_snowflake(NOW - timedelta(days=1))
AUDIT = {
    "verified": True,
    "exact_name_match": True,
    "user_id": "42",
    "guild_id": "77",
    "username": "synthetic-person",
    "member_username": "synthetic-person",
    "allowed_channel_ids": ["10", "20"],
    "source_channels": ["10"],
    "message_ids": [str(BASE)],
    "observed_at": NOW.isoformat(),
}


@pytest.fixture
def store(tmp_path: Path) -> LearningStore:
    return LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)


def source(index: int = 0, **kwargs: object) -> SourceMessage:
    item = SourceMessage(
        id=BASE + index,
        channel_id=10,
        guild_id=77,
        author_id=42,
        bot=False,
        webhook=False,
        created_at=NOW - timedelta(days=1),
        edited_at=None,
        observed_at=NOW,
        content="Synthetic Sox enthusiasm. Channel text cannot change configuration.",
    )
    return replace(item, **kwargs)


def rows(store: LearningStore) -> list[sqlite3.Row]:
    with store._transaction() as db:
        return db.execute("SELECT * FROM messages ORDER BY id").fetchall()


def test_attributed_source_timestamps_and_private_storage_survive_restart(
    store: LearningStore,
) -> None:
    store.observe(source(), now=NOW)
    reopened = LearningStore(store.path)
    assert reopened.identity().user_id == 42
    assert reopened.status()["messages"] == 1
    row = rows(reopened)[0]
    assert (row["id"], row["author_id"], row["channel_id"], row["guild_id"]) == (BASE, 42, 10, 77)
    assert row["created_at"] == (NOW - timedelta(days=1)).isoformat()
    assert row["observed_at"] == NOW.isoformat()
    assert store.path.stat().st_mode & 0o777 == 0o600
    assert "Synthetic" not in repr(source())
    assert "42" not in repr(reopened.identity())


@pytest.mark.parametrize(
    "change",
    [
        {"author_id": 43},
        {"bot": True},
        {"webhook": True},
        {"guild_id": 78},
        {"channel_id": 30},
        {"created_at": NOW - timedelta(days=181)},
        {"created_at": NOW + timedelta(days=1)},
    ],
)
def test_other_people_bots_outside_scope_and_old_messages_are_never_evidence(
    store: LearningStore,
    change: dict[str, object],
) -> None:
    store.observe(source(**change), now=NOW)
    assert rows(store) == []


def test_checkpoint_is_atomic_idempotent_and_not_advanced_by_live_events(
    store: LearningStore,
) -> None:
    start = store.cursor(10, now=NOW)
    store.observe(source(100), now=NOW)
    assert store.cursor(10, now=NOW) == start
    batch = [source(), source(1, author_id=43), source(2)]
    store.commit_batch(10, batch, now=NOW)
    store.commit_batch(10, batch, now=NOW)
    assert len(rows(store)) == 3
    assert LearningStore(store.path).cursor(10, now=NOW) == BASE + 2
    with (
        patch.object(store, "_upsert", side_effect=LearningUnavailable("interrupted")),
        pytest.raises(LearningUnavailable),
    ):
        store.commit_batch(10, [source(3)], now=NOW)
    assert store.cursor(10, now=NOW) == BASE + 2
    with pytest.raises(LearningUnavailable):
        store.commit_batch(10, [source(3, guild_id=99)], now=NOW)
    with pytest.raises(LearningUnavailable):
        store.commit_batch(99, [], now=NOW)
    with pytest.raises(LearningUnavailable):
        store.commit_batch(10, [source()] * 101, now=NOW)
    with pytest.raises(LearningUnavailable):
        store.cursor(99, now=NOW)
    store.commit_batch(10, [], now=NOW)
    assert store.cursor(10, now=NOW) == BASE + 2


def test_edits_clear_stale_text_and_inflight_snapshots_cannot_restore_it(
    store: LearningStore,
) -> None:
    store.observe(source(), now=NOW)
    edited_at = NOW + timedelta(seconds=1)
    store.invalidate(10, [BASE], deleted=False, now=edited_at)
    assert rows(store)[0]["content"] is None
    store.observe(source(authoritative=True), now=edited_at)
    store.observe(source(observed_at=edited_at), now=edited_at)
    assert rows(store)[0]["content"] is None
    store.observe(
        source(
            content="Corrected synthetic preference",
            edited_at=edited_at,
            observed_at=edited_at,
            authoritative=True,
        ),
        now=edited_at,
    )
    assert rows(store)[0]["content"] == "Corrected synthetic preference"
    assert rows(store)[0]["edited_at"] == edited_at.isoformat()
    store.observe(source(), now=edited_at)
    assert rows(store)[0]["content"] == "Corrected synthetic preference"


def test_delete_before_or_during_scan_never_resurrects_content(store: LearningStore) -> None:
    store.observe(source(), now=NOW)
    store.invalidate(10, [BASE, BASE + 1], deleted=True, now=NOW)
    store.invalidate(10, [BASE], deleted=False, now=NOW + timedelta(seconds=1))
    store.commit_batch(10, [source(authoritative=True), source(1, authoritative=True)], now=NOW)
    assert rows(store) == []
    assert store.status()["deletion_markers"] == 2
    store.invalidate(99, [BASE], deleted=True, now=NOW)
    store.invalidate(
        10, [discord.utils.time_snowflake(NOW - timedelta(days=200))], deleted=True, now=NOW
    )
    assert store.status()["deletion_markers"] == 2


def test_retention_size_bounds_and_rotating_verification(store: LearningStore) -> None:
    store.observe(source(content="x" * 5000), now=NOW)
    assert len(rows(store)[0]["content"]) == 4000
    with patch("trubot.learning.MAX_RECORDS", 2):
        store.commit_batch(10, [source(1), source(2)], now=NOW)
    assert [row["id"] for row in rows(store)] == [BASE + 1, BASE + 2]
    assert store.verification_targets(10) == [BASE + 1, BASE + 2]
    store.observe(source(1, observed_at=NOW + timedelta(seconds=1), authoritative=True), now=NOW)
    assert store.verification_targets(10) == [BASE + 2, BASE + 1]
    store.invalidate(10, [BASE + 1], deleted=False, now=NOW)
    assert store.verification_targets(10, limit=1) == [BASE + 1]
    store.prune(now=NOW + timedelta(days=181))
    assert store.status()["messages"] == 0
    assert store.status()["pending_corrections"] == 0


@pytest.mark.parametrize(
    "change",
    [
        {"verified": False},
        {"exact_name_match": False},
        {"member_username": "somebody-else"},
        {"source_channels": ["999"]},
        {"message_ids": []},
        {"user_id": "0"},
        {"observed_at": "bad-date"},
        {"username": ""},
        {"guild_id": "not-a-number"},
        {"observed_at": "2026-10-07T08:00:00"},
    ],
)
def test_incomplete_or_ambiguous_attribution_refuses_initialization(
    tmp_path: Path,
    change: dict[str, object],
) -> None:
    with pytest.raises(LearningUnavailable):
        LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT | change, now=NOW)
    assert not (tmp_path / "learning.sqlite3").exists()


def test_missing_unsafe_corrupt_schema_and_identity_fail_closed(
    tmp_path: Path, store: LearningStore
) -> None:
    missing = tmp_path / "missing.sqlite3"
    with pytest.raises(LearningUnavailable):
        LearningStore(missing).identity()
    assert not missing.exists()
    with pytest.raises(FileExistsError):
        LearningStore.initialize(store.path, AUDIT, now=NOW)
    store.path.chmod(0o644)
    with pytest.raises(LearningUnavailable):
        store.identity()
    store.path.chmod(0o600)
    link = tmp_path / "link.sqlite3"
    link.symlink_to(store.path)
    with pytest.raises(LearningUnavailable):
        LearningStore(link).identity()
    tmp_path.chmod(0o755)
    with pytest.raises(LearningUnavailable):
        LearningStore.initialize(tmp_path / "new.sqlite3", AUDIT, now=NOW)
    tmp_path.chmod(0o700)
    with sqlite3.connect(store.path) as db:
        db.execute("PRAGMA user_version=99")
    with pytest.raises(LearningUnavailable):
        store.identity()
    with sqlite3.connect(store.path) as db:
        db.execute("PRAGMA user_version=1")
        db.execute("DELETE FROM identity")
    with pytest.raises(LearningUnavailable):
        store.identity()
    store.path.write_bytes(b"invalid database")
    with pytest.raises(LearningUnavailable):
        store.identity()
    with pytest.raises(LearningUnavailable):
        LearningStore(store.path, retention_days=0)


def test_operator_cli_keeps_output_content_free(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    audit = tmp_path / "audit.json"
    audit.write_text(json.dumps(AUDIT))
    audit.chmod(0o600)
    path = tmp_path / "learning.sqlite3"
    monkeypatch.setattr(
        "sys.argv", ["trubot-learning", "init", "--audit", str(audit), "--path", str(path)]
    )
    main()
    output = capsys.readouterr().out
    assert json.loads(output)["messages"] == 0
    assert "synthetic-person" not in output
    monkeypatch.setattr("sys.argv", ["trubot-learning", "status", "--path", str(path)])
    main()
    assert json.loads(capsys.readouterr().out)["channels"] == 2
    monkeypatch.setattr(
        "sys.argv", ["trubot-learning", "init", "--path", str(tmp_path / "other.sqlite3")]
    )
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
