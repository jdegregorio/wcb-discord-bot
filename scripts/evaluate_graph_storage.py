"""Installed graph recovery acceptance using disposable synthetic state only."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
from contextlib import closing, suppress
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import discord

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable, SourceMessage
from trubot.memory import ContextMemory


def require(condition):
    if not condition:
        raise RuntimeError("Synthetic graph acceptance failed")


def evaluate():
    now = datetime.now(UTC)
    identifier = discord.utils.time_snowflake(now - timedelta(days=1))
    audit = {
        "verified": True,
        "exact_name_match": True,
        "user_id": "42",
        "guild_id": "77",
        "username": "synthetic-person",
        "member_username": "synthetic-person",
        "allowed_channel_ids": ["10"],
        "source_channels": ["10"],
        "message_ids": [str(identifier)],
        "observed_at": now.isoformat(),
    }
    results = []
    with tempfile.TemporaryDirectory(prefix="trubot-graph-") as temporary:
        root = Path(temporary)
        learning = LearningStore.initialize(root / "learning.sqlite3", audit, now=now)
        archive = ArchiveStore.initialize(learning)
        graph = GraphStore.initialize(learning)
        for i, text in enumerate(["I order caramel after dinner.", "I now prefer vanilla."]):
            learning.observe(
                SourceMessage(
                    identifier + i,
                    10,
                    77,
                    42,
                    False,
                    False,
                    now - timedelta(days=1),
                    None,
                    now,
                    text,
                ),
                now=now,
            )
        graph.populate(now=now, limit=1)
        with (
            patch.object(graph, "_bound", side_effect=LearningUnavailable("interrupted")),
            suppress(LearningUnavailable),
        ):
            graph.populate(now=now, limit=1)
        require(GraphStore(learning).populate(now=now, limit=1)["remaining"] == 0)
        results.append({"id": "interrupted-population-restart", "passed": True})

        def item(index, **changes):
            return {
                "id": "choice" + str(index),
                "kind": "preference",
                "summary": "Synthetic dessert statement.",
                "status": "tentative",
                "confidence_basis": "Synthetic explicit statement",
                "extraction_provenance": "Synthetic installed acceptance",
                "reviewed_by_operator": True,
                "supports": [{"kind": "discord", "message_id": identifier + index}],
                "entities": [{"id": "dessert", "kind": "concept", "aliases": ["sweet tooth"]}],
                **changes,
            }

        graph.import_observation(item(0), now=now)
        memory = ContextMemory(learning)
        candidates = memory.candidates("sweet tooth", guild_id=77, now=now)
        require(
            "CONNECTED REVIEWED MEMORY" in memory.render(candidates, now=now, verified_after=now)
        )
        require(not graph.lookup("sweet tooth", guild_id=78, now=now))
        results.append({"id": "connected-recall-guild-scope", "passed": True})
        graph.import_observation(item(1, contradicts=["choice0"]), now=now)
        conflict = graph.lookup("sweet tooth", guild_id=77, now=now)
        require(len(conflict) == 2 and all(x["status"] == "contested" for x in conflict))
        results.append({"id": "contradictory-preference", "passed": True})
        with (
            closing(sqlite3.connect(graph.path)) as source,
            closing(sqlite3.connect(root / "restore.sqlite3")) as restored,
        ):
            source.backup(restored)
            require(restored.execute("PRAGMA quick_check").fetchone()[0] == "ok")
        (root / "restore.sqlite3").chmod(0o600)
        recovered = GraphStore(learning)
        recovered.path = root / "restore.sqlite3"
        require(recovered.status() == graph.status())
        results.append({"id": "online-backup-disposable-restore", "passed": True})
        learning.invalidate(10, [identifier], deleted=False, now=now)
        require(len(recovered.lookup("sweet tooth", guild_id=77, now=now)) == 1)
        require(len(graph.lookup("sweet tooth", guild_id=77, now=now)) == 1)
        learning.invalidate(10, [identifier + 1], deleted=True, now=now)
        require(not recovered.lookup("sweet tooth", guild_id=77, now=now))
        results.append({"id": "edit-delete-stale-restoration", "passed": True})
        raw = b"peer\n  8:00 AM\nI like chocolate.\nlegacy.target\n  8:01 AM\nI like caramel."
        archive.import_document(
            raw,
            channel="synthetic",
            target_alias="legacy.target",
            alias_basis="Synthetic operator approval",
            origin={"kind": "synthetic"},
            now=now,
        )
        digest = hashlib.sha256(raw).hexdigest()
        personal = item(0)
        personal["supports"] = [{"kind": "slack", "document": digest, "ordinal": 0}]
        try:
            graph.import_observation(personal, now=now)
            raise AssertionError("Peer evidence accepted")
        except LearningUnavailable:
            pass
        personal["supports"][0]["ordinal"] = 1
        graph.import_observation(personal, now=now)
        require(graph.lookup("sweet tooth", guild_id=77, now=now)[0]["unknown_date"])
        archive.remove_document(digest, now=now)
        require(not graph.lookup("sweet tooth", guild_id=77, now=now))
        results.append({"id": "peer-exclusion-unknown-dates-suppression", "passed": True})
        saved = graph.path.read_bytes()
        learning.forget(now=now)
        require(not graph.path.exists())
        graph.path.write_bytes(saved)
        graph.path.chmod(0o600)
        try:
            graph.lookup("sweet tooth", guild_id=77, now=now)
            raise AssertionError("Withdrawal bypassed")
        except LearningUnavailable:
            pass
        results.append({"id": "loaded-client-withdrawal-stale-restore", "passed": True})
    return {
        "synthetic_only": True,
        "no_api_calls": True,
        "no_discord_writes": True,
        "cases": results,
    }


if __name__ == "__main__":
    try:
        print(json.dumps(evaluate()))
    except Exception as error:
        raise SystemExit("Synthetic graph acceptance failed: " + type(error).__name__) from None
