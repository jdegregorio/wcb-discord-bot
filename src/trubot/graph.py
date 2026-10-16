"""Private evidence graph with operator-reviewed derivations and fail-closed recall."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import ExitStack, closing, contextmanager, nullcontext
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from trubot.archives import ArchiveStore
from trubot.episode_memory import (
    OBSERVATION_KINDS,
    PATTERN_KINDS,
    abstraction_contract,
    automated_pattern_context,
    observation_sources,
)
from trubot.learning import LearningStore, LearningUnavailable, _private, _time
from trubot.lexical import phrase, words
from trubot.native_context import NativeEpisode

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


class _LookupLimit(Exception):
    """Stop source validation before considering another incomplete component."""


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
        self.import_observations([item], now=now)

    def import_observations(
        self, items: list[dict[str, Any]], *, now: datetime, dry_run: bool = False
    ) -> None:
        """Validate a whole rollout; previews roll back writes and preserve backups.

        A later import always validates again under the source/withdrawal lock.
        A preview is never a cached authorization to commit stale evidence.
        """
        if not isinstance(items, list) or not 1 <= len(items) <= 100:
            raise LearningUnavailable("One to 100 reviewed observations required")
        identifiers = []
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
                raise LearningUnavailable("Explicit observation identifier required")
            identifiers.append(item["id"])
        if len(set(identifiers)) != len(identifiers):
            raise LearningUnavailable("Distinct rollout observation identifiers required")
        with self._transaction() as (db, source):
            for item in items:
                self._write_observation(db, source, item, now=now)
            if dry_run:
                db.rollback()
        # Validation rejection rolls back replacements and preserves prior backups.
        if not dry_run:
            self._remove_backups()

    def _write_observation(
        self,
        db: sqlite3.Connection,
        source: sqlite3.Connection,
        item: dict[str, Any],
        *,
        now: datetime,
        automated: bool = False,
        native_context: tuple[dict[str, Any], ...] = (),
    ) -> None:
        kind = item["kind"]
        if kind not in OBSERVATION_KINDS:
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
        if (
            automated
            and kind in PATTERN_KINDS
            and not automated_pattern_context(snapshots + counterexamples)
        ):
            raise LearningUnavailable("Native pattern context requires durable study provenance")
        key = "observation:" + item["id"]
        data = {
            k: item[k]
            for k in ("kind", "summary", "status", "confidence_basis", "extraction_provenance")
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
        if native_context:
            if (
                not automated
                or len(native_context) > 6
                or any(
                    not self._context_current(db, source, capture, now=now, exact=True)
                    for capture in native_context
                )
            ):
                raise LearningUnavailable("Study context changed before observation write")
            data["native_context"] = list(native_context)
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
        for capture in native_context:
            self._edge(
                db, key, "interpreted-with", "native-context:" + _key(capture["ref"]), capture
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
        entity_keys = [(entity["kind"], entity["id"]) for entity in item["entities"]]
        if len(set(entity_keys)) != len(entity_keys):
            raise LearningUnavailable("Distinct observation concept relationships required")
        for entity in item["entities"]:
            if entity["kind"] not in {"entity", "concept"} or not 1 <= len(entity["aliases"]) <= 12:
                raise LearningUnavailable("Bounded typed entity aliases required")
            if any(not isinstance(a, str) or not 2 <= len(a) <= 80 for a in entity["aliases"]):
                raise LearningUnavailable("Invalid entity alias")
            entity_key = entity["kind"] + ":" + entity["id"]
            # Existing nodes are also the fallback index for legacy relationships.
            # New aliases belong to this reviewed edge, never replace that index.
            if not db.execute("SELECT 1 FROM nodes WHERE id=?", (entity_key,)).fetchone():
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
                data | {"aliases": entity["aliases"]},
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
        self._prune_concept_indexes(db)
        self._bound(db)

    @staticmethod
    def _prune_concept_indexes(db: sqlite3.Connection) -> None:
        # Only legacy relationships need node-level aliases and source metadata.
        # Once the last legacy owner is gone, erase that fallback instead of
        # retaining a retired alias on an otherwise still-connected concept.
        db.execute(
            "UPDATE nodes SET data=? WHERE kind IN ('entity','concept') AND NOT EXISTS "
            "(SELECT 1 FROM edges WHERE target=nodes.id "
            "AND relation IN ('about','exemplifies') "
            "AND json_type(evidence,'$.aliases') IS NULL)",
            (_json({"aliases": [], "index_provenance": "current observation relationships"}),),
        )

    @staticmethod
    def _bound(db: sqlite3.Connection) -> None:
        if db.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] > MAX_NODES:
            raise LearningUnavailable("Graph capacity requires operator maintenance")

    def _valid(
        self,
        data: dict[str, Any],
        source: sqlite3.Connection,
        *,
        db: sqlite3.Connection,
        kind: str,
        now: datetime,
        verified_after: datetime | None = None,
        archive: sqlite3.Connection | None = None,
    ) -> bool:
        # Stored row kinds predate the optional data.kind field. Recheck the
        # current qualification contract even for restored operator observations.
        if kind in PATTERN_KINDS or "abstraction" in data:
            try:
                if data.get("kind", kind) != kind:
                    return False
                abstraction_contract({**data, "kind": kind}, data["supports"])
                if len({s["content_hash"] for s in data["supports"]}) != len(data["supports"]):
                    return False
            except (LearningUnavailable, KeyError, TypeError, ValueError):
                return False
        if data["status"] in {"superseded", "invalid"} or (
            data.get("expires_at") and data["expires_at"] <= _time(now)
        ):
            return False
        if any(
            not self._context_current(db, source, capture, now=now)
            for capture in data.get("native_context", [])
        ):
            return False
        if (
            data.get("review_kind") == "automated-two-pass"
            and (data.get("kind") in PATTERN_KINDS or "abstraction" in data)
            and not automated_pattern_context(observation_sources(data))
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
            text = phrase(query[:8000])
            entities = {
                row["id"]: json.loads(row["data"])["aliases"]
                for row in db.execute(
                    "SELECT id, data FROM nodes WHERE kind IN ('entity', 'concept') "
                    "ORDER BY id LIMIT 1000"
                )
            }
            # Index aliases by the relationship whose current evidence owns them.
            # Legacy relationships retain the node index they previously used.
            matched: dict[str, int] = {}
            owners: dict[str, list[tuple[int, str]]] = {}
            for row in db.execute(
                "SELECT origin,target,json_extract(evidence,'$.aliases') AS aliases FROM edges "
                "WHERE relation IN ('about','exemplifies')"
            ):
                if row["target"] not in entities:
                    continue
                aliases = (
                    json.loads(row["aliases"])
                    if row["aliases"] is not None
                    else entities[row["target"]]
                )
                lengths = [len(words(alias)) for alias in aliases if phrase(alias) in text]
                if lengths:
                    specificity = max(lengths)
                    matched[row["target"]] = max(matched.get(row["target"], 0), specificity)
                    owners.setdefault(row["target"], []).append((specificity, row["origin"]))
            if not matched:
                return []
            # Rank before bounding source validation. Graph growth must not favor
            # the first eight concepts or twelve observations in identifier order.
            candidates: dict[str, tuple[dict[str, Any], set[str], str]] = {}
            for row in db.execute(
                "SELECT n.id, n.kind, n.data, e.target FROM edges e JOIN nodes n ON n.id=e.origin "  # noqa: S608 - only placeholder count is interpolated; values are bound
                "WHERE e.relation IN ('about', 'exemplifies') AND e.target IN ("
                + ",".join("?" for _ in matched)
                + ")",
                tuple(matched),
            ):
                key = row["id"]
                if key not in candidates:
                    candidates[key] = (json.loads(row["data"]), set(), row["kind"])
                candidates[key][1].add(row["target"])
            ranked = sorted(
                candidates,
                key=lambda key: (
                    -max(matched[topic] for topic in candidates[key][1]),
                    -len(candidates[key][1]),
                    key,
                ),
            )
            # This per-call cache is scoped to the shared source lock. At most 64
            # observations undergo freshness validation, including conflict sides.
            current: dict[str, dict[str, Any] | None] = {}

            def read(key: str) -> dict[str, Any] | None:
                if key in current:
                    return current[key]
                if len(current) >= 64:
                    raise _LookupLimit
                if key in candidates:
                    data, _topics, kind = candidates[key]
                else:
                    row = db.execute("SELECT kind,data FROM nodes WHERE id=?", (key,)).fetchone()
                    if row is None:
                        current[key] = None
                        return None
                    data, kind = json.loads(row["data"]), row["kind"]
                current[key] = (
                    {"id": key, **data}
                    if self._valid(data, source, db=db, kind=kind, now=now)
                    else None
                )
                return current[key]

            active_topics: dict[str, bool] = {}

            def topic_current(topic: str) -> bool:
                if topic not in active_topics:
                    active_topics[topic] = any(
                        read(owner) is not None
                        for _specificity, owner in sorted(
                            owners[topic], key=lambda item: (-item[0], item[1])
                        )
                    )
                return active_topics[topic]

            result: dict[str, dict[str, Any]] = {}
            refs: set[str] = set()
            skipped: set[str] = set()
            for key in ranked:
                if key in result or key in skipped:
                    continue
                try:
                    if not any(topic_current(topic) for topic in sorted(candidates[key][1])):
                        continue
                    component = self._lookup_component(key, db, read)
                except _LookupLimit:
                    # Nothing from an incompletely checked component is emitted.
                    break
                if not component:
                    continue
                extra_refs = {
                    _key(s["ref"]) for item in component.values() for s in observation_sources(item)
                }
                if len(result.keys() | component.keys()) > 4 or len(refs | extra_refs) > 5:
                    skipped.update(component)
                    continue
                result.update(component)
                refs.update(extra_refs)
                if len(result) == 4:
                    break
            return list(result.values())

    @staticmethod
    def _lookup_component(
        key: str,
        db: sqlite3.Connection,
        read: Callable[[str], dict[str, Any] | None],
    ) -> dict[str, dict[str, Any]]:
        """Never select one side of a valid transitive contradiction component."""
        component: dict[str, dict[str, Any]] = {}
        pending = [key]
        seen = set()
        while pending:
            key = pending.pop()
            if key in seen:
                continue
            seen.add(key)
            item = read(key)
            if item is None:
                continue
            component[key] = item
            refs = {
                _key(s["ref"]) for item in component.values() for s in observation_sources(item)
            }
            if len(component) > 4 or len(refs) > 5:
                return {}
            pending.extend(
                row[0]
                for row in db.execute(
                    "SELECT target FROM edges WHERE origin=? AND relation='contradicts' "
                    "UNION SELECT origin FROM edges WHERE target=? AND relation='contradicts' "
                    "ORDER BY 1 DESC",
                    (key, key),
                )
                if row[0] not in seen
            )
        return component

    def describe(
        self, ids: list[str], *, now: datetime, verified_after: datetime | None
    ) -> list[dict[str, Any]]:
        with self._transaction() as (db, source):
            result = []
            for key in ids[:4]:
                row = db.execute("SELECT kind,data FROM nodes WHERE id=?", (key,)).fetchone()
                if row:
                    data = json.loads(row["data"])
                    if self._valid(
                        data,
                        source,
                        db=db,
                        kind=row["kind"],
                        now=now,
                        verified_after=verified_after,
                    ):
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
                elif row["kind"] == "native_context":
                    invalid = not self._native_context_valid(data, source, now=now)
                elif row["kind"] in OBSERVATION_KINDS:
                    invalid = not self._valid(
                        data, source, db=db, kind=row["kind"], now=now, archive=archive
                    )
                elif "archive_episode" in data:
                    invalid = data["archive_episode"] not in episodes
                if invalid:
                    if row["kind"] == "native_context":
                        invalid_sources.add(_key(data["ref"]))
                    elif row["kind"] in OBSERVATION_KINDS:
                        invalid_sources.update(
                            _key(capture["ref"]) for capture in data.get("native_context", [])
                        )
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
            self._prune_concept_indexes(db)
            self._prune_native_dependencies(db)
        if erased:
            self._remove_backups()
        return erased

    def _native_context_valid(
        self, data: dict[str, Any], source: sqlite3.Connection, *, now: datetime
    ) -> bool:
        current = self._snapshot(data["ref"], source, now=now)
        if current is None or current["fingerprint"] != data["source_fingerprint"]:
            return False
        captured = datetime.fromisoformat(data["captured_at"])
        if not now - timedelta(days=30) <= captured <= now:
            return False
        identity = self.learning._read_identity(source)
        for dependency in data["dependencies"]:
            if (
                dependency["guild_id"] != identity.guild_id
                or dependency["channel_id"] != current["ref"]["channel_id"]
                or dependency["created_at"]
                < _time(now - timedelta(days=self.learning.retention_days))
            ):
                return False
            # Target-authored neighbors already have authoritative text in the
            # learning store. Restored metadata must also match their current row.
            target = source.execute(
                "SELECT * FROM messages WHERE id=?", (dependency["message_id"],)
            ).fetchone()
            if target and (
                not target["content"]
                or hashlib.sha256(target["content"].encode()).hexdigest()
                != dependency["content_sha256"]
                or target["edited_at"] != dependency["edited_at"]
            ):
                return False
            invalid = source.execute(
                "SELECT * FROM invalidations WHERE id=?", (dependency["message_id"],)
            ).fetchone()
            if invalid and (
                invalid["channel_id"] != dependency["channel_id"]
                or invalid["deleted"]
                or invalid["observed_at"] >= data["captured_at"]
            ):
                return False
        return True

    def native_context_targets(
        self, *, now: datetime, channel_ids: frozenset[int], limit: int = 2
    ) -> list[dict[str, Any]]:
        """Rotate existing captures, never treat stored metadata as fresh context."""
        if not 1 <= limit <= 2:
            raise LearningUnavailable("Bounded native context verification required")
        with self._transaction() as (db, source):
            rows = [
                row
                for row in db.execute(
                    "SELECT id,data FROM nodes WHERE kind='native_context' ORDER BY id"
                ).fetchall()
                if (data := json.loads(row["data"]))["ref"]["channel_id"] in channel_ids
                and self._native_context_valid(data, source, now=now)
            ]
            cursor = db.execute(
                "SELECT cursor FROM checkpoints WHERE stream='native-context-verification'"
            ).fetchone()
            after = cursor[0] if cursor else ""
            ordered = [row for row in rows if row["id"] > after] + [
                row for row in rows if row["id"] <= after
            ]
            selected = ordered[:limit]
            if selected:
                db.execute(
                    "INSERT OR REPLACE INTO checkpoints VALUES ('native-context-verification', ?)",
                    (selected[-1]["id"],),
                )
            return [json.loads(row["data"]) for row in selected]

    def native_context_current(self, data: dict[str, Any], *, now: datetime) -> bool:
        with self._transaction() as (db, source):
            return self._context_current(db, source, data, now=now, exact=True)

    @staticmethod
    def _context_signature(data: dict[str, Any]) -> dict[str, Any]:
        # Unchanged recaptures extend observed visibility, not the interpretation.
        return {key: value for key, value in data.items() if key != "captured_at"}

    def _context_current(
        self,
        db: sqlite3.Connection,
        source: sqlite3.Connection,
        data: dict[str, Any],
        *,
        now: datetime,
        exact: bool = False,
    ) -> bool:
        row = db.execute(
            "SELECT data FROM nodes WHERE id=? AND kind='native_context'",
            ("native-context:" + _key(data["ref"]),),
        ).fetchone()
        current = json.loads(row[0]) if row else None
        return bool(
            current
            and (
                current == data
                if exact
                else self._context_signature(current) == self._context_signature(data)
            )
            and self._native_context_valid(data, source, now=now)
            and self._native_context_valid(current, source, now=now)
        )

    def study_context(self, ref: dict[str, Any], *, now: datetime) -> dict[str, Any] | None:
        """Select existing setup only. No new collector, intake or visibility claim."""
        with self._transaction() as (db, source):
            row = db.execute(
                "SELECT data FROM nodes WHERE id=? AND kind='native_context'",
                ("native-context:" + _key(ref),),
            ).fetchone()
            if row:
                data: dict[str, Any] = json.loads(row[0])
                if self._native_context_valid(data, source, now=now):
                    return data
            return None

    @staticmethod
    def _erase_context_observations(db: sqlite3.Connection, key: str) -> None:
        db.execute(
            "DELETE FROM nodes WHERE id IN (SELECT origin FROM edges "
            "WHERE target=? AND relation='interpreted-with')",
            (key,),
        )
        source_key = key.removeprefix("native-context:")
        for row in db.execute(
            "SELECT stream,cursor FROM checkpoints WHERE stream LIKE 'study:%'"
        ).fetchall():
            if source_key in json.loads(row["cursor"]).get("source_keys", []):
                db.execute("DELETE FROM checkpoints WHERE stream=?", (row["stream"],))

    def discard_native_context(self, data: dict[str, Any]) -> bool:
        """A stale verifier cannot erase a concurrent newer capture."""
        with self._transaction() as (db, _source):
            key = "native-context:" + _key(data["ref"])
            row = db.execute("SELECT data FROM nodes WHERE id=?", (key,)).fetchone()
            removed = bool(row and json.loads(row[0]) == data)
            if removed:
                self._erase_context_observations(db, key)
                db.execute("DELETE FROM nodes WHERE id=?", (key,))
                self._prune_native_dependencies(db)
        if removed:
            self._remove_backups()
        return removed

    def record_native_context(self, episode: NativeEpisode, *, now: datetime) -> bool:
        """Record last-observed setup dependencies, never a study eligibility certificate.

        Peer text remains ephemeral. The automatic native pattern gate stays closed;
        offline metadata cannot establish current Discord visibility or complete setup.
        """
        focus = episode.source
        if focus is None:
            raise LearningUnavailable("Authenticated native capture required")
        with self._transaction() as (db, source):
            identity = self.learning._read_identity(source)
            ref = {"kind": "discord", "message_id": focus.id}
            current = self._snapshot(ref, source, now=now)
            if (
                current is None
                or focus.bot
                or focus.webhook
                or focus.author_id != identity.user_id
                or focus.guild_id != identity.guild_id
                or focus.channel_id != current["ref"]["channel_id"]
                or _time(focus.created_at) != current["source_time"]
                or not episode.matches(
                    focus.content[:4000], _time(focus.edited_at) if focus.edited_at else None
                )
                or current["fingerprint"]
                != _hash(
                    [
                        current["ref"],
                        focus.content[:4000],
                        _time(focus.created_at),
                        _time(focus.edited_at) if focus.edited_at else None,
                    ]
                )
                or not now - timedelta(seconds=30) <= focus.observed_at <= now
                or len(episode.dependencies) > 5
                or len({row["message_id"] for row in episode.dependencies})
                != len(episode.dependencies)
                or any(row["message_id"] == focus.id for row in episode.dependencies)
            ):
                raise LearningUnavailable("Native capture source changed or outside bounds")
            dependency_keys = {
                "message_id",
                "created_at",
                "edited_at",
                "speaker_id",
                "position",
                "reply_to_message_id",
                "focus_replies_to_this",
                "channel_id",
                "guild_id",
                "content_sha256",
                "media_present",
            }
            if any(set(row) != dependency_keys for row in episode.dependencies):
                raise LearningUnavailable("Content-free dependency metadata required")
            for row in episode.dependencies:
                if (
                    any(
                        type(row[key]) is not int or row[key] <= 0
                        for key in ("message_id", "speaker_id", "channel_id", "guild_id")
                    )
                    or row["position"] not in ("before", "after")
                    or type(row["media_present"]) is not bool
                    or type(row["focus_replies_to_this"]) is not bool
                    or not isinstance(row["content_sha256"], str)
                    or len(row["content_sha256"]) != 64
                    or any(c not in "0123456789abcdef" for c in row["content_sha256"])
                    or not _time(datetime.fromisoformat(row["created_at"]))
                    <= _time(focus.observed_at)
                ):
                    raise LearningUnavailable("Invalid dependency metadata")
            data = {
                "ref": current["ref"],
                "source_fingerprint": current["fingerprint"],
                "captured_at": _time(focus.observed_at),
                "source_time": current["source_time"],
                "unknown_date": False,
                "extraction_version": "native-dependency-capture-v1",
                "scope": "bounded adjacency and same-channel reference; not complete context",
                "visibility": "observed at capture only; fresh reads required before learning",
                "dependencies": list(episode.dependencies),
                "gaps": list(episode.gaps),
            }
            if not self._native_context_valid(data, source, now=now):
                raise LearningUnavailable("Native capture dependencies invalidated")
            key = "native-context:" + _key(ref)
            previous = db.execute("SELECT data FROM nodes WHERE id=?", (key,)).fetchone()
            # A raced or older collector must not overwrite a newer capture.
            if previous and json.loads(previous[0])["captured_at"] > data["captured_at"]:
                return False
            if previous and self._context_signature(
                json.loads(previous[0])
            ) != self._context_signature(data):
                self._erase_context_observations(db, key)
            db.execute("DELETE FROM edges WHERE origin=?", (key,))
            if not db.execute("SELECT 1 FROM nodes WHERE id=?", (_key(ref),)).fetchone():
                source_data = current | {
                    "extraction_version": VERSION,
                    "observed_at": _time(now),
                    "confidence_basis": "Pinned authenticated identity",
                    "status": "active",
                }
                self._node(db, _key(ref), "human_source", source_data)
                self._node(
                    db, "person:target", "person", source_data | {"label": "verified Andrew"}
                )
                source_episode = "episode:" + _key(ref)
                self._node(db, source_episode, "episode", source_data)
                self._edge(db, _key(ref), "authored-by", "person:target", source_data)
                self._edge(db, _key(ref), "part-of", source_episode, source_data)
            self._node(db, key, "native_context", data)
            self._edge(
                db, key, "context-for", _key(ref), {"source_fingerprint": current["fingerprint"]}
            )
            for dependency in data["dependencies"]:
                target = "native-context-dependency:" + str(dependency["message_id"])
                # Edge evidence holds this capture's complete metadata. Shared nodes
                # hold only routing, so another capture cannot rewrite its fingerprint.
                self._node(
                    db,
                    target,
                    "native_context_dependency",
                    {key: dependency[key] for key in ("message_id", "guild_id", "channel_id")},
                )
                self._edge(db, key, "depends-on", target, dependency)
            for evicted in db.execute(
                "SELECT id FROM nodes WHERE kind='native_context' "
                "ORDER BY json_extract(data, '$.captured_at') DESC, id DESC LIMIT -1 OFFSET 100"
            ).fetchall():
                self._erase_context_observations(db, evicted[0])
            db.execute(
                "DELETE FROM nodes WHERE id IN (SELECT id FROM nodes WHERE kind='native_context' "
                "ORDER BY json_extract(data, '$.captured_at') DESC, id DESC LIMIT -1 OFFSET 100)"
            )
            self._prune_native_dependencies(db)
            if db.execute("SELECT COUNT(*) FROM nodes").fetchone()[0] > MAX_NODES:
                raise LearningUnavailable("Graph node limit reached")
        # Replacement/eviction must not leave older private setup in graph backups.
        self._remove_backups()
        return True

    @staticmethod
    def _prune_native_dependencies(db: sqlite3.Connection) -> None:
        db.execute(
            "DELETE FROM nodes WHERE kind='native_context_dependency' AND id NOT IN "
            "(SELECT target FROM edges WHERE relation='depends-on')"
        )

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
            row = db.execute("SELECT kind, data FROM nodes WHERE id=?", (key,)).fetchone()
            if row and row["kind"] in OBSERVATION_KINDS:
                data = json.loads(row["data"])
                if data.get("review_kind") == "automated-two-pass":
                    for support in observation_sources(data):
                        db.execute(
                            "INSERT OR REPLACE INTO checkpoints VALUES (?, ?)",
                            ("study-veto:" + _key(support["ref"]), support["fingerprint"]),
                        )
                db.execute("DELETE FROM nodes WHERE id=?", (key,))
            db.execute(
                "DELETE FROM nodes WHERE kind IN ('visual','captured_human') AND id NOT IN "
                "(SELECT origin FROM edges WHERE relation='part-of')"
            )
            db.execute(
                "DELETE FROM nodes WHERE kind IN ('entity','concept') AND id NOT IN "
                "(SELECT target FROM edges WHERE relation IN ('about','exemplifies'))"
            )
            self._prune_concept_indexes(db)
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
    parser.add_argument("--dry-run", action="store_true", help="Preview import without committing")
    args = parser.parse_args()
    if args.dry_run and args.command != "import":
        parser.error("--dry-run only applies to import")
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
            graph.import_observations(manifest["observations"], now=now, dry_run=args.dry_run)
            batch = {
                "validated": len(manifest["observations"]),
                "committed": 0 if args.dry_run else len(manifest["observations"]),
            }
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
