"""Public-data aurora opportunities, never claims of a witnessed local sighting."""

from __future__ import annotations

import argparse
import asyncio
import calendar
import json
import math
import os
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import aiohttp

from trubot.learning import LearningUnavailable, _private

EASTERN = ZoneInfo("America/Detroit")
KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
USER_AGENT = "Trubot aurora (https://github.com/jdegregorio/wcb-discord-bot)"
MAX_FEED_BYTES = 4_000_000


@dataclass(frozen=True, slots=True)
class Region:
    station: str
    name: str
    latitude: float
    longitude: float


REGIONS = (
    Region("KCMX", "the Keweenaw", 47.168, -88.489),
    Region("KSAW", "Marquette", 46.354, -87.395),
    Region("KP53", "Munising", 46.412, -86.657),
)


@dataclass(frozen=True, slots=True)
class Opportunity:
    morning: str
    station: str
    region: str
    kp: float
    observations: tuple[str, ...]


def morning_window(now: datetime) -> tuple[datetime, datetime] | None:
    """A local calendar night, including DST changes, with a bounded posting window."""
    if now.tzinfo is None:
        raise ValueError("Timezone-aware clock required")
    local = now.astimezone(EASTERN)
    if not 8 <= local.hour < 11:
        return None
    end = datetime.combine(local.date(), datetime.min.time(), EASTERN).replace(hour=6)
    start = datetime.combine(local.date() - timedelta(days=1), datetime.min.time(), EASTERN)
    return start.replace(hour=18).astimezone(UTC), end.astimezone(UTC)


def _time(value: Any, *, noaa_utc: bool = False) -> datetime:
    if not isinstance(value, str):
        raise ValueError("Missing timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        if not noaa_utc:
            raise ValueError("Missing timestamp zone")
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def solar_elevation(at: datetime, region: Region) -> float:
    """NOAA fractional-year solar-position approximation, degrees above horizon."""
    utc = at.astimezone(UTC)
    hour = utc.hour + utc.minute / 60 + utc.second / 3600
    gamma = (
        2
        * math.pi
        / (366 if calendar.isleap(utc.year) else 365)
        * (utc.timetuple().tm_yday - 1 + (hour - 12) / 24)
    )
    eqtime = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )
    decl = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148 * math.sin(3 * gamma)
    )
    angle = math.radians((hour * 60 + eqtime + 4 * region.longitude) / 4 - 180)
    latitude = math.radians(region.latitude)
    cosine = math.sin(latitude) * math.sin(decl) + math.cos(latitude) * math.cos(decl) * math.cos(
        angle
    )
    return 90 - math.degrees(math.acos(max(-1, min(1, cosine))))


def _clear(properties: dict[str, Any]) -> bool:
    layers = properties.get("cloudLayers")
    visibility = properties.get("visibility")
    if not isinstance(visibility, dict) or visibility.get("unitCode") != "wmoUnit:m":
        return False
    distance = visibility.get("value")
    if (
        not isinstance(distance, int | float)
        or isinstance(distance, bool)
        or not math.isfinite(distance)
        or distance < 8_000
    ):
        return False
    if visibility.get("qualityControl") not in {"C", "V", "S"}:
        return False
    # Empty or missing layers do not establish clear sky. KP53 often lacks this field.
    return (
        isinstance(layers, list)
        and bool(layers)
        and all(isinstance(x, dict) and x.get("amount") in {"CLR", "SKC", "FEW"} for x in layers)
        and properties.get("presentWeather") == []
    )


def select_opportunity(
    kp_rows: Any, observations: dict[str, Any], *, now: datetime
) -> Opportunity | None:
    window = morning_window(now)
    if window is None:
        return None
    start, end = window
    if not isinstance(kp_rows, list) or not 1 <= len(kp_rows) <= 100:
        raise ValueError("Invalid observed activity feed")
    periods: list[tuple[datetime, float]] = []
    for row in kp_rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid observed activity row")
        at = _time(row.get("time_tag"), noaa_utc=True)
        kp, stations = row.get("Kp"), row.get("station_count")
        if (
            not isinstance(kp, int | float)
            or isinstance(kp, bool)
            or not math.isfinite(kp)
            or not 0 <= kp <= 9
        ):
            raise ValueError("Invalid observed activity value")
        if type(stations) is not int or stations < 6:
            continue
        if at + timedelta(hours=3) <= now:
            periods.append((at, float(kp)))
    if not periods or max(at for at, _ in periods) < end - timedelta(hours=3):
        raise ValueError("Observed activity feed does not cover the completed night")
    if len({at for at, _ in periods}) != len(periods):
        raise ValueError("Ambiguous activity timestamps")
    candidates = []
    for region in REGIONS:
        feed = observations.get(region.station)
        if not isinstance(feed, dict) or not isinstance(feed.get("features"), list):
            continue
        if len(feed["features"]) > 500:
            raise ValueError("Weather feed exceeds its bound")
        for at, kp in periods:
            if kp < 5 or at >= end or at + timedelta(hours=3) <= start:
                continue
            times = set()
            for row in feed["features"]:
                try:
                    props = row["properties"]
                    observed = _time(props.get("timestamp"))
                    if (
                        start <= observed < end
                        and at <= observed < at + timedelta(hours=3)
                        and _clear(props)
                        and solar_elevation(observed, region) <= -12
                    ):
                        times.add(observed)
                except (ValueError, TypeError, KeyError, AttributeError):
                    continue
            if len(times) < 2 or max(times) - min(times) < timedelta(minutes=30):
                continue
            candidates.append(
                Opportunity(
                    now.astimezone(EASTERN).date().isoformat(),
                    region.station,
                    region.name,
                    kp,
                    tuple(t.isoformat() for t in sorted(times)),
                )
            )
    return max(candidates, key=lambda c: (c.kp, len(c.observations), c.station), default=None)


async def _fetch(
    session: aiohttp.ClientSession, url: str, params: dict[str, str] | None = None
) -> Any:
    async with session.get(url, params=params, allow_redirects=False) as response:
        response.raise_for_status()
        if response.status != 200:
            raise ValueError("Unexpected feed response")
        data = bytearray()
        async for chunk in response.content.iter_chunked(65_536):
            if len(data) + len(chunk) > MAX_FEED_BYTES:
                raise ValueError("Public feed exceeds its byte bound")
            data.extend(chunk)
        return json.loads(data)


async def collect_opportunity(*, now: datetime) -> Opportunity | None:
    window = morning_window(now)
    if window is None:
        return None
    async with aiohttp.ClientSession(
        headers={"User-Agent": USER_AGENT, "Accept": "application/geo+json, application/json"},
        timeout=aiohttp.ClientTimeout(total=20),
    ) as session:
        kp_rows = await _fetch(session, KP_URL)
        start, end = window
        params = {"start": start.isoformat(), "end": end.isoformat(), "limit": "500"}
        # Station failures remain unknown, never clear. Other regions can still qualify.
        results = await asyncio.gather(
            *(
                _fetch(
                    session, f"https://api.weather.gov/stations/{r.station}/observations", params
                )
                for r in REGIONS
            ),
            return_exceptions=True,
        )
        return select_opportunity(
            kp_rows,
            {
                r.station: data
                for r, data in zip(REGIONS, results, strict=True)
                if not isinstance(data, BaseException)
            },
            now=now,
        )


class AuroraStore:
    """Content-free durable one-attempt-per-night claims, shared across restarts."""

    def __init__(self, path: Path) -> None:
        self.path = path.absolute()

    @classmethod
    def initialize(cls, path: Path) -> AuroraStore:
        store = cls(path)
        info = path.parent.lstat()
        if path.parent.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise LearningUnavailable("Private app directory required")
        with path.open("xb"):
            pass
        path.chmod(0o600)
        with closing(sqlite3.connect(path)) as db:
            db.executescript(
                "PRAGMA user_version=1; CREATE TABLE nights (morning TEXT PRIMARY KEY, "
                "status TEXT NOT NULL, evidence TEXT NOT NULL, message_id TEXT);"
            )
        return store

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        _private(self.path)
        with closing(sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True)) as db:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("BEGIN IMMEDIATE")
            if db.execute("PRAGMA user_version").fetchone()[0] != 1:
                raise LearningUnavailable("Unsupported aurora state schema")
            with db:
                yield db

    def seen(self, morning: str) -> bool:
        with self.transaction() as db:
            return (
                db.execute("SELECT 1 FROM nights WHERE morning=?", (morning,)).fetchone()
                is not None
            )

    def claim(self, opportunity: Opportunity) -> bool:
        with self.transaction() as db:
            cursor = db.execute(
                "INSERT OR IGNORE INTO nights VALUES (?, 'attempting', ?, NULL)",
                (opportunity.morning, json.dumps(asdict(opportunity))),
            )
            cutoff = (date.fromisoformat(opportunity.morning) - timedelta(days=35)).isoformat()
            db.execute("DELETE FROM nights WHERE morning<?", (cutoff,))
            return cursor.rowcount == 1

    def finish(self, morning: str, status: str, message_id: int | None = None) -> None:
        if status not in {"posted", "failed", "deferred", "send_uncertain"}:
            raise ValueError("Invalid aurora outcome")
        with self.transaction() as db:
            db.execute(
                "UPDATE nights SET status=?,message_id=? WHERE morning=?",
                (status, str(message_id) if message_id else None, morning),
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize or inspect public aurora post state")
    parser.add_argument("command", choices=("init", "status"))
    parser.add_argument("--path", type=Path, default=Path("/var/lib/trubot/aurora.sqlite3"))
    args = parser.parse_args()
    try:
        store = (
            AuroraStore.initialize(args.path) if args.command == "init" else AuroraStore(args.path)
        )
        with store.transaction() as db:
            print(
                json.dumps(
                    {
                        "nights": dict(
                            db.execute(
                                "SELECT status,COUNT(*) FROM nights GROUP BY status"
                            ).fetchall()
                        )
                    }
                )
            )
    except (OSError, ValueError, sqlite3.Error, LearningUnavailable):
        parser.exit(2, "Aurora state unavailable; inspect private app storage.\n")
