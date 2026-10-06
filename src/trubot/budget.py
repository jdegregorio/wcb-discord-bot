"""Content-free, fail-closed API spending ledger, using integer nanodollars."""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

NANODOLLARS = 1_000_000_000
MONTHLY_LIMIT = 20 * NANODOLLARS
RUNTIME_LIMIT = 18 * NANODOLLARS
MAINTENANCE_LIMIT = 2 * NANODOLLARS
PRICING_VERSION = "openai-standard-2026-10-06-cache-write-upper-bound"
PRICED_MODEL = "gpt-6-luna"
# Per-token nanodollars. Uncached input includes the maximum cache-write rate.
INPUT_RATE = 125
CACHED_RATE = 10
OUTPUT_RATE = 500
MAX_INPUT_BOUND = 200_000  # Below the provider's 272K long-context threshold.
_SCHEMA = """
PRAGMA user_version = 1;
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
INSERT INTO metadata VALUES ('halted', '0');
CREATE TABLE attempts (
    id TEXT PRIMARY KEY,
    month TEXT NOT NULL,
    settled_month TEXT,
    created_at TEXT NOT NULL,
    purpose TEXT NOT NULL CHECK (purpose IN ('runtime', 'maintenance')),
    mode TEXT NOT NULL,
    model TEXT NOT NULL,
    pricing_version TEXT NOT NULL,
    reserved INTEGER NOT NULL CHECK (reserved > 0),
    charged INTEGER CHECK (charged >= 0),
    status TEXT NOT NULL CHECK (status IN ('pending', 'uncertain', 'settled')),
    input_tokens INTEGER,
    cached_input_tokens INTEGER,
    output_tokens INTEGER
);
CREATE INDEX attempts_month ON attempts(month);
"""


class BudgetError(RuntimeError):
    """Generation must stop before making an unaccounted API call."""


class BudgetExceeded(BudgetError):
    """No room remains for a conservative reservation."""


class BudgetUnavailable(BudgetError):
    """Persistent state or pricing is unavailable or unsafe."""


@dataclass(frozen=True)
class Reservation:
    id: str
    amount: int


class UsageLedger:
    def __init__(
        self,
        path: Path,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.path = path
        self._clock = clock or (lambda: datetime.now(UTC))

    @classmethod
    def initialize(cls, path: Path) -> UsageLedger:
        """Explicit operator action only. Never overwrite or recreate runtime state."""
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with path.open("xb"):
            pass
        path.chmod(0o600)
        with closing(sqlite3.connect(path)) as db:
            db.executescript(_SCHEMA)
            db.execute(
                "INSERT INTO metadata VALUES ('coverage_start', ?)",
                (datetime.now(UTC).isoformat(),),
            )
            db.commit()
        return cls(path)

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            # mode=rw prevents missing state from silently resetting the allowance.
            with closing(
                sqlite3.connect(
                    self.path.resolve().as_uri() + "?mode=rw",
                    uri=True,
                    timeout=5,
                    isolation_level=None,
                )
            ) as db:
                db.row_factory = sqlite3.Row
                db.execute("PRAGMA synchronous = FULL")
                db.execute("BEGIN IMMEDIATE")
                if db.execute("PRAGMA user_version").fetchone()[0] != 1:
                    raise BudgetUnavailable("Unsupported usage ledger schema")
                if db.execute("SELECT value FROM metadata WHERE key='halted'").fetchone()[0] != "0":
                    raise BudgetUnavailable("Usage ledger requires operator reconciliation")
                yield db
                db.commit()
        except (sqlite3.Error, OSError, TypeError) as error:
            raise BudgetUnavailable("Usage ledger unavailable") from error

    def check(self) -> None:
        with self._transaction() as db:
            if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise BudgetUnavailable("Usage ledger failed integrity check")
            self._month(db)

    def _month(self, db: sqlite3.Connection) -> str:
        month = self._clock().astimezone(UTC).strftime("%Y-%m")
        row = db.execute("SELECT value FROM metadata WHERE key='last_month'").fetchone()
        if row and month < row[0]:
            raise BudgetUnavailable("Clock moved behind the usage ledger")
        if not row or row[0] != month:
            year, number = map(int, month.split("-"))
            index = year * 12 + number - 1 - 13
            cutoff = f"{index // 12:04d}-{index % 12 + 1:02d}"
            db.execute(
                "DELETE FROM attempts WHERE status='settled' AND month < ? AND settled_month < ?",
                (cutoff, cutoff),
            )
        db.execute("INSERT OR REPLACE INTO metadata VALUES ('last_month', ?)", (month,))
        return month

    @staticmethod
    def _totals(db: sqlite3.Connection, month: str) -> dict[str, int]:
        # Uncertain and crash-interrupted requests carry their full reservation into
        # every later month until billing evidence permits operator reconciliation.
        # Cross-month settlements conservatively count in both request/completion months.
        rows = db.execute(
            "SELECT purpose, SUM(CASE WHEN status='settled' THEN charged ELSE reserved END) "
            "FROM attempts WHERE month <= ? AND "
            "(month = ? OR status != 'settled' OR settled_month >= ?) GROUP BY purpose",
            (month, month, month),
        ).fetchall()
        totals = {"runtime": 0, "maintenance": 0}
        totals.update({row[0]: row[1] for row in rows})
        return totals

    def reserve(
        self, *, model: str, input_bound: int, output_bound: int, purpose: str, mode: str
    ) -> Reservation:
        if model != PRICED_MODEL:
            raise BudgetUnavailable("Model has no approved price")
        if not 0 < input_bound <= MAX_INPUT_BOUND or not 1 <= output_bound <= 4096:
            raise BudgetUnavailable("Request exceeds the priced token bounds")
        if purpose not in {"runtime", "maintenance"}:
            raise BudgetUnavailable("Unknown spending purpose")
        amount = input_bound * INPUT_RATE + output_bound * OUTPUT_RATE
        reservation = Reservation(uuid4().hex, amount)
        with self._transaction() as db:
            month = self._month(db)
            totals = self._totals(db, month)
            limit = RUNTIME_LIMIT if purpose == "runtime" else MAINTENANCE_LIMIT
            if sum(totals.values()) + amount > MONTHLY_LIMIT or totals[purpose] + amount > limit:
                raise BudgetExceeded("Monthly API allowance exhausted")
            db.execute(
                "INSERT INTO attempts (id,month,created_at,purpose,mode,model,pricing_version,"
                "reserved,status) VALUES (?,?,?,?,?,?,?,?,'pending')",
                (
                    reservation.id,
                    month,
                    self._clock().astimezone(UTC).isoformat(),
                    purpose,
                    mode,
                    model,
                    PRICING_VERSION,
                    amount,
                ),
            )
        return reservation

    def uncertain(self, reservation: Reservation) -> None:
        with self._transaction() as db:
            db.execute(
                "UPDATE attempts SET status='uncertain' WHERE id=? AND status='pending'",
                (reservation.id,),
            )

    def settle(
        self,
        reservation: Reservation,
        *,
        input_tokens: int,
        cached_input_tokens: int,
        output_tokens: int,
    ) -> int:
        tokens = (input_tokens, cached_input_tokens, output_tokens)
        if (
            any(type(value) is not int or value < 0 for value in tokens)
            or cached_input_tokens > input_tokens
        ):
            self.uncertain(reservation)
            raise BudgetUnavailable("Invalid provider token usage")
        cost = (
            (input_tokens - cached_input_tokens) * INPUT_RATE
            + cached_input_tokens * CACHED_RATE
            + output_tokens * OUTPUT_RATE
        )
        with self._transaction() as db:
            month = self._month(db)
            row = db.execute(
                "SELECT status,reserved,charged FROM attempts WHERE id=?", (reservation.id,)
            ).fetchone()
            if row is None:
                raise BudgetUnavailable("Reservation missing from usage ledger")
            if row[0] == "settled":
                raise BudgetUnavailable("Reservation already settled")
            db.execute(
                "UPDATE attempts SET status='settled',settled_month=?,charged=?,input_tokens=?,"
                "cached_input_tokens=?,output_tokens=? WHERE id=?",
                (month, cost, *tokens, reservation.id),
            )
            if cost > row[1]:
                db.execute("UPDATE metadata SET value='1' WHERE key='halted'")
        if cost > row[1]:
            raise BudgetUnavailable("Provider usage exceeded the reserved bound")
        return cost

    def summary(self) -> dict[str, object]:
        with self._transaction() as db:
            month = self._month(db)
            totals = self._totals(db, month)
            usage = db.execute(
                "SELECT COUNT(*),COALESCE(SUM(input_tokens),0),"
                "COALESCE(SUM(cached_input_tokens),0),"
                "COALESCE(SUM(output_tokens),0),SUM(status!='settled') FROM attempts WHERE month=?",
                (month,),
            ).fetchone()
            coverage_start = db.execute(
                "SELECT value FROM metadata WHERE key='coverage_start'"
            ).fetchone()[0]
            return {
                "month": month,
                "coverage_start": coverage_start,
                "timezone": "UTC",
                "pricing_version": PRICING_VERSION,
                "estimated_usd": sum(totals.values()) / NANODOLLARS,
                "runtime_usd": totals["runtime"] / NANODOLLARS,
                "maintenance_usd": totals["maintenance"] / NANODOLLARS,
                "monthly_limit_usd": 20,
                "runtime_limit_usd": 18,
                "maintenance_limit_usd": 2,
                "attempts": usage[0],
                "input_tokens": usage[1],
                "cached_input_tokens": usage[2],
                "output_tokens": usage[3],
                "unsettled_attempts": usage[4] or 0,
                "pre_guard_spend": "unknown; not included"
                if month == coverage_start[:7]
                else "none in this month",
            }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "status"))
    parser.add_argument("--path", type=Path, default=Path("/var/lib/trubot/usage.sqlite3"))
    args = parser.parse_args()
    try:
        ledger = (
            UsageLedger.initialize(args.path) if args.command == "init" else UsageLedger(args.path)
        )
        print(json.dumps(ledger.summary(), indent=2))
    except (BudgetError, OSError) as error:
        raise SystemExit(f"Usage ledger action failed: {type(error).__name__}") from None


if __name__ == "__main__":
    main()
