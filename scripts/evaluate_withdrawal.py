"""Probe withdrawal and stale recovery in disposable synthetic state only."""

from __future__ import annotations

import asyncio
import json
import sqlite3
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import discord

from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable, SourceMessage


def evaluate() -> dict[str, object]:
    now = datetime.now(UTC)
    created = now - timedelta(days=1)
    message_id = discord.utils.time_snowflake(created)
    audit = {
        "verified": True,
        "exact_name_match": True,
        "user_id": "42",
        "guild_id": "77",
        "username": "synthetic-person",
        "member_username": "synthetic-person",
        "allowed_channel_ids": ["10"],
        "source_channels": ["10"],
        "message_ids": [str(message_id)],
        "observed_at": now.isoformat(),
    }
    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="trubot-withdrawal-probe-") as temporary:
        directory = Path(temporary)
        store = LearningStore.initialize(directory / "learning.sqlite3", audit, now=now)
        source = SourceMessage(
            message_id, 10, 77, 42, False, False, created, None, now, "Synthetic preference only."
        )
        store.observe(source, now=now)
        usage = directory / "usage.sqlite3"
        usage.write_bytes(b"synthetic spending state")
        copies = directory / "backups"
        copies.mkdir(mode=0o700)
        copy = copies / "learning-synthetic.sqlite3"
        with sqlite3.connect(store.path) as connection, sqlite3.connect(copy) as target:
            connection.backup(target)
        copy.chmod(0o600)
        saved = copy.read_bytes()
        audit_path = directory / "identity-audit.json"
        audit_path.write_text(json.dumps(audit))
        audit_path.chmod(0o600)
        supported = hasattr(store, "forget")
        learner = MessageIngestor(store, frozenset({10}), clock=lambda: now)
        learner.verified = True
        if supported:
            store.forget(now=now)
        else:
            # Existing runbook revocation removes the store and audit. A stale
            # recovery then restores exactly the old pinned identity and text.
            store.path.unlink()
            audit_path.unlink()
        checks["withdrawal_command_available"] = supported
        checks["known_learning_copies_removed"] = not copy.exists()
        checks["spending_state_preserved"] = usage.read_bytes() == b"synthetic spending state"
        store.path.write_bytes(saved)
        reopened = LearningStore(store.path)
        try:
            reopened.identity()
        except LearningUnavailable:
            checks["stale_restore_identity_blocked"] = True
        else:
            checks["stale_restore_identity_blocked"] = False
        try:
            reopened.observe(source, now=now)
        except LearningUnavailable:
            checks["stale_restore_intake_blocked"] = True
        else:
            checks["stale_restore_intake_blocked"] = False
        if supported:
            client = MagicMock(spec=discord.Client)
            asyncio.run(learner.cycle(client))
            checks["loaded_worker_stops_without_discord_reads"] = (
                not learner.verified and not client.get_guild.called
            )
            reopened.forget(now=now)
            checks["cleanup_retry_erases_restored_data"] = reopened.status()["messages"] == 0
        else:
            checks["loaded_worker_stops_without_discord_reads"] = False
            checks["cleanup_retry_erases_restored_data"] = False
    return {
        "time": now.isoformat(),
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "provider_calls": 0,
        "discord_reads": 0,
        "discord_writes": 0,
        "fixture_privacy": "synthetic disposable learning store",
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
