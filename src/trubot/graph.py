"""Private evidence graph with operator-reviewed derivations and fail-closed recall."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from collections.abc import Iterator
from contextlib import ExitStack, closing, contextmanager, nullcontext
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from trubot.archives import ArchiveStore
from trubot.episode_memory import abstraction_contract, observation_sources
from trubot.learning import LearningStore, LearningUnavailable, _private, _time
from trubot.lexical import phrase

VERSION = "reviewed-graph-v1"
MAX_NODES = 30_000
_SCHEMA = """
PRAGMA user_version=1;
CREATE TABLE nodes (id TEXT PRIMARY KEY, kind TEXT NOT NULL, data TEXT NOT NULL);
CREATE TABLE edges (
    origin TEXT REFERENCES nodes(id) ON DELETE CASCADE,
    relation TEXT NOT NULL, target TEXT REFERENCES nodes(id) ON DELETE CASCADE,
    evidence TEXT NOT NULL, PRIMARY KEY(origin, relation, target)
);
CREATE INDEX reverse_edges ON edges(target, relation);
CREATE TABLE checkpoints (stream TEXT PRIMARY KEY, cursor TEXT NOT NULL);
"""


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _key(ref: dict[str, Any]) -> str:
    if ref["kind"] == "discord":
        return f"discord:{int(ref['message_id'])}"
    if ref["kind"] == "slack":
        return f"slack:{ref['document']}:{int(ref['ordinal']):06}"
    raise LearningUnavailable("Unsupported graph support source")


class GraphStore:
    def __init__(self, learning: LearningStore) -> None:
        self.learning = learning
        self.archives = ArchiveStore(learning)
        self.path = learning.path.absolute().with_name("memory-graph.sqlite3")

    @classmethod
    def initialize(cls, learning: LearningStore) -> GraphStore:
        store = cls(learning)
        with learning._transaction() as db:
            learning._read_identity(db)
            with store.path.open("xb"):
                pass
            store.path.chmod(0o600)
            with closing(sqlite3.connect(store.path)) as graph:
                graph.executescript(_SCHEMA)
        return store

    @contextmanager
    def _transaction(self) -> Iterator[tuple[sqlite3.Connection, sqlite3.Connection]]:
        # Shared learning lock orders graph reads/imports against withdrawal and
        # native edits. Archive writers take the same lock. Never cache derivations.
        with self.learning._transaction() as source:
            self.learning._read_identity(source)
            try:
                _private(self.path)
                with closing(sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True)) as db:
                    db.row_factory = sqlite3.Row
                    db.execute("PRAGMA foreign_keys=ON")
                    db.execute("PRAGMA secure_delete=ON")
                    db.execute("PRAGMA synchronous=FULL")
                    db.execute("BEGIN IMMEDIATE")
                    if db.execute("PRAGMA user_version").fetchone()[0] != 1:
                        raise LearningUnavailable("Unsupported graph schema")
                    yield db, source
                    db.commit()
            except (sqlite3.Error, OSError, KeyError, TypeError, ValueError) as error:
                raise LearningUnavailable("Private graph unavailable") from error

    def _archive(self) -> sqlite3.Connection:
        _private(self.archives.path)
        db = sqlite3.connect(self.archives.path.as_uri() + "?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        if db.execute("PRAGMA user_version").fetchone()[0] != 1:
            db.close()
            raise LearningUnavailable("Unsupported archive schema")
        return db

    def _snapshot(
        self,
        ref: dict[str, Any],
        source: sqlite3.Connection,
        *,
        now: datetime,
        verified_after: datetime | None = None,
        archive: sqlite3.Connection | None = None,
    ) -> dict[str, Any] | None:
        identity = self.learning._read_identity(source)
        if ref["kind"] == "discord":
            row = source.execute(
                "SELECT * FROM messages WHERE id=?", (ref["message_id"],)
            ).fetchone()
            if (
                row is None
                or not row["content"]
                or row["author_id"] != identity.user_id
                or row["guild_id"] != identity.guild_id
                or row["channel_id"] not in identity.channel_ids
                or row["created_at"] < _time(now - timedelta(days=self.learning.retention_days))
                or (verified_after and row["verified_at"] < _time(verified_after))
            ):
                return None
            reference = {
                "kind": "discord",
                "message_id": row["id"],
                "channel_id": row["channel_id"],
            }
            content, timestamp = row["content"], row["created_at"]
            fingerprint = _hash([reference, content, timestamp, row["edited_at"]])
        else:
            with (
                nullcontext(archive)
                if archive is not None
                else closing(self._archive()) as historical
            ):
                row = historical.execute(
                    "SELECT * FROM messages WHERE document=? AND ordinal=?",
                    (ref["document"], ref["ordinal"]),
                ).fetchone()
                if row is None or not row["target"] or not row["voice_eligible"]:
                    return None
                reference = {
                    "kind": "slack",
                    "document": row["document"],
                    "ordinal": row["ordinal"],
                    "start_line": row["start_line"],
                    "end_line": row["end_line"],
                }
                content, timestamp = row["content"], None
                fingerprint = _hash([reference, content, row["speaker"], row["flags"]])
        return {
            "ref": reference,
            "fingerprint": fingerprint,
            "content_hash": _hash(content),
            "source_time": timestamp,
            "unknown_date": timestamp is None,
        }

    @staticmethod
    def _node(db: sqlite3.Connection, key: str, kind: str, data: dict[str, Any]) -> None:
        db.execute(
            "INSERT INTO nodes VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
            "kind=excluded.kind, data=excluded.data",
            (key, kind, _json(data)),
        )

    @staticmethod
    def _edge(db: sqlite3.Connection, origin: str, relation: str, target: str, data: Any) -> None:
        db.execute(
            "INSERT OR REPLACE INTO edges VALUES (?, ?, ?, ?)",
            (origin, relation, target, _json(data)),
        )

    def populate(self, *, now: datetime, limit: int = 100) -> dict[str, int]:
        """One resumable operator batch. Source nodes hold references, never copied text."""
        if not 1 <= limit <= 200:
            raise LearningUnavailable("Graph batches must be bounded")
        with self._transaction() as (db, source):
            refs = [
                {"kind": "discord", "message_id": r[0]}
                for r in source.execute(
                    "SELECT id FROM messages WHERE content IS NOT NULL ORDER BY id LIMIT 10000"
                )
            ]
            try:
                with closing(self._archive()) as archive:
                    refs += [
                        {"kind": "slack", "document": r[0], "ordinal": r[1]}
                        for r in archive.execute(
                            "SELECT document, ordinal FROM messages "
                            "WHERE target=1 AND voice_eligible=1 "
                            "ORDER BY document, ordinal LIMIT 10000"
                        )
                    ]
            except (LearningUnavailable, OSError):
                pass
            present = {r[0] for r in db.execute("SELECT id FROM nodes WHERE kind='human_source'")}
            pending = sorted((r for r in refs if _key(r) not in present), key=_key)
            batch = pending[:limit]
            for ref in batch:
                snapshot = self._snapshot(ref, source, now=now)
                if snapshot is None:
                    continue
                data = snapshot | {
                    "extraction_version": VERSION,
                    "observed_at": _time(now),
                    "confidence_basis": "Verified author or exact approved alias",
                    "status": "active",
                }
                key = _key(ref)
                self._node(db, key, "human_source", data)
                self._node(db, "person:target", "person", data | {"label": "verified Andrew"})
                episode = "episode:" + key
                self._node(
                    db, episode, "episode", data | {"context": "adjacency, not proven replies"}
                )
                self._edge(db, key, "authored-by", "person:target", data)
                self._edge(db, key, "part-of", episode, data)
            if batch:
                db.execute(
                    "INSERT OR REPLACE INTO checkpoints VALUES ('sources', ?)", (_key(batch[-1]),)
                )
            if not db.execute("SELECT 1 FROM nodes WHERE id='person:target'").fetchone():
                self._node(
                    db,
                    "person:target",
                    "person",
                    {
                        "label": "verified Andrew",
                        "extraction_version": VERSION,
                        "observed_at": _time(now),
                        "confidence_basis": "Pinned authenticated identity",
                        "status": "active",
                        "source_time": None,
                        "unknown_date": True,
                    },
                )
            visual_processed = 0
            try:
                with closing(self._archive()) as archive:
                    checkpoint = db.execute(
                        "SELECT cursor FROM checkpoints WHERE stream='visuals'"
                    ).fetchone()
                    after = checkpoint[0] if checkpoint else ""
                    for row in archive.execute(
                        "SELECT digest, metadata, captured_at FROM visual_episodes "
                        "WHERE digest>? ORDER BY digest LIMIT ?",
                        (after, limit),
                    ):
                        episode = json.loads(row["metadata"])
                        metadata = {
                            "archive_episode": row["digest"],
                            "source": episode["source"],
                            "observed_at": row["captured_at"],
                            "extraction_version": VERSION,
                            "status": "tentative",
                            "confidence_basis": "Captured pixels only; not interpreted",
                            "source_time": next(
                                (
                                    m["created_at"]
                                    for m in episode["context"]
                                    if str(m["id"]) == str(episode["source"]["message_id"])
                                ),
                                None,
                            ),
                            "unknown_date": False,
                            "context": "adjacent captured messages, not proven replies",
                        }
                        key = "visual-episode:" + row["digest"]
                        self._node(db, key, "episode", metadata)
                        for image in episode["images"]:
                            digest = image.get("digest")
                            if digest:
                                visual = "visual:" + digest
                                self._node(
                                    db,
                                    visual,
                                    "visual",
                                    {
                                        "image_sha256": digest,
                                        "extraction_version": VERSION,
                                        "observed_at": row["captured_at"],
                                        "status": "tentative",
                                        "source_time": None,
                                        "unknown_date": True,
                                        "confidence_basis": "Captured pixels; see episodes",
                                        "interpretation": "unstudied; review frames",
                                    },
                                )
                                self._edge(db, visual, "part-of", key, metadata)
                        for message in episode["context"]:
                            if message["target"]:
                                human = "captured-human:" + str(message["id"])
                                self._node(
                                    db,
                                    human,
                                    "captured_human",
                                    {
                                        "native_message_id": message["id"],
                                        "source_time": message["created_at"],
                                        "unknown_date": False,
                                        "extraction_version": VERSION,
                                        "observed_at": row["captured_at"],
                                        "status": "tentative",
                                        "confidence_basis": "Pinned ID in captured context",
                                        "interpretation": "refresh source before belief support",
                                    },
                                )
                                self._edge(db, human, "part-of", key, metadata)
                                self._edge(db, human, "authored-by", "person:target", metadata)
                        db.execute(
                            "INSERT OR REPLACE INTO checkpoints VALUES ('visuals', ?)",
                            (row["digest"],),
                        )
                        visual_processed += 1
            except (LearningUnavailable, OSError):
                pass
            self._bound(db)
            return {
                "visual_processed": visual_processed,
                "processed": len(batch),
                "remaining": max(0, len(pending) - len(batch)),
            }

    def import_observation(self, item: dict[str, Any], *, now: datetime) -> None:
        """Trusted private operator input. Human-source content cannot invoke this API."""
        with self._transaction() as (db, source):
            self._write_observation(db, source, item, now=now)
        self._remove_backups()

    def _write_observation(
        self,
        db: sqlite3.Connection,
        source: sqlite3.Connection,
        item: dict[str, Any],
        *,
        now: datetime,
        automated: bool = False,
    ) -> None:
        kind = item["kind"]
        if kind not in {"claim", "preference", "humor", "style"}:
            raise LearningUnavailable("Unsupported reviewed observation")
        if item["status"] not in {"active", "tentative", "contested", "superseded"}:
            raise LearningUnavailable("Explicit observation status required")
        if (
            (not automated and item.get("reviewed_by_operator") is not True)
            or not isinstance(item.get("confidence_basis"), str)
            or not 1 <= len(item["confidence_basis"]) <= 500
            or not isinstance(item.get("extraction_provenance"), str)
            or not 1 <= len(item["extraction_provenance"]) <= 300
            or not 1 <= len(item["supports"]) <= 3
            or not 1 <= len(item["entities"]) <= 4
            or not 1 <= len(item["summary"]) <= 600
        ):
            raise LearningUnavailable("Bounded evidence and review provenance required")
        expiry = item.get("expires_at")
        if expiry:
            expiry = _time(datetime.fromisoformat(expiry))
        if expiry and _time(datetime.fromisoformat(expiry)) <= _time(now):
            raise LearningUnavailable("Observation has expired")
        if automated and (
            item.get("support_basis") not in {"corroborated", "explicit_self_report"}
            or (
                item["support_basis"] == "explicit_self_report"
                and (kind not in {"claim", "preference"} or len(item["supports"]) != 1)
            )
            or (item["support_basis"] == "corroborated" and len(item["supports"]) < 2)
            or item["status"] != "tentative"
            or not expiry
        ):
            raise LearningUnavailable("Qualified automated support basis required")
        snapshots = []
        for ref in item["supports"]:
            snapshot = self._snapshot(ref, source, now=now)
            if snapshot is None:
                raise LearningUnavailable(
                    "Only current attributed human sources can support beliefs"
                )
            snapshots.append(snapshot)
        if len({s["content_hash"] for s in snapshots}) != len(snapshots):
            raise LearningUnavailable("Duplicate support is not corroboration")
        abstraction = abstraction_contract(item, snapshots)
        counterexamples: list[dict[str, Any]] = []
        if abstraction is not None:
            for ref in abstraction["counterexamples"]:
                snapshot = self._snapshot(ref, source, now=now)
                if snapshot is None or any(
                    snapshot["content_hash"] == old["content_hash"]
                    or _key(snapshot["ref"]) == _key(old["ref"])
                    for old in snapshots + counterexamples
                ):
                    raise LearningUnavailable("Distinct attributed counterevidence required")
                counterexamples.append(snapshot)
        key = "observation:" + item["id"]
        data = {
            k: item[k] for k in ("summary", "status", "confidence_basis", "extraction_provenance")
        }
        data |= {
            "supports": snapshots,
            "extraction_version": VERSION,
            "observed_at": _time(now),
            "source_times": [s["source_time"] for s in snapshots],
            "unknown_date": any(s["unknown_date"] for s in snapshots),
            "expires_at": expiry,
            "review_kind": "automated-two-pass" if automated else "operator",
            "support_basis": item.get("support_basis", "operator_reviewed"),
        }
        if abstraction is not None:
            data["abstraction"] = {
                "conditions": abstraction["conditions"],
                "limitations": abstraction["limitations"],
                "counterexamples": counterexamples,
            }
            data["source_times"] = [s["source_time"] for s in snapshots + counterexamples]
            data["unknown_date"] = any(s["unknown_date"] for s in snapshots + counterexamples)
        self._node(db, key, kind, data)
        db.execute(
            "DELETE FROM edges WHERE origin=? OR (target=? AND relation IN "
            "('supports','counterexample-of'))",
            (key, key),
        )
        for snapshot in snapshots + counterexamples:
            src = _key(snapshot["ref"])
            self._node(
                db,
                src,
                "human_source",
                snapshot
                | {
                    "extraction_version": VERSION,
                    "observed_at": _time(now),
                    "confidence_basis": "Attribution checked; see linked observation",
                    "status": "active",
                },
            )
            self._edge(
                db,
                src,
                "counterexample-of" if snapshot in counterexamples else "supports",
                key,
                snapshot | data,
            )
        for entity in item["entities"]:
            if entity["kind"] not in {"entity", "concept"} or not 1 <= len(entity["aliases"]) <= 12:
                raise LearningUnavailable("Bounded typed entity aliases required")
            if any(not isinstance(a, str) or not 2 <= len(a) <= 80 for a in entity["aliases"]):
                raise LearningUnavailable("Invalid entity alias")
            entity_key = entity["kind"] + ":" + entity["id"]
            self._node(
                db,
                entity_key,
                entity["kind"],
                {
                    "aliases": entity["aliases"],
                    "extraction_version": VERSION,
                    "observed_at": _time(now),
                    "confidence_basis": "Attribution checked; see linked observation",
                    "source_times": data["source_times"],
                    "unknown_date": data["unknown_date"],
                    "status": "tentative",
                },
            )
            self._edge(
                db,
                key,
                "about" if kind in {"claim", "preference"} else "exemplifies",
                entity_key,
                data,
            )
        for other in item.get("contradicts", []):
            other_key = "observation:" + other
            if not db.execute("SELECT 1 FROM nodes WHERE id=?", (other_key,)).fetchone():
                raise LearningUnavailable("Contradiction requires an existing observation")
            self._edge(db, key, "contradicts", other_key, data)
            for contested in (key, other_key):
                old = json.loads(
                    db.execute("SELECT data FROM nodes WHERE id=?", (contested,)).fetchone()[0]
                )
                old["status"] = "contested"
                db.execute("UPDATE nodes SET data=? WHERE id=?", (_json(old), contested))
        self._bound(db)

    @staticmethod
    def _bound(db: sqlite3.Connection) -> None:
        if db.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] > MAX_NODES:
            raise LearningUnavailable("Graph capacity requires operator maintenance")

    def _valid(
        self,
        data: dict[str, Any],
        source: sqlite3.Connection,
        *,
        now: datetime,
        verified_after: datetime | None = None,
        archive: sqlite3.Connection | None = None,
    ) -> bool:
        if data["status"] in {"superseded", "invalid"} or (
            data.get("expires_at") and data["expires_at"] <= _time(now)
        ):
            return False
        for support in observation_sources(data):
            current = self._snapshot(
                support["ref"], source, now=now, verified_after=verified_after, archive=archive
            )
            if current is None or current["fingerprint"] != support["fingerprint"]:
                return False
        return True

    def lookup(self, query: str, *, guild_id: int, now: datetime) -> list[dict[str, Any]]:
        with self._transaction() as (db, source):
            if self.learning._read_identity(source).guild_id != guild_id:
                return []
            matched = []
            text = phrase(query[:8000])
            for row in db.execute(
                "SELECT id, data FROM nodes WHERE kind IN ('entity', 'concept') LIMIT 1000"
            ):
                entity = json.loads(row["data"])
                if any(phrase(alias) in text for alias in entity["aliases"]):
                    matched.append(row["id"])
            result = []
            seen = set()
            for key in matched[:8]:
                for row in db.execute(
                    "SELECT n.id, n.data FROM edges e JOIN nodes n ON n.id=e.origin "
                    "WHERE e.target=? AND e.relation IN ('about', 'exemplifies') "
                    "ORDER BY n.id LIMIT 12",
                    (key,),
                ):
                    data = json.loads(row["data"])
                    if row["id"] not in seen and self._valid(data, source, now=now):
                        seen.add(row["id"])
                        result.append({"id": row["id"], **data})
            # Conflicting observations are included together even if only one entity matched.
            for item in list(result):
                for row in db.execute(
                    "SELECT n.id, n.data FROM edges e JOIN nodes n "
                    "ON n.id=CASE WHEN e.origin=? THEN e.target ELSE e.origin END "
                    "WHERE e.relation='contradicts' AND (e.origin=? OR e.target=?)",
                    (item["id"], item["id"], item["id"]),
                ):
                    data = json.loads(row["data"])
                    if row["id"] not in seen and self._valid(data, source, now=now):
                        seen.add(row["id"])
                        result.append({"id": row["id"], **data})
            # A complete neighborhood must fit. Never drop one side of a contradiction.
            refs = {_key(s["ref"]) for item in result for s in observation_sources(item)}
            return result if len(result) <= 4 and len(refs) <= 5 else []

    def describe(
        self, ids: list[str], *, now: datetime, verified_after: datetime | None
    ) -> list[dict[str, Any]]:
        with self._transaction() as (db, source):
            result = []
            for key in ids[:4]:
                row = db.execute("SELECT data FROM nodes WHERE id=?", (key,)).fetchone()
                if row:
                    data = json.loads(row[0])
                    if self._valid(data, source, now=now, verified_after=verified_after):
                        result.append({"id": key, **data})
            return result

    def sweep(self, *, now: datetime) -> int:
        """Erase derivations after source changes; keep source fingerprints authoritative."""
        erased = 0
        invalid_sources = set()
        with self._transaction() as (db, source), ExitStack() as stack:
            archive = None
            try:
                archive = stack.enter_context(closing(self._archive()))
                episodes = {r[0] for r in archive.execute("SELECT digest FROM visual_episodes")}
            except (LearningUnavailable, OSError):
                episodes = set()
            for row in db.execute("SELECT id, kind, data FROM nodes").fetchall():
                data = json.loads(row["data"])
                invalid = False
                if row["kind"] == "human_source":
                    current = self._snapshot(data["ref"], source, now=now, archive=archive)
                    invalid = current is None or current["fingerprint"] != data["fingerprint"]
                elif row["kind"] in {"claim", "preference", "humor", "style"}:
                    invalid = not self._valid(data, source, now=now, archive=archive)
                elif "archive_episode" in data:
                    invalid = data["archive_episode"] not in episodes
                if invalid:
                    db.execute("DELETE FROM nodes WHERE id=?", (row["id"],))
                    db.execute("DELETE FROM nodes WHERE id=?", ("episode:" + row["id"],))
                    if row["kind"] == "human_source":
                        invalid_sources.add(row["id"])
                        db.execute(
                            "DELETE FROM checkpoints WHERE stream IN (?, ?)",
                            ("study:" + row["id"], "study-veto:" + row["id"]),
                        )
                    erased += 1
            for checkpoint in db.execute(
                "SELECT stream, cursor FROM checkpoints WHERE stream LIKE 'study:%'"
            ).fetchall():
                if invalid_sources.intersection(
                    json.loads(checkpoint["cursor"]).get("source_keys", [])
                ):
                    db.execute("DELETE FROM checkpoints WHERE stream=?", (checkpoint["stream"],))
            db.execute(
                "DELETE FROM nodes WHERE kind IN ('visual','captured_human') AND id NOT IN "
                "(SELECT origin FROM edges WHERE relation='part-of')"
            )
            db.execute(
                "DELETE FROM nodes WHERE kind IN ('entity','concept') AND id NOT IN "
                "(SELECT target FROM edges WHERE relation IN ('about','exemplifies'))"
            )
        if erased:
            self._remove_backups()
        return erased

    def _remove_backups(self) -> None:
        backups = self.path.parent / "backups"
        if backups.exists() or backups.is_symlink():
            _private(backups)
            for path in backups.glob("memory-graph-*.sqlite3*"):
                _private(path)
                if not path.is_file():
                    raise LearningUnavailable("Graph backup must be a regular private file")
                path.unlink()

    def remove(self, key: str) -> None:
        with self._transaction() as (db, _source):
            row = db.execute("SELECT data FROM nodes WHERE id=?", (key,)).fetchone()
            if row:
                data = json.loads(row[0])
                if data.get("review_kind") == "automated-two-pass":
                    for support in observation_sources(data):
                        db.execute(
                            "INSERT OR REPLACE INTO checkpoints VALUES (?, ?)",
                            ("study-veto:" + _key(support["ref"]), support["fingerprint"]),
                        )
            db.execute(
                "DELETE FROM nodes WHERE id=? AND kind IN ('claim','preference','humor','style')",
                (key,),
            )
            db.execute(
                "DELETE FROM nodes WHERE kind IN ('visual','captured_human') AND id NOT IN "
                "(SELECT origin FROM edges WHERE relation='part-of')"
            )
            db.execute(
                "DELETE FROM nodes WHERE kind IN ('entity','concept') AND id NOT IN "
                "(SELECT target FROM edges WHERE relation IN ('about','exemplifies'))"
            )
        self._remove_backups()

    def status(self) -> dict[str, Any]:
        with self._transaction() as (db, _source):
            if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise LearningUnavailable("Graph integrity check failed")
            return {
                "schema": 1,
                "nodes": dict(db.execute("SELECT kind, COUNT(*) FROM nodes GROUP BY kind")),
                "edges": db.execute("SELECT COUNT(*) FROM edges").fetchone()[0],
                "studies": dict(
                    db.execute(
                        "SELECT json_extract(cursor, '$.outcome'), COUNT(*) FROM checkpoints "
                        "WHERE stream LIKE 'study:%' GROUP BY json_extract(cursor, '$.outcome')"
                    )
                ),
                "study_vetoes": db.execute(
                    "SELECT COUNT(*) FROM checkpoints WHERE stream LIKE 'study-veto:%'"
                ).fetchone()[0],
                "checkpoints": db.execute("SELECT COUNT(*) FROM checkpoints").fetchone()[0],
            }


def main() -> None:
    parser = argparse.ArgumentParser(description="Private graph administration (counts only)")
    parser.add_argument(
        "command", choices=("init", "populate", "import", "status", "remove", "sweep")
    )
    parser.add_argument(
        "--learning-path",
        type=Path,
        default=Path(
            os.environ.get("TRUBOT_LEARNING_STORE_PATH", "/var/lib/trubot/learning.sqlite3")
        ),
    )
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--id")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    try:
        learning = LearningStore(args.learning_path.absolute())
        graph = GraphStore.initialize(learning) if args.command == "init" else GraphStore(learning)
        now = datetime.now(UTC)
        batch = None
        if args.command == "populate":
            batch = graph.populate(now=now, limit=args.limit)
        elif args.command == "import":
            if args.manifest is None or args.manifest.stat().st_size > 128_000:
                raise LearningUnavailable("Bounded private reviewed manifest required")
            _private(args.manifest)
            manifest = json.loads(args.manifest.read_text())
            if manifest["schema"] != 1 or not 1 <= len(manifest["observations"]) <= 100:
                raise LearningUnavailable("Unsupported observation manifest")
            for item in manifest["observations"]:
                graph.import_observation(item, now=now)
        elif args.command == "remove":
            if not args.id:
                raise LearningUnavailable("Observation identifier required")
            graph.remove("observation:" + args.id)
        if args.command == "sweep":
            batch = {"erased": graph.sweep(now=now)}
        print(json.dumps({"status": graph.status(), "batch": batch}))
    except (LearningUnavailable, OSError, ValueError, KeyError, TypeError):
        parser.exit(2, "Graph unavailable; inspect private sources and review provenance.\n")


if __name__ == "__main__":
    main()
