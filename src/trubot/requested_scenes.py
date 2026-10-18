"""Explicit public-scene requests with durable, bounded paid-side-effect claims."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sqlite3
from collections.abc import Awaitable, Callable, Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal, Protocol

from trubot.aurora_image import AuroraImage
from trubot.learning import LearningUnavailable, _private, _time

MAX_REQUEST_AGE = timedelta(minutes=5)
IMAGE_COOLDOWN = timedelta(minutes=10)
DAILY_LIMIT = 3
Claim = Literal["claimed", "duplicate", "limited", "blocked"]
# A full grammar, not keyword co-occurrence. Unsupported modifiers stay with the
# ordinary responder rather than silently authorizing a different paid picture.
_REQUEST = re.compile(
    r"^(?:(?:can|could|would|will) you |please )?"
    r"(?:generate|create|draw|make)(?: me| us)? "
    r"(?:(?:an?|one) )?(?:(?:original|generated|ai[- ]generated) )?"
    r"(?:"
    r"(?:northern[- ]lights|aurora)(?: (?:picture|image|scene|illustration))?"
    r"|(?:picture|image|scene|illustration) (?:of|with) (?:the )?(?:northern[- ]lights|aurora)"
    r") (?:over |above )?(?:lake superior )?(?:near |at |over |in |from )?"
    r"(?P<region>marquette|munising|(?:the )?keweenaw(?: peninsula)?)"
    r"(?:,? please)?[.!?]?$",
    re.IGNORECASE,
)


def requested_region(content: str, *, bot_user_id: int) -> str | None:
    if len(content) > 300:
        return None
    text = content.strip()
    for prefix in ("🤖", f"<@{bot_user_id}>", f"<@!{bot_user_id}>"):
        if text.startswith(prefix):
            text = text[len(prefix) :].strip()
            break
    match = _REQUEST.fullmatch(text)
    if match is None:
        life = re.fullmatch(
            r"(?:(?:can|could|would|will) you |please )?(?:generate|create|draw|make)(?: me| us)? "
            r"(?:an?|one) (?:(?:original|generated|ai[- ]generated) )?"
            r"(?P<scene>trail[- ]camera|woodpile|lake view|lake freezing|lake thawing) "
            r"(?:picture|image|scene|illustration) (?:in|of) (?:the )?"
            r"(?:u\.?p\.?|upper peninsula)[.!?]?",
            text,
            re.I,
        )
        return (
            {
                "trail-camera": "trail_camera",
                "trail camera": "trail_camera",
                "woodpile": "woodpile",
                "lake view": "lake_view",
                "lake freezing": "lake_freeze",
                "lake thawing": "lake_thaw",
            }.get(life["scene"].lower())
            if life
            else None
        )
    region = match["region"].casefold()
    return "the Keweenaw" if "keweenaw" in region else region.title()


def operation_key(*parts: int) -> str:
    """Persist operational hashes, never message text or raw Discord account IDs."""
    return hashlib.sha256(":".join(str(part) for part in parts).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class SceneRequest:
    message_id: int
    author_id: int = field(repr=False)
    content: str = field(repr=False)
    created_at: datetime
    edited_at: datetime | None


class SceneStore:
    def __init__(self, path: Path) -> None:
        self.path = path.absolute()

    @classmethod
    def initialize(cls, path: Path) -> SceneStore:
        info = path.parent.lstat()
        if path.parent.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise LearningUnavailable("Private app directory required")
        with path.open("xb"):
            pass
        path.chmod(0o600)
        with closing(sqlite3.connect(path)) as db:
            db.executescript(
                "PRAGMA user_version=1; CREATE TABLE requests ("
                "request_key TEXT PRIMARY KEY, channel_key TEXT NOT NULL, "
                "created_at TEXT NOT NULL, status TEXT NOT NULL);"
                "CREATE INDEX request_time ON requests(created_at);"
            )
        return cls(path)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            _private(self.path)
            with closing(sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True)) as db:
                db.execute("PRAGMA synchronous=FULL")
                db.execute("BEGIN IMMEDIATE")
                if db.execute("PRAGMA user_version").fetchone()[0] != 1:
                    raise LearningUnavailable("Unsupported requested-scene state schema")
                with db:
                    yield db
        except (OSError, sqlite3.Error) as error:
            raise LearningUnavailable("Requested-scene state unavailable") from error

    def claim(self, request_key: str, channel_key: str, *, now: datetime) -> Claim:
        at = _time(now)
        with self.transaction() as db:
            if db.execute("SELECT 1 FROM requests WHERE request_key=?", (request_key,)).fetchone():
                return "duplicate"
            day = now.astimezone(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
            # A global limit covers all allowed channels and parallel processes.
            count = db.execute(
                "SELECT COUNT(*) FROM requests WHERE created_at>=? AND status!='limited'",
                (_time(day),),
            ).fetchone()[0]
            latest = db.execute(
                "SELECT MAX(created_at) FROM requests WHERE status!='limited'"
            ).fetchone()[0]
            limited = count >= DAILY_LIMIT
            if latest is not None:
                limited |= now - datetime.fromisoformat(latest) < IMAGE_COOLDOWN
            status: Claim = "limited" if limited else "claimed"
            db.execute(
                "INSERT INTO requests VALUES (?,?,?,?)", (request_key, channel_key, at, status)
            )
            # Older requests cannot re-enter: the handler requires a fresh human anchor.
            db.execute(
                "DELETE FROM requests WHERE created_at<?", (_time(now - timedelta(days=35)),)
            )
            return status

    def finish(self, request_key: str, status: str) -> None:
        expected = "send_uncertain" if status == "posted" else "claimed"
        if status not in {"posted", "failed", "blocked", "send_uncertain"}:
            raise ValueError("Invalid requested-scene outcome")
        with self.transaction() as db:
            if (
                db.execute(
                    "UPDATE requests SET status=? WHERE request_key=? AND status=?",
                    (status, request_key, expected),
                ).rowcount
                != 1
            ):
                raise LearningUnavailable("Invalid requested-scene state transition")


class RequestedImageGenerator(Protocol):
    async def generate_requested(self, region: str, *, purpose: str) -> AuroraImage: ...


@dataclass(frozen=True)
class RequestedScenes:
    store: SceneStore
    images: RequestedImageGenerator
    purpose: str = "runtime"

    async def prepare(
        self,
        region: str,
        *,
        request_key: str,
        channel_key: str,
        now: datetime,
        before_generation: Callable[[], Awaitable[bool]],
    ) -> tuple[Claim, AuroraImage | None]:
        claim = await asyncio.to_thread(self.store.claim, request_key, channel_key, now=now)
        if claim != "claimed":
            return claim, None
        try:
            if not await before_generation():
                await asyncio.to_thread(self.store.finish, request_key, "blocked")
                return "blocked", None
            image = await self.images.generate_requested(region, purpose=self.purpose)
        except BaseException:
            # Never reopen a claim after cancellation or an ambiguous paid request.
            await asyncio.to_thread(self.store.finish, request_key, "failed")
            raise
        return "claimed", image


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize or inspect requested-scene claims")
    parser.add_argument("command", choices=("init", "status"))
    parser.add_argument(
        "--path", type=Path, default=Path("/var/lib/trubot/requested-scenes.sqlite3")
    )
    args = parser.parse_args()
    try:
        store = (
            SceneStore.initialize(args.path) if args.command == "init" else SceneStore(args.path)
        )
        with store.transaction() as db:
            print(
                json.dumps(
                    {
                        "requests": dict(
                            db.execute("SELECT status,COUNT(*) FROM requests GROUP BY status")
                        )
                    }
                )
            )
    except (LearningUnavailable, OSError):
        raise SystemExit("Requested-scene state unavailable") from None


if __name__ == "__main__":
    main()
