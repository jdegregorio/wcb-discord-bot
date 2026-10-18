"""Private, restart-safe outdoor check-ins. Waking does not authorize publication."""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import sqlite3
from collections.abc import Awaitable, Callable, Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

import aiohttp

from trubot.aurora import EASTERN, USER_AGENT, _fetch, _time
from trubot.aurora_image import AuroraImage
from trubot.learning import LearningUnavailable, _private

FORECAST_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"
LIFE_SCENES = frozenset({"trail_camera", "woodpile", "lake_freeze", "lake_thaw"})


@dataclass(frozen=True, slots=True)
class Forecast:
    status: str
    promising: bool = False


def forecast(feed: Any, now: datetime) -> Forecast:
    """Only a recently anchored forecast can shorten a private check interval."""
    if not isinstance(feed, list) or not 1 <= len(feed) <= 100:
        return Forecast("unavailable")
    rows = []
    try:
        for row in feed:
            at = _time(row["time_tag"], noaa_utc=True)
            kp, kind = row["kp"], row["observed"]
            if (
                isinstance(kp, bool)
                or not isinstance(kp, int | float)
                or not math.isfinite(kp)
                or not 0 <= kp <= 9
                or kind not in {"observed", "estimated", "predicted"}
            ):
                return Forecast("unavailable")
            rows.append((at, float(kp), kind))
    except (KeyError, TypeError, ValueError):
        return Forecast("unavailable")
    if len({at for at, _, _ in rows}) != len(rows):
        return Forecast("unavailable")
    # A future prediction alone cannot establish that this is a fresh bulletin.
    if not any(
        now - timedelta(hours=6) <= at <= now and kind != "predicted" for at, _, kind in rows
    ):
        return Forecast("unavailable")
    upcoming = [
        kp
        for at, kp, kind in rows
        if now - timedelta(hours=3) < at <= now + timedelta(hours=6)
        and kind in {"estimated", "predicted"}
    ]
    if not upcoming:
        return Forecast("unavailable")
    return Forecast("available", max(upcoming) >= 5)


async def read_forecast(*, now: datetime) -> Forecast:
    try:
        async with aiohttp.ClientSession(
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=aiohttp.ClientTimeout(total=8),
            trust_env=False,
        ) as session:
            return forecast(await _fetch(session, FORECAST_URL), now)
    except (aiohttp.ClientError, TimeoutError, ValueError):
        return Forecast("unavailable")


def posting_window(now: datetime) -> bool:
    return 9 <= now.astimezone(EASTERN).hour < 21


def seasonal_scenes(now: datetime) -> tuple[str, ...]:
    month = now.astimezone(EASTERN).month
    if month in {9, 10, 11}:
        return ("woodpile", "trail_camera")
    if month in {12, 1, 2}:
        return ("lake_freeze", "trail_camera")
    if month in {3, 4, 5}:
        return ("lake_thaw", "trail_camera")
    return ("trail_camera",)


@dataclass(frozen=True, slots=True)
class OutdoorCandidate:
    # Common publication claim key with the legacy aurora feature's interface.
    morning: str
    scene: str


class OutdoorStore:
    """Operational decisions only. No private thoughts, source text or images."""

    def __init__(self, path: Path) -> None:
        self.path = path.absolute()

    @classmethod
    def initialize(cls, path: Path, *, now: datetime | None = None) -> OutdoorStore:
        info = path.parent.lstat()
        if path.parent.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise LearningUnavailable("Private app directory required")
        at = (now or datetime.now(UTC)).timestamp()
        with path.open("xb"):
            pass
        path.chmod(0o600)
        with closing(sqlite3.connect(path)) as db:
            db.executescript(
                "PRAGMA user_version=1; CREATE TABLE plan ("
                "id INTEGER PRIMARY KEY CHECK(id=1), next_at REAL NOT NULL, "
                "last_at REAL NOT NULL, started_at REAL NOT NULL);"
                "CREATE TABLE wakes (claim TEXT PRIMARY KEY, at REAL NOT NULL, "
                "reason TEXT NOT NULL, scene TEXT, status TEXT NOT NULL);"
                "CREATE INDEX wake_time ON wakes(at);"
            )
            db.execute("INSERT INTO plan VALUES (1, ?, ?, ?)", (at, at, at))
            db.commit()
        return cls(path)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        _private(self.path)
        with closing(sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True)) as db:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            if db.execute("PRAGMA user_version").fetchone()[0] != 1:
                raise LearningUnavailable("Unsupported outdoor state schema")
            with db:
                yield db

    def due(self, now: datetime) -> bool:
        with self.transaction() as db:
            row = db.execute("SELECT next_at,last_at FROM plan WHERE id=1").fetchone()
            if row is None:
                raise LearningUnavailable("Missing outdoor plan")
            return bool(now.timestamp() >= max(row))

    def wake(self, now: datetime) -> str | None:
        at = now.timestamp()
        with self.transaction() as db:
            row = db.execute("SELECT next_at,last_at FROM plan WHERE id=1").fetchone()
            if row is None:
                raise LearningUnavailable("Missing outdoor plan")
            if at < max(row):
                return None
            key = uuid4().hex
            # Commit a safe next wake BEFORE network, timing or paid I/O. No catch-up burst.
            db.execute("UPDATE plan SET next_at=?,last_at=? WHERE id=1", (at + 14400, at))
            db.execute("INSERT INTO wakes VALUES (?, ?, 'checking', NULL, 'quiet')", (key, at))
            db.execute("DELETE FROM wakes WHERE at<?", (at - 35 * 86400,))
            return key

    def reflect(
        self,
        key: str,
        *,
        now: datetime,
        signal: Forecast,
        next_minutes: int | None = None,
        consider_scene: bool = True,
    ) -> OutdoorCandidate | None:
        if next_minutes is not None and (
            type(next_minutes) is not int or next_minutes not in {20, 60, 240, 480}
        ):
            raise ValueError("Invalid next check interval")
        at = now.timestamp()
        local = now.astimezone(EASTERN)
        watch = (
            signal.promising
            and signal.status == "available"
            and (local.hour >= 18 or local.hour < 6)
        )
        with self.transaction() as db:
            if db.execute("SELECT last_at FROM plan WHERE id=1").fetchone() != (at,):
                return None
            row = db.execute("SELECT reason,status FROM wakes WHERE claim=?", (key,)).fetchone()
            if row != ("checking", "quiet"):
                return None
            minutes = next_minutes if next_minutes is not None else (20 if watch else 240)
            # No rapid polling without a fresh promising nighttime forecast.
            minutes = max(minutes, 20 if watch else 60)
            db.execute("UPDATE plan SET next_at=? WHERE id=1", (at + minutes * 60,))
            # Forecasts never constitute sighting confirmation. Automatic aurora posts
            # remain closed until a fresh, accessible local confirmation source is qualified.
            reason = (
                "aurora_unconfirmed"
                if watch
                else "forecast_unavailable"
                if signal.status != "available"
                else "routine"
            )
            attempts = db.execute(
                "SELECT at,scene FROM wakes WHERE scene IS NOT NULL ORDER BY at DESC"
            ).fetchall()
            started = db.execute("SELECT started_at FROM plan WHERE id=1").fetchone()[0]
            # Conservative attempts, including deferred/failed/uncertain, consume frequency.
            limited = at - started < 7 * 86400 or (attempts and at - attempts[0][0] < 7 * 86400)
            if limited or not posting_window(now) or not consider_scene:
                db.execute("UPDATE wakes SET reason=? WHERE claim=?", (reason, key))
                return None
            choices = seasonal_scenes(now)
            scene = next((s for s in choices if not attempts or s != attempts[0][1]), choices[0])
            db.execute(
                "UPDATE wakes SET reason='seasonal',scene=?,status='attempting' WHERE claim=?",
                (scene, key),
            )
            return OutdoorCandidate(key, scene)

    def quiet(self, key: str, reason: str) -> None:
        if reason not in {"scope_unavailable", "check_failed"}:
            raise ValueError("Invalid quiet check outcome")
        with self.transaction() as db:
            db.execute(
                "UPDATE wakes SET reason=? WHERE claim=? AND status='quiet' AND reason='checking'",
                (reason, key),
            )

    def finish(self, key: str, status: str, message_id: int | None = None) -> None:
        del message_id  # No raw Discord identifiers retained in the operational journal.
        if status not in {"posted", "failed", "deferred", "send_uncertain"}:
            raise ValueError("Invalid outdoor outcome")
        expected = "send_uncertain" if status == "posted" else "attempting"
        with self.transaction() as db:
            if (
                db.execute(
                    "UPDATE wakes SET status=? WHERE claim=? AND status=?",
                    (status, key, expected),
                ).rowcount
                != 1
            ):
                raise LearningUnavailable("Invalid outdoor state transition")

    def summary(self) -> dict[str, object]:
        with self.transaction() as db:
            row = db.execute("SELECT next_at FROM plan WHERE id=1").fetchone()
            if row is None:
                raise LearningUnavailable("Missing outdoor plan")
            return {
                "next_wake_utc": datetime.fromtimestamp(row[0], UTC).isoformat(),
                "wakes": db.execute("SELECT COUNT(*) FROM wakes").fetchone()[0],
                "outcomes": dict(db.execute("SELECT status,COUNT(*) FROM wakes GROUP BY status")),
                "reasons": dict(db.execute("SELECT reason,COUNT(*) FROM wakes GROUP BY reason")),
                "aurora_confirmation": "unavailable_no_automatic_aurora_posts",
            }


class LifeImages(Protocol):
    async def generate_life(self, scene: str, *, purpose: str = "runtime") -> AuroraImage: ...


class OutdoorFeature:
    def __init__(
        self,
        store: OutdoorStore,
        images: LifeImages,
        *,
        collect: Callable[..., Awaitable[Forecast]] = read_forecast,
        purpose: str = "runtime",
        planner: Callable[[Forecast, datetime], Awaitable[tuple[int, bool]]] | None = None,
    ) -> None:
        self.store, self.images, self.collect, self.purpose = store, images, collect, purpose
        self.planner = planner

    async def prepare(
        self,
        *,
        now: datetime,
        before_generation: Callable[[], Awaitable[bool]] | None = None,
        before_check: Callable[[], Awaitable[bool]] | None = None,
    ) -> tuple[OutdoorCandidate, AuroraImage] | None:
        key = await asyncio.to_thread(self.store.wake, now)
        if key is None:
            return None
        try:
            if before_check is not None and not await before_check():
                await asyncio.to_thread(self.store.quiet, key, "scope_unavailable")
                return None
            signal = await self.collect(now=now)
            if before_check is not None and not await before_check():
                await asyncio.to_thread(self.store.quiet, key, "scope_unavailable")
                return None
            interval, consider = (await self.planner(signal, now)) if self.planner else (None, True)
            candidate = await asyncio.to_thread(
                self.store.reflect,
                key,
                now=now,
                signal=signal,
                next_minutes=interval,
                consider_scene=consider,
            )
        except BaseException:
            await asyncio.to_thread(self.store.quiet, key, "check_failed")
            raise
        if candidate is None:
            return None
        try:
            if before_generation is not None and not await before_generation():
                await asyncio.to_thread(self.store.finish, key, "deferred")
                return None
            image = await self.images.generate_life(candidate.scene, purpose=self.purpose)
        except BaseException:
            await asyncio.to_thread(self.store.finish, key, "failed")
            raise
        return candidate, image


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize or inspect private outdoor check-ins")
    parser.add_argument("command", choices=("init", "status"))
    parser.add_argument("--path", type=Path, default=Path("/var/lib/trubot/outdoors.sqlite3"))
    args = parser.parse_args()
    try:
        store = (
            OutdoorStore.initialize(args.path)
            if args.command == "init"
            else OutdoorStore(args.path)
        )
        print(json.dumps(store.summary()))
    except (OSError, sqlite3.Error, ValueError, LearningUnavailable):
        parser.exit(2, "Outdoor state unavailable; inspect private app storage.\n")


if __name__ == "__main__":
    main()
