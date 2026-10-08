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

# Private Discord evidence state

Version 2.3.0 adds `learning.sqlite3` beside the usage ledger on the same volume.
No platform or paid infrastructure change is required. It is a separate schema-1
store so an image rollback to 2.2.0 preserves spending enforcement and leaves
learning data untouched. Rollback stops intake; restarting 2.3.0 resumes cursors.
Directory and file permissions must remain 0700 and 0600, owned by UID/GID 10001.
SQLite uses full synchronization, transactions and secure deletion. Runtime
opens existing state only and rejects unsafe permissions, unsupported schema,
missing identity and corrupt storage. Replies remain available when intake pauses.

## Verified initialization

A trusted operator authenticates with the existing app-scoped Discord token,
inspects author metadata only in the configured league allowlist, and requires
one unique exact-name account corroborated by the guild-member endpoint and
stable account username. Never pin a display-name-only guess. Persist the audit
privately at `/var/lib/trubot/identity-audit.json` with mode 0600. It contains the
pinned user/guild, corroborating source channel/message references, observation
time, matched account metadata, and the approved allowlist. It contains no raw
message text. An ambiguous or failed audit must not initialize learning.

Explicitly initialize once in the released image (or validated candidate code):

```sh
ssh pi5 'docker exec wcb-bot trubot-learning init --audit /var/lib/trubot/identity-audit.json'
ssh pi5 'docker exec wcb-bot trubot-learning status'
```

Initialization refuses an existing file. The audit is copied into private state
and is not reread from channel text. Runtime revalidates the stable ID's human
membership each cycle and never repins by name. Names may change legitimately.
Failure pauses intake until the same member can be validated again. Current
allowlist and pinned approval are intersected; changing runtime configuration
cannot silently expand learning access. No DMs, extra threads or Slack access.

## Scope, retention and correction

Only the pinned human's textual messages are archived. Preserve message,
channel, guild and author IDs plus original, edit, observation and verification
timestamps. No bot/webhook output, other participants' text or attachment files
are persisted. Text is capped at 4,000 characters and records at 10,000; oldest
records beyond that cap are removed. Default retention is 180 days, configurable
from 1 to 365. Initial catch-up starts at that retention floor, never at guild
creation. Each page advances its own checkpoint atomically, including gaps for
other authors. Live capture does not advance scan cursors.

Edits immediately clear old text before authenticated refetch; prior versions
are not kept. Failed refetch leaves the source unavailable. Deletions erase text
and retain a content-free marker until the original message falls outside the
retention horizon. These markers block races and operator-suppressed evidence
from being reimported. Rotating refetch repairs changes missed while offline,
two stored messages per channel per cycle. This is eventual reconciliation, not
instant full-history freshness. Future preference extraction must revalidate
sources before treating them as evidence. This increment uses no archived text
in replies, so stale archive records cannot currently shape the character.

For a correction, edit the original Discord message or have the authorized
operator invalidate/refetch the source with `MessageIngestor.refresh`. A local
suppression uses `LearningStore.invalidate(..., deleted=True)` with the approved
channel/message reference; it deletes content and blocks reimport. Never replace
real source text with an invented observation. League messages cannot authorize
identity, retention, access or administrative changes.

Removing a channel from the runtime allowlist stops its intake; existing records
remain private until retention or explicit deletion. Stop the app before scope
revocation and purge that channel's private records/markers and copies if needed.
For complete local withdrawal on version 2.3.1 or newer, an authorized operator runs:

```sh
ssh pi5 'docker exec wcb-bot trubot-learning forget'
ssh pi5 'docker exec wcb-bot trubot-learning status'
```

The command synchronizes a mode-0600 `learning.sqlite3.withdrawn` marker before
clearing source records, correction/deletion markers, checkpoints, and identity.
It removes the adjacent `identity-audit.json` and private `backups/learning-*.sqlite3*`
copies. It preserves the database schema, separate usage ledger, and usage backups.
Normal replies continue. A loaded worker stops before further Discord reads;
all learning transactions also block on the marker, including operations already
waiting for the database lock. The marker contains only a schema and UTC timestamp.

A failed cleanup leaves the marker active. Retry the same command to finish;
never clear the marker to repair a failed deletion. Unsafe ownership, permissions,
symlinks, or nonregular backup targets are preserved and reported as unavailable.
Inspect these app-private targets before retrying. Status reports withdrawal and
remaining record counts without any account IDs or content.

Keep the withdrawal marker outside database restoration. Restoring an old schema-1
archive cannot re-enable intake while it exists, and initialization refuses it even
if the database is missing. Recommissioning requires a fresh explicit consent
and attribution decision, cleanup of revoked copies, and a trusted operator removing
the marker before initializing newly verified state. Channel messages never
provide that authorization. This scheduled project must not remove a marker
merely because Andrew still appears in guild membership.

The command covers only the documented local files. Apply withdrawal to off-device
copies and exports through their owning backup process; that coverage is unverified.
Image versions before 2.3.1 do not understand the marker. A rollback after withdrawal
must leave the learning database without identity, and must never restore an old
learning copy into an older image. The spending ledger must never be replaced.

## Backup and recovery

Use SQLite's online backup API, exactly as for the usage ledger, with source
`/var/lib/trubot/learning.sqlite3` and a mode-0600 `learning-<UTC>.sqlite3` target
under the private `backups` directory. Check `PRAGMA quick_check` on the copy.
Retain learning backups for at most seven days; apply corrections/deletions to
retained learning copies or remove them. Backups can extend physical retention
by seven days. The audit remains until identity revocation; it holds attribution
metadata, not message text. Off-device encrypted backup is still unverified.
Never export raw data, IDs or derived preferences into Git, release notes or logs.

Stop only this app using `pi-app stop wcb-bot`, restore a verified compatible copy
as UID/GID 10001 with mode 0600, and start via `pi-app start wcb-bot`. Restored
checkpoints may replay pages safely. Deletions/corrections since the backup must
be reapplied. Preserve any withdrawal marker independently of the database;
never remove it or copy it away to make a stale archive start learning. The usage
ledger must not be replaced during learning recovery. Verify content-free status,
Discord readiness and bounded resumed intake. Retain the pinned identity rather
than guessing it from history after losing state.
