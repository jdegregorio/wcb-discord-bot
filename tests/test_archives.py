import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest
from test_learning import AUDIT, NOW

from trubot.archives import ArchiveStore, main, parse_slack_export
from trubot.learning import LearningStore, LearningUnavailable

RAW = b"""You created this channel on July 18th, 2017.

league.peer
  9:00 AM
Our bench has ten slots.

legacy.target
  9:01 AM
Perfect, just enough room for all my quarterbacks.
9:02
This is a synthetic continuation.
:laughing:
2

1 reply
2 years agoView thread

Slackbot
  9:02 AM
legacy.target likes this team

legacy.target
  9:04 AM
replied to a thread:
A peer's quote, not the target's authored words.
Potential response with ambiguous boundary

legacy.target
  9:06 AM
https://example.test/story
NewsNews
Copied preview is not the target's opinion.

legacy.target
  9:07 AM
joined #general along with 3 others.
"""


@pytest.fixture
def corpus(tmp_path: Path) -> ArchiveStore:
    return ArchiveStore.initialize(
        LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    )


def ingest(corpus: ArchiveStore, **changes):
    options = dict(
        raw=RAW,
        channel="general",
        target_alias="legacy.target",
        alias_basis="Operator-provided synthetic alias.",
        origin={"kind": "user_attachment", "filename": "synthetic.txt"},
        now=NOW,
    )
    options.update(changes)
    return corpus.import_document(**options)


def test_parser_separates_voice_from_context_bots_system_quotes_and_previews():
    messages = parse_slack_export(RAW, target_alias="legacy.target")
    assert len(messages) == 6
    assert [m.target for m in messages] == [False, True, False, True, True, False]
    assert [m.voice_eligible for m in messages] == [False, True, False, False, False, False]
    assert messages[2].kind == "bot"
    assert messages[-1].kind == "system"
    assert "9:02" not in messages[1].content
    assert ":laughing:" not in messages[1].content
    assert "View thread" not in messages[1].content
    assert "continuation" in messages[1].content
    assert "calendar_date_unknown" in messages[0].flags
    assert "thread_quote_ambiguous" in messages[3].flags
    assert "link_preview_ambiguous" in messages[4].flags
    assert "Perfect" not in repr(messages[1])
    assert messages[1].start_line < messages[1].end_line < messages[2].start_line
    # Similar names and mentions cannot set identity or target attribution.
    assert not any(m.target for m in parse_slack_export(RAW, target_alias="legacy"))


@pytest.mark.parametrize(
    "raw,alias", [(b"", "x"), (b"not an export", "x"), (b"\xff", "x"), (RAW, "")]
)
def test_unparseable_or_unattributed_input_is_rejected(raw, alias):
    with pytest.raises(LearningUnavailable):
        parse_slack_export(raw, target_alias=alias)
    with patch("trubot.archives.MAX_SOURCE_BYTES", 5), pytest.raises(LearningUnavailable):
        parse_slack_export(RAW, target_alias="x")


def test_lossless_idempotent_import_preserves_origins_and_neighbor_context(corpus):
    assert ingest(corpus)["result"] == "imported"
    assert ingest(corpus)["result"] == "duplicate"
    assert (
        ingest(corpus, origin={"kind": "discord_attachment", "message_id": "synthetic"})["result"]
        == "duplicate"
    )
    reopened = ArchiveStore(LearningStore(corpus.learning.path))
    assert reopened.status() == dict(
        schema=1,
        visual_episodes=0,
        image_assets=0,
        image_bytes=0,
        documents=1,
        origins=2,
        blocks=6,
        target_blocks=3,
        voice_eligible_blocks=1,
        suppressed_documents=0,
    )
    with corpus._transaction() as db:
        document = db.execute("SELECT * FROM documents").fetchone()
        assert document["raw"] == RAW
        assert document["imported_at"] == NOW.isoformat()
        digest = document["digest"]
    context = reopened.context(digest, 1, radius=1)
    assert [m["kind"] for m in context] == ["message", "message", "bot"]
    assert [m["target"] for m in context] == [0, 1, 0]
    assert context[1]["display_time"] == "9:01 AM"
    assert "created_at" not in context[1]
    assert reopened.context(digest, 999) == []
    assert corpus.path.stat().st_mode & 0o777 == 0o600
    assert "Perfect" not in json.dumps(corpus.status())
    with pytest.raises(LearningUnavailable):
        corpus.context(digest, 1, radius=11)


@pytest.mark.parametrize(
    "change",
    [
        dict(channel="other"),
        dict(target_alias="other"),
        dict(alias_basis="other"),
        dict(channel=""),
        dict(alias_basis=""),
        dict(origin={}),
    ],
)
def test_conflicting_attribution_or_missing_provenance_fails_closed(corpus, change):
    ingest(corpus)
    with pytest.raises(LearningUnavailable):
        ingest(corpus, **change)
    assert corpus.status()["documents"] == 1


def test_atomic_interruption_does_not_leave_partial_messages(corpus):
    with (
        patch("trubot.archives._time", side_effect=ValueError("interrupted")),
        pytest.raises(LearningUnavailable),
    ):
        ingest(corpus)
    assert corpus.status()["documents"] == 0
    assert corpus.status()["blocks"] == 0


def test_operator_correction_removes_raw_messages_and_backups_and_blocks_reimport(corpus):
    ingest(corpus)
    with corpus._transaction() as db:
        digest = db.execute("SELECT digest FROM documents").fetchone()[0]
    backups = corpus.path.parent / "backups"
    backups.mkdir(mode=0o700)
    copy = backups / "archives-test.sqlite3"
    copy.write_bytes(corpus.path.read_bytes())
    copy.chmod(0o600)
    usage = backups / "usage-test.sqlite3"
    usage.write_bytes(b"preserve")
    corpus.remove_document(digest, now=NOW)
    assert (
        corpus.status()["documents"] == corpus.status()["blocks"] == corpus.status()["origins"] == 0
    )
    assert corpus.status()["suppressed_documents"] == 1
    assert not copy.exists()
    assert usage.read_bytes() == b"preserve"
    with pytest.raises(LearningUnavailable):
        ingest(corpus)


def test_global_withdrawal_covers_historical_state_and_stale_restoration(corpus):
    ingest(corpus)
    saved = corpus.path.read_bytes()
    backups = corpus.path.parent / "backups"
    backups.mkdir(mode=0o700)
    copy = backups / "archives-test.sqlite3"
    copy.write_bytes(saved)
    copy.chmod(0o600)
    corpus.learning.forget(now=NOW)
    assert not corpus.path.exists()
    assert not copy.exists()
    corpus.path.write_bytes(saved)
    corpus.path.chmod(0o600)
    with pytest.raises(LearningUnavailable):
        corpus.status()
    with pytest.raises(LearningUnavailable):
        ingest(corpus)
    with pytest.raises(LearningUnavailable):
        ArchiveStore.initialize(corpus.learning)
    corpus.learning.forget(now=NOW)
    assert not corpus.path.exists()


def test_unsafe_missing_corrupt_and_unsupported_archive_state(corpus):
    with pytest.raises(LearningUnavailable):
        ArchiveStore.initialize(corpus.learning)
    corpus.path.chmod(0o644)
    with pytest.raises(LearningUnavailable):
        corpus.status()
    corpus.path.chmod(0o600)
    with sqlite3.connect(corpus.path) as db:
        db.execute("PRAGMA user_version=99")
    with pytest.raises(LearningUnavailable):
        corpus.status()
    corpus.path.write_bytes(b"corrupt")
    with pytest.raises(LearningUnavailable):
        corpus.status()
    corpus.path.unlink()
    with pytest.raises(LearningUnavailable):
        corpus.status()
    assert not corpus.path.exists()


def test_cli_import_roundtrip_duplicate_and_content_free_output(tmp_path, monkeypatch, capsys):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    base = ["trubot-archives", "--learning-path", str(learning.path)]
    monkeypatch.setattr("sys.argv", [*base, "init"])
    main()
    assert json.loads(capsys.readouterr().out)["status"]["documents"] == 0
    source = tmp_path / "source.txt"
    source.write_bytes(RAW)
    source.chmod(0o600)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": 1,
                "target_alias": "legacy.target",
                "alias_basis": "operator",
                "files": [
                    {"path": source.name, "channel": "general", "origin": {"kind": "fixture"}}
                ],
            }
        )
    )
    manifest.chmod(0o600)
    monkeypatch.setattr("sys.argv", [*base, "import", "--manifest", str(manifest)])
    main()
    output = capsys.readouterr().out
    assert "Perfect" not in output and "legacy.target" not in output
    assert json.loads(output)["imports"][0]["result"] == "imported"
    main()
    assert json.loads(capsys.readouterr().out)["imports"][0]["result"] == "duplicate"
    monkeypatch.setattr("sys.argv", [*base, "status"])
    main()
    assert json.loads(capsys.readouterr().out)["status"]["documents"] == 1
    with ArchiveStore(learning)._transaction() as db:
        digest = db.execute("SELECT digest FROM documents").fetchone()[0]
    monkeypatch.setattr("sys.argv", [*base, "remove", "--digest", digest])
    main()
    assert json.loads(capsys.readouterr().out)["status"]["documents"] == 0
    for tail in [["import"], ["remove"], ["remove", "--digest", "invalid"]]:
        monkeypatch.setattr("sys.argv", [*base, *tail])
        with pytest.raises(SystemExit) as error:
            main()
        assert error.value.code == 2
    manifest.chmod(0o644)
    monkeypatch.setattr("sys.argv", [*base, "import", "--manifest", str(manifest)])
    with pytest.raises(SystemExit):
        main()


def visual_episode(raw=b"synthetic image bytes"):
    import hashlib

    digest = hashlib.sha256(raw).hexdigest()
    return {
        "source": {"guild_id": "77", "channel_id": "10", "message_id": "200"},
        "images": [{"digest": digest, "path": "synthetic.png", "captured": True}],
        "context": [
            {
                "id": "200",
                "author_id": "50",
                "bot": False,
                "webhook": False,
                "created_at": NOW.isoformat(),
                "content": "A peer posted the visual setup.",
                "target": True,
            },
            {
                "id": "201",
                "author_id": "42",
                "bot": False,
                "webhook": False,
                "created_at": NOW.isoformat(),
                "content": "Synthetic target response to image.",
            },
            {
                "id": "202",
                "author_id": "42",
                "bot": True,
                "webhook": False,
                "created_at": NOW.isoformat(),
                "content": "Bot text cannot teach personality.",
            },
        ],
    }, {digest: raw}


def test_visual_bytes_context_stable_attribution_duplicate_updates_and_withdrawal(corpus):
    episode, assets = visual_episode()
    digest = corpus.import_visual_episode(episode, assets, now=NOW)
    assert corpus.import_visual_episode(episode, assets, now=NOW) == digest
    stored = corpus.visual_context(digest)
    assert [m["target"] for m in stored["context"]] == [False, True, False]
    assert stored["context"][1]["created_at"] == NOW.isoformat()
    assert corpus.status()["visual_episodes"] == corpus.status()["image_assets"] == 1
    assert corpus.read_asset(next(iter(assets))) == next(iter(assets.values()))
    # A source correction replaces context and garbage-collects orphaned pixels.
    updated, new_assets = visual_episode(b"corrected image bytes")
    updated["context"][1]["content"] = "Corrected caption context"
    assert corpus.import_visual_episode(updated, new_assets, now=NOW) == digest
    assert corpus.visual_context(digest)["context"][1]["content"] == "Corrected caption context"
    assert corpus.status()["image_assets"] == 1
    with pytest.raises(LearningUnavailable):
        corpus.read_asset(next(iter(assets)))
    corpus.remove_visual_episode(digest, now=NOW)
    assert corpus.status()["visual_episodes"] == corpus.status()["image_assets"] == 0
    with pytest.raises(LearningUnavailable):
        corpus.visual_context(digest)
    with pytest.raises(LearningUnavailable):
        corpus.import_visual_episode(episode, assets, now=NOW)
    episode["source"]["message_id"] = "201"
    corpus.import_visual_episode(episode, assets, now=NOW)
    corpus.learning.forget(now=NOW)
    assert not corpus.path.exists()


@pytest.mark.parametrize(
    "change",
    ["guild", "channel", "context", "source_missing", "date", "digest", "size", "declared"],
)
def test_visual_invalid_scope_dates_or_pixels_are_refused(corpus, change):
    episode, assets = visual_episode()
    if change == "guild":
        episode["source"]["guild_id"] = "78"
    elif change == "channel":
        episode["source"]["channel_id"] = "0"
    elif change == "context":
        episode["context"] = []
    elif change == "source_missing":
        episode["source"]["message_id"] = "999"
    elif change == "date":
        episode["context"][0]["created_at"] = "2020-01-01T12:00:00"
    elif change == "digest":
        assets[next(iter(assets))] = b"wrong"
    elif change == "size":
        assets[next(iter(assets))] = b""
    else:
        episode["images"] = []
    with pytest.raises(LearningUnavailable):
        corpus.import_visual_episode(episode, assets, now=NOW)
    assert corpus.status()["visual_episodes"] == 0


def test_visual_cli_imports_bytes_replays_and_suppresses(corpus, tmp_path, monkeypatch, capsys):
    episode, assets = visual_episode()
    image = tmp_path / "synthetic.png"
    image.write_bytes(next(iter(assets.values())))
    image.chmod(0o600)
    source = tmp_path / "episode.json"
    source.write_text(json.dumps(episode))
    source.chmod(0o600)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"schema": 1, "files": [], "visuals": [{"path": source.name}]}))
    manifest.chmod(0o600)
    base = ["trubot-archives", "--learning-path", str(corpus.learning.path)]
    monkeypatch.setattr("sys.argv", [*base, "import", "--manifest", str(manifest)])
    main()
    output = capsys.readouterr().out
    assert json.loads(output)["status"]["image_assets"] == 1
    assert "Synthetic" not in output
    main()
    assert json.loads(capsys.readouterr().out)["status"]["visual_episodes"] == 1
    with corpus._transaction() as db:
        digest = db.execute("SELECT digest FROM visual_episodes").fetchone()[0]
    monkeypatch.setattr("sys.argv", [*base, "remove-visual", "--digest", digest])
    main()
    assert json.loads(capsys.readouterr().out)["status"]["image_assets"] == 0
