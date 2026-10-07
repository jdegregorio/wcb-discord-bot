"""Private, attributed Discord evidence. Never a source of commands or identity changes."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import discord

MAX_RECORDS = 10_000
MAX_TEXT_CHARS = 4_000
_SCHEMA = """
PRAGMA user_version = 1;
CREATE TABLE identity (singleton INTEGER PRIMARY KEY CHECK(singleton=1), audit TEXT NOT NULL);
CREATE TABLE channels (id INTEGER PRIMARY KEY, cursor INTEGER NOT NULL);
CREATE TABLE messages (
    id INTEGER PRIMARY KEY, channel_id INTEGER NOT NULL, guild_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL, created_at TEXT NOT NULL, edited_at TEXT,
    observed_at TEXT NOT NULL, verified_at TEXT NOT NULL, content TEXT
);
CREATE INDEX verification_order ON messages(verified_at, id);
CREATE TABLE invalidations (
    id INTEGER PRIMARY KEY, channel_id INTEGER NOT NULL, observed_at TEXT NOT NULL,
    deleted INTEGER NOT NULL CHECK(deleted IN (0,1))
);
"""


class LearningUnavailable(RuntimeError):
    """Learning pauses without interrupting ordinary replies."""


def _private(path: Path) -> None:
    for item in (path.parent, path):
        info = item.lstat()
        if item.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise LearningUnavailable("Learning state must be owned by this user and private")


def _time(value: datetime) -> str:
    if value.tzinfo is None:
        raise LearningUnavailable("Evidence requires timezone-aware timestamps")
    return value.astimezone(UTC).isoformat()


@dataclass(frozen=True, slots=True)
class Identity:
    user_id: int = field(repr=False)
    guild_id: int = field(repr=False)
    channel_ids: frozenset[int] = field(repr=False)


@dataclass(frozen=True, slots=True)
class SourceMessage:
    id: int
    channel_id: int
    guild_id: int
    author_id: int
    bot: bool
    webhook: bool
    created_at: datetime
    edited_at: datetime | None
    observed_at: datetime
    content: str = field(repr=False)
    authoritative: bool = False

    @classmethod
    def from_discord(
        cls, message: discord.Message, *, observed_at: datetime, authoritative: bool = False
    ) -> SourceMessage:
        return cls(
            id=message.id,
            channel_id=message.channel.id,
            guild_id=message.guild.id if message.guild else 0,
            author_id=message.author.id,
            bot=message.author.bot,
            webhook=message.webhook_id is not None,
            created_at=message.created_at,
            edited_at=message.edited_at,
            observed_at=observed_at,
            content=message.content,
            authoritative=authoritative,
        )


class LearningStore:
    def __init__(self, path: Path, *, retention_days: int = 180) -> None:
        if not 1 <= retention_days <= 365:
            raise LearningUnavailable("Retention must be between 1 and 365 days")
        self.path = path
        self.retention_days = retention_days

    @classmethod
    def initialize(
        cls, path: Path, audit: dict[str, Any], *, now: datetime, retention_days: int = 180
    ) -> LearningStore:
        """Explicit operator action after authenticated attribution, never at runtime."""
        store = cls(path, retention_days=retention_days)
        identity = cls._identity(audit)
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        # Check the directory before writing personal data, then create exclusively.
        info = path.parent.lstat()
        if path.parent.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise LearningUnavailable("Unsafe learning directory")
        with path.open("xb"):
            pass
        path.chmod(0o600)
        floor = discord.utils.time_snowflake(now - timedelta(days=retention_days))
        with closing(sqlite3.connect(path)) as db:
            db.executescript(_SCHEMA)
            db.execute("INSERT INTO identity VALUES (1, ?)", (json.dumps(audit),))
            db.executemany(
                "INSERT INTO channels VALUES (?, ?)",
                [(channel_id, floor) for channel_id in identity.channel_ids],
            )
            db.commit()
        return store

    @staticmethod
    def _identity(audit: dict[str, Any]) -> Identity:
        try:
            channels = frozenset(int(value) for value in audit["allowed_channel_ids"])
            sources = {int(value) for value in audit["source_channels"]}
            ids = [int(value) for value in audit["message_ids"]]
            identity = Identity(int(audit["user_id"]), int(audit["guild_id"]), channels)
            _time(datetime.fromisoformat(audit["observed_at"]))
            if (
                audit["verified"] is not True
                or audit["exact_name_match"] is not True
                or not audit["username"]
                or audit["username"] != audit["member_username"]
                or not sources
                or not sources <= channels
                or not ids
                or min(*channels, *ids, identity.user_id, identity.guild_id) <= 0
            ):
                raise ValueError("Invalid audit")
        except (KeyError, TypeError, ValueError) as error:
            raise LearningUnavailable(
                "A corroborated, unambiguous operator audit is required"
            ) from error
        return identity

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            _private(self.path)
            with closing(
                sqlite3.connect(self.path.absolute().as_uri() + "?mode=rw", uri=True, timeout=1)
            ) as db:
                db.row_factory = sqlite3.Row
                db.execute("PRAGMA secure_delete = ON")
                db.execute("PRAGMA synchronous = FULL")
                db.execute("BEGIN IMMEDIATE")
                if db.execute("PRAGMA user_version").fetchone()[0] != 1:
                    raise LearningUnavailable("Unsupported learning schema")
                yield db
                db.commit()
        except (sqlite3.Error, OSError, TypeError, ValueError) as error:
            raise LearningUnavailable("Private learning state unavailable") from error

    @staticmethod
    def _read_identity(db: sqlite3.Connection) -> Identity:
        row = db.execute("SELECT audit FROM identity WHERE singleton=1").fetchone()
        if row is None:
            raise LearningUnavailable("Missing verified identity")
        return LearningStore._identity(json.loads(row[0]))

    def identity(self) -> Identity:
        with self._transaction() as db:
            if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise LearningUnavailable("Learning state failed integrity check")
            return self._read_identity(db)

    def cursor(self, channel_id: int, *, now: datetime) -> int:
        with self._transaction() as db:
            row = db.execute("SELECT cursor FROM channels WHERE id=?", (channel_id,)).fetchone()
            if row is None:
                raise LearningUnavailable("Channel was not approved at initialization")
            floor = discord.utils.time_snowflake(now - timedelta(days=self.retention_days))
            return max(int(row[0]), floor)

    def _upsert(self, db: sqlite3.Connection, message: SourceMessage, now: datetime) -> None:
        identity = self._read_identity(db)
        if (
            message.author_id != identity.user_id
            or message.guild_id != identity.guild_id
            or message.channel_id not in identity.channel_ids
            or message.bot
            or message.webhook
            or not now - timedelta(days=self.retention_days) <= message.created_at <= now
        ):
            return
        observed = _time(message.observed_at)
        invalid = db.execute("SELECT * FROM invalidations WHERE id=?", (message.id,)).fetchone()
        if invalid and (
            invalid["deleted"] or not message.authoritative or invalid["observed_at"] > observed
        ):
            return
        edited = _time(message.edited_at) if message.edited_at else None
        created = _time(message.created_at)
        existing = db.execute(
            "SELECT edited_at, created_at FROM messages WHERE id=?", (message.id,)
        ).fetchone()
        if existing and (existing["edited_at"] or existing["created_at"]) > (edited or created):
            return
        db.execute(
            "INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                message.id,
                message.channel_id,
                message.guild_id,
                message.author_id,
                created,
                edited,
                observed,
                observed,
                message.content[:MAX_TEXT_CHARS],
            ),
        )
        db.execute("DELETE FROM invalidations WHERE id=? AND deleted=0", (message.id,))

    def observe(self, message: SourceMessage, *, now: datetime) -> None:
        with self._transaction() as db:
            self._upsert(db, message, now)
            self._prune(db, now)

    def commit_batch(
        self, channel_id: int, messages: Sequence[SourceMessage], *, now: datetime
    ) -> None:
        """Evidence and scan checkpoint commit together, including non-target scan gaps."""
        if len(messages) > 100:
            raise LearningUnavailable("Unbounded history batch")
        with self._transaction() as db:
            identity = self._read_identity(db)
            if channel_id not in identity.channel_ids or any(
                message.channel_id != channel_id or message.guild_id != identity.guild_id
                for message in messages
            ):
                raise LearningUnavailable("History crossed the approved scope")
            for message in messages:
                self._upsert(db, message, now)
            if messages:
                db.execute(
                    "UPDATE channels SET cursor=MAX(cursor, ?) WHERE id=?",
                    (max(message.id for message in messages), channel_id),
                )
            self._prune(db, now)

    def invalidate(
        self, channel_id: int, message_ids: Sequence[int], *, deleted: bool, now: datetime
    ) -> None:
        with self._transaction() as db:
            if channel_id not in self._read_identity(db).channel_ids:
                return
            for message_id in message_ids:
                if discord.utils.snowflake_time(message_id) < now - timedelta(
                    days=self.retention_days
                ):
                    continue
                db.execute(
                    "INSERT INTO invalidations VALUES (?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                    "observed_at=MAX(observed_at, excluded.observed_at), "
                    "deleted=MAX(deleted, excluded.deleted)",
                    (message_id, channel_id, _time(now), int(deleted)),
                )
                # Never retain old text after an edit/deletion notice, even on fetch failure.
                if deleted:
                    db.execute(
                        "DELETE FROM messages WHERE id=? AND channel_id=?", (message_id, channel_id)
                    )
                else:
                    db.execute(
                        "UPDATE messages SET content=NULL WHERE id=? AND channel_id=?",
                        (message_id, channel_id),
                    )
            self._prune(db, now)

    def verification_targets(self, channel_id: int, *, limit: int = 2) -> list[int]:
        with self._transaction() as db:
            return [
                int(row[0])
                for row in db.execute(
                    "SELECT id FROM messages WHERE channel_id=? "
                    "ORDER BY content IS NOT NULL, verified_at, id LIMIT ?",
                    (channel_id, limit),
                )
            ]

    def _prune(self, db: sqlite3.Connection, now: datetime) -> None:
        cutoff = now - timedelta(days=self.retention_days)
        db.execute("DELETE FROM messages WHERE created_at < ?", (_time(cutoff),))
        db.execute(
            "DELETE FROM invalidations WHERE id < ?", (discord.utils.time_snowflake(cutoff),)
        )
        db.execute(
            "DELETE FROM messages WHERE id IN (SELECT id FROM messages "
            "ORDER BY created_at DESC, id DESC LIMIT -1 OFFSET ?)",
            (MAX_RECORDS,),
        )

    def prune(self, *, now: datetime) -> None:
        with self._transaction() as db:
            self._prune(db, now)

    def status(self) -> dict[str, int | str]:
        with self._transaction() as db:
            self._read_identity(db)
            return {
                "schema": 1,
                "retention_days": self.retention_days,
                "max_messages": MAX_RECORDS,
                "messages": db.execute(
                    "SELECT COUNT(*) FROM messages WHERE content IS NOT NULL"
                ).fetchone()[0],
                "pending_corrections": db.execute(
                    "SELECT COUNT(*) FROM messages WHERE content IS NULL"
                ).fetchone()[0],
                "deletion_markers": db.execute(
                    "SELECT COUNT(*) FROM invalidations WHERE deleted=1"
                ).fetchone()[0],
                "channels": db.execute("SELECT COUNT(*) FROM channels").fetchone()[0],
                "identity": "privately verified and pinned",
            }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Private Trubot learning state (no message output)"
    )
    parser.add_argument("command", choices=("init", "status"))
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(
            os.environ.get("TRUBOT_LEARNING_STORE_PATH", "/var/lib/trubot/learning.sqlite3")
        ),
    )
    parser.add_argument("--audit", type=Path)
    parser.add_argument(
        "--retention-days",
        type=int,
        default=int(os.environ.get("TRUBOT_LEARNING_RETENTION_DAYS", "180")),
    )
    args = parser.parse_args()
    try:
        store = LearningStore(args.path, retention_days=args.retention_days)
        if args.command == "init":
            if args.audit is None:
                raise LearningUnavailable("Initialization requires a private attribution audit")
            _private(args.audit)
            store = LearningStore.initialize(
                args.path,
                json.loads(args.audit.read_text()),
                now=datetime.now(UTC),
                retention_days=args.retention_days,
            )
        print(json.dumps(store.status(), indent=2))
    except (LearningUnavailable, OSError, ValueError):
        parser.exit(
            2, "Learning state unavailable; inspect private storage and attribution audit.\n"
        )


if __name__ == "__main__":
    main()
