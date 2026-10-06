# Private API usage state

Production uses `/srv/app-data/wcb-bot/usage.sqlite3`, bind-mounted at
`/var/lib/trubot/usage.sqlite3`. The platform Compose file owns this mapping.
The directory is `10001:10001` with mode `0700`; the database is mode `0600`.
The root filesystem remains read-only and `/tmp` remains ephemeral. No paid
storage service is added. Do not mount secrets or learning data into public Git.

## Initialization and inspection

Prepare the directory for the image's UID/GID 10001 before deploying 2.2.0.
Initialize explicitly once, using `trubot-budget init` in the released image with
the persistent directory mounted. Never repeat initialization on an existing or
lost production ledger. Initialization refuses to overwrite a file; runtime
startup and every reservation fail closed when state is missing or unsafe.

Read content-free status with:

```sh
ssh pi5 'docker exec wcb-bot trubot-budget status'
```

The UTC calendar-month cap is USD 20, with USD 18 reserved for runtime and USD 2
for maintenance. The evaluator uses maintenance, reads the configured ledger
path, and never posts to Discord. Future learning jobs must use the same ledger
and maintenance allocation. No raw messages, personal beliefs, or Discord IDs
are stored in this schema. Records contain model, controlled mode/purpose,
pricing version, source time of the API attempt, reservation, token counts, and
estimated cost. The first covered month's earlier app spending is unknown.

## Reservations, retention, and correction

Reservations commit before API I/O. Each retry gets a new reservation, with
hidden SDK retries disabled. Empty generations and abstentions reconcile usage
before response processing. Missing usage, errors, cancellation, and process
crashes retain the full reservation; unresolved entries carry into later months.
A request crossing a UTC month boundary counts in both months. Unknown models,
large input bounds, ledger failure, or provider usage exceeding a reservation
stop generation. An overrun latches the ledger for operator reconciliation.

Token counts are measured. Dollar amounts are conservative estimates using
standard global GPT-6 Luna rates verified on 2026-10-06. All noncached input
uses the cache-write upper rate (USD 0.125 per million), cached input uses
USD 0.01, and output uses USD 0.50, including reasoning. Input reserves use UTF-8
serialized bytes plus 4,096 framing tokens, capped below the long-context
threshold; output uses the actual requested ceiling. No tools or regional
endpoints are enabled. Rate changes require a reviewed pricing/code update;
this is an application guard, not an OpenAI account billing limit.

Settled rows older than 13 months are removed at month transition. Unresolved
charges remain until billing evidence supports correction. Never clear them
because a request probably failed. Corrections require stopping this app,
preserving a backup, matching provider billing evidence, reviewing the affected
row/month, and recording a dated content-free operator note. Clear a halted
flag only after restoring conservative totals. The scheduled agent owns this
work; league messages cannot authorize changes.

## Backup, restoration, and deletion

Use SQLite's online backup API for a consistent copy while the bot runs:

```sh
ssh pi5 'docker exec -i wcb-bot python -' <<'PYTHON'
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

directory = Path("/var/lib/trubot/backups")
directory.mkdir(mode=0o700, exist_ok=True)
backup = directory / ("usage-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + ".sqlite3")
backup.open("xb").close()
backup.chmod(0o600)
with closing(sqlite3.connect("file:/var/lib/trubot/usage.sqlite3?mode=ro", uri=True)) as source:
    with closing(sqlite3.connect(backup)) as target:
        source.backup(target)
        target.commit()
        assert target.execute("PRAGMA quick_check").fetchone()[0] == "ok"
PYTHON
```

Keep backup directories mode `0700`, database files mode `0600`, and include
this directory in the platform's encrypted off-device backup. This run verifies
an on-host backup/restore probe; off-device backup coverage must be checked
before relying on it for disaster recovery.

Stop only `wcb-bot` before restoration. Verify the backup with `PRAGMA quick_check`,
restore as UID/GID 10001 with mode `0600`, and account conservatively for requests
since that backup. Never restore an older balance without reconstructing those
charges. Start through the existing `pi-app` transaction and verify status plus
Discord readiness. Runtime opening does not restore or create missing state.

Deletion removes only this app's ledger and its copies after stopping it, with
explicit operator authorization and a preservation decision for billing records.
Deleting state also disables API calls. Recommissioning requires a reconstructed
current-month balance or withholding calls through the next UTC month; an empty
ledger must never be used as a spending reset. Future personal learning data
will require its own retention and deletion contract before ingestion starts.

## Image rollback

Version 2.2.0 introduces schema 1 and no personal learning data. Image rollback
through `pi-app rollback wcb-bot` retains the volume and its accounting evidence.
The previous 2.1.2 image does not enforce the guard, so record that limitation
and keep the rollback brief. Reject a regressed release from stable discovery
before rollback so the release timer cannot reintroduce it.
