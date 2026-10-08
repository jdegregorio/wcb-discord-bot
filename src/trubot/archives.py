"""Operator-imported Slack text exports with lossless provenance and cautious attribution.

This module performs no network or model calls. Export text never configures identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trubot.learning import LearningStore, LearningUnavailable, _private, _time

MAX_SOURCE_BYTES = 16 * 1024 * 1024
PARSER_VERSION = 1
_CLOCK = re.compile(r"^\s*(?:[1-9]|1[0-2]):[0-5]\d\s+[AP]M\s*$")
_SHORT_CLOCK = re.compile(r"^(?:[0-9]|1[0-9]|2[0-3]):[0-5]\d$")
_REACTION = re.compile(r"^:[\w+-]+:$")
_THREAD = re.compile(r"^\d+ repl(?:y|ies)$")
_SYSTEM = re.compile(r"^(?:joined #|was added to #|set the channel (?:description|purpose):)")
_SCHEMA = """
PRAGMA user_version = 1;
CREATE TABLE documents (
    digest TEXT PRIMARY KEY, channel TEXT NOT NULL, raw BLOB NOT NULL,
    imported_at TEXT NOT NULL, parser_version INTEGER NOT NULL,
    target_alias TEXT NOT NULL, alias_basis TEXT NOT NULL
);
CREATE TABLE origins (
    document TEXT NOT NULL REFERENCES documents(digest) ON DELETE CASCADE,
    metadata TEXT NOT NULL, period_hint TEXT, PRIMARY KEY(document, metadata)
);
CREATE TABLE messages (
    document TEXT NOT NULL REFERENCES documents(digest) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL, start_line INTEGER NOT NULL, end_line INTEGER NOT NULL,
    speaker TEXT NOT NULL, display_time TEXT NOT NULL, content TEXT NOT NULL,
    kind TEXT NOT NULL, target INTEGER NOT NULL, voice_eligible INTEGER NOT NULL,
    flags TEXT NOT NULL, PRIMARY KEY(document, ordinal)
);
CREATE TABLE suppressions (digest TEXT PRIMARY KEY, suppressed_at TEXT NOT NULL);
CREATE TABLE visual_episodes (
    digest TEXT PRIMARY KEY, metadata TEXT NOT NULL, captured_at TEXT NOT NULL
);
CREATE TABLE assets (digest TEXT PRIMARY KEY, raw BLOB NOT NULL);
CREATE TABLE episode_assets (
    episode TEXT NOT NULL REFERENCES visual_episodes(digest) ON DELETE CASCADE,
    asset TEXT NOT NULL REFERENCES assets(digest), PRIMARY KEY(episode, asset)
);
"""


@dataclass(frozen=True, slots=True)
class ArchiveMessage:
    ordinal: int
    start_line: int
    end_line: int
    speaker: str = field(repr=False)
    display_time: str
    content: str = field(repr=False)
    kind: str
    target: bool
    voice_eligible: bool
    flags: tuple[str, ...]


def parse_slack_export(raw: bytes, *, target_alias: str) -> list[ArchiveMessage]:
    """Parse copied Slack UI blocks, retaining raw bytes separately for reparsing.

    Time of day is a display value, never a dated source timestamp. Shorthand times
    stay in the same block: AM/PM, calendar date and message IDs are unavailable.
    Context is export adjacency, not proof of a reply relationship or motive.
    """
    if not raw or len(raw) > MAX_SOURCE_BYTES or not target_alias.strip():
        raise LearningUnavailable("Empty, oversized or unattributed archive")
    try:
        lines = raw.decode("utf-8-sig").splitlines()
    except UnicodeDecodeError as error:
        raise LearningUnavailable("Archive requires UTF-8 text") from error
    starts = [
        i
        for i in range(len(lines) - 1)
        if lines[i].strip() and len(lines[i].strip()) <= 100 and _CLOCK.fullmatch(lines[i + 1])
    ]
    if not starts:
        raise LearningUnavailable("No supported Slack message headers")
    messages = []
    for ordinal, start in enumerate(starts):
        end = starts[ordinal + 1] if ordinal + 1 < len(starts) else len(lines)
        speaker = lines[start].strip()
        body = lines[start + 2 : end]
        flags = {"calendar_date_unknown", "adjacent_context_only"}
        cleaned = []
        for index, line in enumerate(body):
            stripped = line.strip()
            if _SHORT_CLOCK.fullmatch(stripped):
                flags.add("grouped_continuations")
                continue
            if (
                _REACTION.fullmatch(stripped)
                and index + 1 < len(body)
                and body[index + 1].strip().isdigit()
            ):
                flags.add("reaction_metadata")
                continue
            if stripped.isdigit() and index and _REACTION.fullmatch(body[index - 1].strip()):
                continue
            if (
                _THREAD.fullmatch(stripped)
                or "View thread" in stripped
                or stripped in ("View newer replies", "Custom response")
            ):
                flags.add("slack_ui_metadata")
                continue
            cleaned.append(line)
        content = "\n".join(cleaned).strip()
        kind = "system" if _SYSTEM.match(content) else "message"
        if speaker.casefold() == "slackbot":
            kind = "bot"
        if "replied to a thread:" in content:
            flags.add("thread_quote_ambiguous")
        if "http://" in content or "https://" in content:
            flags.add("link_preview_ambiguous")
        if any(label in content for label in ("Image from iOS", "Click to expand", "Show more")):
            flags.add("attachment_or_preview")
            flags.add("visual_context_missing")
        if re.search(r"(?im)^.{1,100}\.(?:png|jpe?g|gif|webp)\s*$", content):
            flags.update(("attachment_or_preview", "visual_context_missing"))
        target = speaker == target_alias and kind == "message"
        ambiguous = {"thread_quote_ambiguous", "link_preview_ambiguous", "attachment_or_preview"}
        messages.append(
            ArchiveMessage(
                ordinal,
                start + 1,
                end,
                speaker,
                lines[start + 1].strip(),
                content,
                kind,
                target,
                target and bool(content) and not flags & ambiguous,
                tuple(sorted(flags)),
            )
        )
    return messages


class ArchiveStore:
    """Separate long-term historical corpus, guarded by the existing learning identity.

    The learning lock serializes import/read/delete with complete withdrawal.
    Ordinary replies never read this store. Historical retention is operator-owned,
    independent of the rolling Discord retention horizon.
    """

    def __init__(self, learning: LearningStore) -> None:
        self.learning = learning
        self.path = learning.path.absolute().with_name("archives.sqlite3")

    @classmethod
    def initialize(cls, learning: LearningStore) -> ArchiveStore:
        store = cls(learning)
        with learning._transaction() as db:
            learning._read_identity(db)
            with store.path.open("xb"):
                pass
            store.path.chmod(0o600)
            with closing(sqlite3.connect(store.path)) as archive:
                archive.executescript(_SCHEMA)
        return store

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        with self.learning._transaction() as learning_db:
            self.learning._read_identity(learning_db)
            try:
                _private(self.path)
                with closing(sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True)) as db:
                    db.row_factory = sqlite3.Row
                    db.execute("PRAGMA foreign_keys=ON")
                    db.execute("PRAGMA secure_delete=ON")
                    db.execute("PRAGMA synchronous=FULL")
                    db.execute("BEGIN IMMEDIATE")
                    if db.execute("PRAGMA user_version").fetchone()[0] != 1:
                        raise LearningUnavailable("Unsupported historical archive schema")
                    yield db
                    db.commit()
            except (sqlite3.Error, OSError) as error:
                raise LearningUnavailable("Private historical archive unavailable") from error

    def import_document(
        self,
        raw: bytes,
        *,
        channel: str,
        target_alias: str,
        alias_basis: str,
        origin: dict[str, Any],
        now: datetime,
        period_hint: str | None = None,
    ) -> dict[str, int | str]:
        if not channel.strip() or not alias_basis.strip() or not origin:
            raise LearningUnavailable("Operator source and attribution provenance required")
        messages = parse_slack_export(raw, target_alias=target_alias)
        digest = hashlib.sha256(raw).hexdigest()
        metadata = json.dumps(origin, sort_keys=True)
        with self._transaction() as db:
            if db.execute("SELECT 1 FROM suppressions WHERE digest=?", (digest,)).fetchone():
                raise LearningUnavailable("Archive was suppressed by operator")
            existing = db.execute("SELECT * FROM documents WHERE digest=?", (digest,)).fetchone()
            if existing and (
                existing["channel"] != channel
                or existing["target_alias"] != target_alias
                or existing["alias_basis"] != alias_basis
            ):
                raise LearningUnavailable("Conflicting archive attribution requires review")
            inserted = existing is None
            if inserted:
                db.execute(
                    "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (digest, channel, raw, _time(now), PARSER_VERSION, target_alias, alias_basis),
                )
                db.executemany(
                    "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        (
                            digest,
                            m.ordinal,
                            m.start_line,
                            m.end_line,
                            m.speaker,
                            m.display_time,
                            m.content,
                            m.kind,
                            int(m.target),
                            int(m.voice_eligible),
                            json.dumps(m.flags),
                        )
                        for m in messages
                    ],
                )
            db.execute(
                "INSERT OR IGNORE INTO origins VALUES (?, ?, ?)", (digest, metadata, period_hint)
            )
        return {
            "result": "imported" if inserted else "duplicate",
            "blocks": len(messages),
            "target_blocks": sum(m.target for m in messages),
        }

    def context(self, digest: str, ordinal: int, *, radius: int = 3) -> list[dict[str, Any]]:
        if not 0 <= radius <= 10:
            raise LearningUnavailable("Context radius must be bounded")
        with self._transaction() as db:
            return [
                dict(row)
                for row in db.execute(
                    "SELECT * FROM messages WHERE document=? AND ordinal BETWEEN ? AND ? "
                    "ORDER BY ordinal",
                    (digest, ordinal - radius, ordinal + radius),
                )
            ]

    def import_visual_episode(
        self, episode: dict[str, Any], assets: dict[str, bytes], *, now: datetime
    ) -> str:
        """Preserve native visual setup and recompute attribution from pinned IDs.

        External embed URLs are references, not a claim that pixels were captured.
        The operator scan has broader guild read authorization than runtime intake.
        """
        identity = self.learning.identity()
        source = episode["source"]
        if int(source["guild_id"]) != identity.guild_id or int(source["channel_id"]) <= 0:
            raise LearningUnavailable("Visual episode must belong to the verified guild")
        context = episode["context"]
        if not 1 <= len(context) <= 21 or not any(
            str(m["id"]) == str(source["message_id"]) for m in context
        ):
            raise LearningUnavailable("Bounded source message context required")
        normalized = []
        for message in context:
            # A malicious/source-supplied target flag is always ignored.
            normalized.append(
                message
                | {
                    "target": (
                        int(message["author_id"]) == identity.user_id
                        and message["bot"] is False
                        and message["webhook"] is False
                    )
                }
            )
            _time(datetime.fromisoformat(message["created_at"]))
        for digest, raw in assets.items():
            if not raw or len(raw) > MAX_SOURCE_BYTES or hashlib.sha256(raw).hexdigest() != digest:
                raise LearningUnavailable("Invalid visual attachment bytes or digest")
        declared = {m["digest"] for m in episode["images"] if m.get("digest")}
        if declared != assets.keys():
            raise LearningUnavailable("Image provenance and captured bytes must match")
        digest = hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()
        metadata = json.dumps(episode | {"context": normalized}, sort_keys=True)
        with self._transaction() as db:
            if db.execute("SELECT 1 FROM suppressions WHERE digest=?", (digest,)).fetchone():
                raise LearningUnavailable("Visual episode was suppressed by operator")
            db.execute(
                "INSERT INTO visual_episodes VALUES (?, ?, ?) ON CONFLICT(digest) "
                "DO UPDATE SET metadata=excluded.metadata, captured_at=excluded.captured_at",
                (digest, metadata, _time(now)),
            )
            db.execute("DELETE FROM episode_assets WHERE episode=?", (digest,))
            for asset, raw in assets.items():
                db.execute("INSERT OR IGNORE INTO assets VALUES (?, ?)", (asset, raw))
                db.execute("INSERT INTO episode_assets VALUES (?, ?)", (digest, asset))
            db.execute("DELETE FROM assets WHERE digest NOT IN (SELECT asset FROM episode_assets)")
        return digest

    def visual_context(self, digest: str) -> dict[str, Any]:
        with self._transaction() as db:
            row = db.execute(
                "SELECT metadata FROM visual_episodes WHERE digest=?", (digest,)
            ).fetchone()
            if row is None:
                raise LearningUnavailable("Visual source unavailable")
            return dict(json.loads(row[0]))

    def read_asset(self, digest: str) -> bytes:
        """Private study callers may save these bytes for image/animation inspection."""
        with self._transaction() as db:
            row = db.execute("SELECT raw FROM assets WHERE digest=?", (digest,)).fetchone()
            if row is None:
                raise LearningUnavailable("Visual attachment unavailable")
            return bytes(row[0])

    def remove_visual_episode(self, digest: str, *, now: datetime) -> None:
        with self._transaction() as db:
            db.execute("INSERT OR IGNORE INTO suppressions VALUES (?, ?)", (digest, _time(now)))
            db.execute("DELETE FROM visual_episodes WHERE digest=?", (digest,))
            db.execute("DELETE FROM assets WHERE digest NOT IN (SELECT asset FROM episode_assets)")
        self._remove_backups()

    def remove_document(self, digest: str, *, now: datetime) -> None:
        """Correction removes raw and parsed data and blocks silent reimport."""
        with self._transaction() as db:
            db.execute("INSERT OR IGNORE INTO suppressions VALUES (?, ?)", (digest, _time(now)))
            db.execute("DELETE FROM documents WHERE digest=?", (digest,))
        self._remove_backups()

    def _remove_backups(self) -> None:
        # Backup copies could otherwise restore corrected sources. Remove only
        # this store's documented copies; the withdrawal marker remains separate.
        directory = self.path.parent / "backups"
        if directory.exists() or directory.is_symlink():
            _private(directory)
            for path in directory.glob("archives-*.sqlite3*"):
                _private(path)
                if not path.is_file():
                    raise LearningUnavailable("Archive backup requires a regular private file")
                path.unlink()

    def status(self) -> dict[str, int]:
        with self._transaction() as db:
            if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise LearningUnavailable("Historical archive failed integrity check")
            return {
                "visual_episodes": db.execute("SELECT COUNT(*) FROM visual_episodes").fetchone()[0],
                "image_assets": db.execute("SELECT COUNT(*) FROM assets").fetchone()[0],
                "image_bytes": db.execute(
                    "SELECT COALESCE(SUM(length(raw)), 0) FROM assets"
                ).fetchone()[0],
                "schema": 1,
                "documents": db.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
                "origins": db.execute("SELECT COUNT(*) FROM origins").fetchone()[0],
                "blocks": db.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
                "target_blocks": db.execute(
                    "SELECT COUNT(*) FROM messages WHERE target=1"
                ).fetchone()[0],
                "voice_eligible_blocks": db.execute(
                    "SELECT COUNT(*) FROM messages WHERE voice_eligible=1"
                ).fetchone()[0],
                "suppressed_documents": db.execute("SELECT COUNT(*) FROM suppressions").fetchone()[
                    0
                ],
            }


def main() -> None:
    parser = argparse.ArgumentParser(description="Private historical import (content-free output)")
    parser.add_argument("command", choices=("init", "import", "status", "remove", "remove-visual"))
    parser.add_argument(
        "--learning-path",
        type=Path,
        default=Path(
            os.environ.get("TRUBOT_LEARNING_STORE_PATH", "/var/lib/trubot/learning.sqlite3")
        ),
    )
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--digest")
    args = parser.parse_args()
    try:
        learning = LearningStore(args.learning_path.absolute())
        store = (
            ArchiveStore.initialize(learning) if args.command == "init" else ArchiveStore(learning)
        )
        results = []
        if args.command == "import":
            if args.manifest is None:
                raise LearningUnavailable("A private operator manifest is required")
            _private(args.manifest)
            manifest = json.loads(args.manifest.read_text())
            if manifest["schema"] != 1:
                raise LearningUnavailable("Unsupported import manifest")
            for item in manifest["files"]:
                path = args.manifest.parent / item["path"]
                _private(path)
                if path.stat().st_size > MAX_SOURCE_BYTES:
                    raise LearningUnavailable("Archive source exceeds byte limit")
                results.append(
                    store.import_document(
                        path.read_bytes(),
                        channel=item["channel"],
                        target_alias=manifest["target_alias"],
                        alias_basis=manifest["alias_basis"],
                        origin=item["origin"],
                        period_hint=item.get("period_hint"),
                        now=datetime.now(UTC),
                    )
                )
            for item in manifest.get("visuals", []):
                path = args.manifest.parent / item["path"]
                _private(path)
                episode = json.loads(path.read_text())
                assets = {}
                for media in episode["images"]:
                    if media.get("digest"):
                        asset_path = args.manifest.parent / media["path"]
                        _private(asset_path)
                        if asset_path.stat().st_size > MAX_SOURCE_BYTES:
                            raise LearningUnavailable("Image source exceeds byte limit")
                        assets[media["digest"]] = asset_path.read_bytes()
                store.import_visual_episode(episode, assets, now=datetime.now(UTC))
        elif args.command in ("remove", "remove-visual"):
            if not args.digest or not re.fullmatch(r"[0-9a-f]{64}", args.digest):
                raise LearningUnavailable("A valid document digest is required")
            if args.command == "remove":
                store.remove_document(args.digest, now=datetime.now(UTC))
            else:
                store.remove_visual_episode(args.digest, now=datetime.now(UTC))
        print(json.dumps({"status": store.status(), "imports": results}, indent=2))
    except (LearningUnavailable, OSError, ValueError, KeyError, TypeError):
        parser.exit(
            2, "Historical import unavailable; inspect private source and learning state.\n"
        )


if __name__ == "__main__":
    main()
