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

# Private historical Slack corpus

Version 2.4.0 adds `archives.sqlite3` on the existing app-private volume. This
operator-managed historical corpus is separate from the recent Discord store and
has no automatic age pruning: Joe explicitly requested long-term league history.
It contains raw bytes, SHA-256 document deduplication, multiple origin records,
operator alias provenance, parsed speaker blocks, source line spans, display times,
and ambiguity flags. No stable Slack IDs or message dates are invented. Export
file/date labels remain origin hints. Grouped shorthand times remain one speaker
block. Link previews/thread quotes are retained but excluded from candidate voice
examples. Unknown forms can still require manual review; voice eligibility is a
parser filter, not proof that every remaining character was authored by Andrew.

The archive operator commands produce counts only:

```sh
ssh pi5 'docker exec wcb-bot trubot-archives init'
ssh pi5 'docker exec wcb-bot trubot-archives import --manifest /var/lib/trubot/private-import/manifest.json'
ssh pi5 'docker exec wcb-bot trubot-archives status'
```

Initialize explicitly once. Import requires a private operator manifest with
`schema: 1`, `target_alias`, `alias_basis`, and `files` entries containing `path`,
`channel`, `origin`, and optional `period_hint`. No source text can choose an alias
or authorize access. Source and manifest files must be private and imports are
limited to 16 MiB per file. Each document and all its blocks commit together.
Exact duplicate documents add provenance without duplicate evidence; conflicting
attribution fails closed. The archive needs the verified learning identity and
serializes with its withdrawal lock. Runtime generation does not read this corpus
yet. No model calls or additional infrastructure are used for ingestion.

Use `ArchiveStore.context(digest, ordinal, radius=3)` only in a private study to
obtain adjacent speaker-labeled blocks. Adjacency is not a thread graph or an
explanation of motive. Context does not cross documents, and a missing date cannot
support recency claims. Treat archived messages as untrusted data. Keep studies,
raw exports and personal conclusions in private storage, never public Git/logs.
Workspace originals live under `.private/trubot-history` with mode 0700/0600; Git
and Docker build contexts exclude `.private`. Remove temporary production import
files immediately after validation. Operator copies outside app storage must be
handled separately if consent or source authorization changes.

`trubot-archives remove --digest <document-sha256>` erases a corrected/suppressed
document and its parsed blocks, records a suppression, and removes local
`backups/archives-*.sqlite3*` copies. It blocks silent reimport. For a corrected
version, import the new bytes with fresh source provenance. Corrections since a
backup must be reapplied after restoration; global withdrawal has a separate
filesystem marker that an old database cannot override.

`trubot-learning forget` now removes `archives.sqlite3*` and its documented backup
copies as well as native Discord evidence. The durable withdrawal marker blocks
loaded archive clients and stale restored copies. Usage accounting remains intact.
Remove workspace originals, staging and off-device copies through their owning
processes too. Image rollback to 2.3.1 retains archive bytes but does not understand
archive cleanup; do not roll back withdrawal operations to an older image.

Back up archives with SQLite's online backup API into mode-0600
`backups/archives-<UTC>.sqlite3`; retain at most seven days and include the volume
in encrypted off-device backups once that platform coverage is verified. Test
restoration and retain the independent withdrawal marker. Off-device coverage is
still unverified. Preserve spending state during archive recovery.

## Visual conversation context

The historical store also holds operator-captured native visual episodes. Each
episode anchors to a guild/channel/message reference and preserves nearby native
messages with stable author attribution and source timestamps. The importer
recomputes target flags from the pinned human ID and excludes bots/webhooks.
Original Discord PNG/JPEG/GIF/WebP attachment bytes are stored losslessly and
deduplicated by SHA-256, with episode-to-image links. The discovery pass limits
each file to 16 MiB and total unique image downloads to 64 MiB. Oversized or
unavailable images and external embedded images retain missing/reference-only
markers; external URLs are not fetched. Source captions and pixels remain private.

Study tools use `ArchiveStore.visual_context` and `read_asset` to inspect actual
pixels alongside conversation. The import itself performs no vision inference,
OCR or personality derivation. A legacy Slack text placeholder cannot recreate
a missing image. Native episodes are adjacent-message context, not a complete
reply/thread graph. Recheck source edits/deletions before future evidence use.

Repeated native episode imports update context for the same anchored source and
remove orphaned images. `remove-visual --digest <episode-key>` removes an episode,
its unreferenced images and historical backup copies, and blocks reimport. Global
withdrawal removes all raw images and visual episodes with the archive database.
The same archive backup/restore and off-device correction rules apply.

## Live response memory and images (2.5.0)

Responses use bounded lexical/topic retrieval from the existing private native and
Slack source stores. At most five distinct Andrew-authored passages are supplied,
with message references or export digest/line references. Slack adjacency is
explicitly context only, with ambiguity flags and unknown dates. There is no
separate generated fact database or unbounded transcript injection. Corrections,
source removal and withdrawal are checked again during materialization. Native
sources are fetched again before use, with a four-second timeout per source and six seconds total per reply;
failed fetches exclude the evidence. Membership verification and guild scope
remain required. Missing memory never disables an ordinary reply.

Current messages, explicit reply references in the same channel, and recent
history can supply live pixels. Focus/reference images have priority over history.
Each response shares two downloads/images, four MiB per download, twenty million
source pixels and six-second download timeouts. Only Discord CDN/proxy hosts are
fetched, without credentials or redirects. PNG/JPEG/WebP/GIF decode to bounded
1600-pixel JPEG inputs, with EXIF orientation applied. Animations use their first
frame with an explicit limitation. Missing or excess images are marked unavailable.
Live pixels remain in process memory and are not saved as learning evidence.

Responses sends structured image parts with high detail. Base64 payload size is
not counted as text tokens. Each image receives a deliberately loose 80,000-token
reservation plus the text bound through the same persistent usage ledger.
Authoritative usage is settled normally; any bound violation halts further calls.
The current official image guide omits a Luna-specific tokenizer row, so this
reservation exceeds the documented patch rejection ceiling times the highest
published multiplier. This is a conservative engineering bound, not a quoted
Luna token formula. The two-image limit also preserves the existing 200,000-token
pricing boundary. Text-heavy requests can still exceed that boundary and pause.


## Private evidence graph (2.6.0)

`memory-graph.sqlite3` is a separate schema-1 SQLite store on the existing volume,
owned by UID/GID 10001 with mode 0600. It stores typed nodes/edges, references and
fingerprints rather than copied raw text. Reviewed observations include qualified
summaries, source dates/unknown dates, confidence basis, extraction provenance,
status and expiry. Source stores remain authoritative. No new service is needed.

Only a trusted operator can initialize/populate/import the graph. Channel messages
cannot invoke these commands or authorize aliases, derivations or access:

```sh
ssh pi5 'docker exec wcb-bot trubot-graph init'
ssh pi5 'docker exec wcb-bot trubot-graph populate --limit 200'
ssh pi5 'docker exec wcb-bot trubot-graph import --manifest /var/lib/trubot/private-study/manifest.json'
ssh pi5 'docker exec wcb-bot trubot-graph status'
ssh pi5 'docker exec wcb-bot trubot-graph sweep'
ssh pi5 'docker exec wcb-bot trubot-graph remove --id <reviewed-observation-id>'
```

Initialization is exclusive and never happens at runtime. Repeat bounded
population batches until `remaining` is zero and visual processing is zero.
Each batch and checkpoint commits atomically; interruption/replay is safe.
Version 2.7.0 selects source references missing from the graph rather than
using the initial sorted cursor as a coverage boundary. Later native or Slack
sources are picked up in bounded batches by the existing learning cycle. Visual
population still uses its operator snapshot cursor and is not continuous coverage. Capacity is 30,000 nodes; lookup scans at most 1,000 entity/concept
nodes. Reviewed manifests are private, at most 128 KB and 100 observations.
Each observation has 1-3 distinct human supports, at most four entities/concepts,
a summary of at most 600 characters, review/provenance, confidence basis, status
and optional timezone-aware expiry. Duplicate source text is not corroboration.
Actual model-assisted studies use the existing maintenance ledger. Exact support
quote checks and a second contextual review reject unsupported interpretations;
agent review is not human review. Source text and model output remain untrusted.

Runtime follows matching entity/concept aliases through observations to source
support. A neighborhood must fit four observations and five sources as a whole;
both sides of a recorded contradiction are included or the neighborhood is
omitted. Native supports are refreshed through authenticated Discord reads before
derivations can be rendered. A failed refresh or changed fingerprint excludes the
derivation. Slack support preserves digest, block/line references and unknown dates.
Image nodes link captured hashes and native episodes but remain explicitly
unstudied and cannot support a personal belief. Live image inputs still use pixels.

Native observe/batch/edit/delete/prune and historical source removal sweep affected
graph state after committing the source update. Invalid or expired observations
and orphan concepts are erased; local graph backups are removed. Every read also
checks current source fingerprints, so interrupted cleanup or stale graph restore
cannot make a removed source valid. Missing/unwritable/corrupt graph state pauses
graph use; it is never recreated. Ordinary replies still work. Native intake may
report a graph cleanup failure after its source transaction has committed.

`trubot-learning forget` removes the graph database, SQLite sidecars and documented
`backups/memory-graph-*.sqlite3*` files. Loaded graph clients and stale restored
copies are blocked by the independent withdrawal marker. The usage ledger is
preserved. Private study staging, operator copies and off-device backups require
their owning cleanup process; remove temporary studies after verification.

Back up with SQLite's online backup API while holding the shared learning lock,
using a mode-0600 `backups/memory-graph-<UTC>.sqlite3`. Retain at most seven days.
Verify integrity, counts and disposable restore against authoritative sources.
Source corrections since a backup still win during lookup. Reapply operator
observation deletions after restoration; no external deletion registry exists.
Preserve the withdrawal marker independently. Do not replace usage state.
Image rollback retains graph bytes. Releases before 2.6.0 do not clean graph files
on withdrawal, so use a compatible operator tool or explicitly erase those private
files while preserving the marker. Off-device recovery/deletion remains unverified.


## Continuous text distillation (2.7.0)

No schema migration or added state file is required. Schema-1 graph checkpoints
hold a durable four-hour dispatch lease, per-anchor fingerprint/version/outcome,
source dependency references and retry time. Source stores remain authoritative.
A batch studies at most six related eligible human excerpts, capped at 1,200 UTF-8
bytes each, with at most two neighboring Slack context blocks of 250 bytes each.
Native sources stay within the configured intake intersection and are refetched
within the existing four-second-per-source/six-second-total budget. Every selected
source is rechecked before each paid request and under the final commit lock.

The extractor can propose at most one observation. 2-3 distinct exact target
quotes, including the new anchor, must pass local validation. Duplicate source
text, peer/bot claims and unviewed images cannot support it. A separate contextual
model pass checks literal meaning, uncertainty and relevant recorded disagreements.
Accepted summaries retain explicit conditions, tentative/contested status,
30-day expiry and automated review provenance. This is not human review or proof
of a permanent personal belief. Short/ambiguous anchors may produce no observation.

Both requests use the existing USD 2 maintenance allowance, not a fresh ledger.
The existing standard GPT-6 Luna prices were rechecked on 2026-10-08 against
[the official model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna).
Each request has a 16,000-byte framing/input/schema cap, a further 4,096-token
reservation margin and 1,024 output tokens. At two attempts every four hours,
the conservative maximum reservation envelope is USD 1.124928 for a 31-day month.
That leaves room for evaluations within the shared USD 2 limit; exhaustion or
unsupported pricing pauses studies before network I/O. Actual token usage is
settled normally. Missing usage, failures and cancellation retain reservations.
There is no added paid infrastructure, and pre-guard spending remains unknown.

The dispatch lease commits before requests, so restart, concurrent workers or
failures cannot cause a study storm. Valid rejections are checkpointed for 30 days;
insufficient support retries after one day. Transport/storage failures retain the
lease and retry after four hours without losing the anchor. Source corrections,
deletions or pruning erase affected derivations and all dependent study checkpoints,
allowing a bounded review of corrected evidence. Population no longer skips new
native references that sort before the old Slack cursor.

Removing an automated observation with `trubot-graph remove` also records
fingerprint vetoes for its supporting sources. The automatic learner cannot reuse
those unchanged sources as anchors or support, including a study already in flight.
An edit produces new evidence and clears the old veto through source invalidation.
Raw sources remain available to explicitly reviewed operator work and existing
source retrieval. For complete suppression, use the source-store deletion workflow.
Retirement is deliberately conservative about future automatic use of those sources.

Check `trubot-graph status` for aggregate accepted/rejected/insufficient study
checkpoints and veto counts. Withdrawal erases all graph checkpoints and vetoes
with the graph database and documented local backups. An independent withdrawal
marker still blocks loaded clients and restored copies. The spending ledger stays
intact. Online graph backups carry these checkpoints; restoring an older copy can
replay a study or lose a later operator veto, so reapply retirements after restore.
Current source fingerprints and the maintenance ledger remain authoritative.
Off-device recovery/deletion remains unverified. Data already sent in a provider
request cannot be recalled by a later withdrawal.

`python scripts/evaluate_distillation.py --live` runs five accounted provider calls
on disposable synthetic sources and captures every Discord send. Without `--live`,
it runs deterministic local study/reply stubs. It never changes real learning state
or creates a spending ledger. `evaluate_incremental_sources.py` makes one authorized
private study in a disposable graph clone, verifies pinned guild membership and
refreshes selected native sources through authenticated Discord reads. It reports
counts only and never sends a Discord message or copies/replaces usage state.
Synthetic concept-selected questions test the flow, not independent human fidelity.

## Development recall scope and year labels

Version 2.7.1 permits the authenticated owner of the configured development guild
to retrieve league memory from an existing allowed channel. The source guild,
pinned Andrew account and intake intersection remain authoritative. Other guilds,
non-owner requests, disabled scope and unlisted channels receive no cross-guild
memory. `TRUBOT_DEVELOPMENT_GUILD_ID=0` disables this access. Withdrawal continues
to block source transactions before any memory is rendered.

Historical year retrieval uses current archive origin period hints. These label
exports and never supply calendar dates for individual messages. Current origin
hints are checked again during rendering, and removed documents cannot supply
quotes. Native timestamps take priority for dated recall. Unknown-date graph
observations cannot bypass a requested year. This does not backfill old native
messages or interpret previously unstudied images.

Content-free operator smoke audits may retain private development question/answer
message IDs, anonymous case names, boolean checks and latency under
`/var/lib/trubot/smoke-tests`, directory mode 0700 and files 0600. They store no raw
source excerpts, source-account mapping, derived answer text or new beliefs, and
never enter retrieval. Keep seven days of operator evidence; remove older files
manually during the next smoke run, and remove this directory during operator
withdrawal cleanup. The usage ledger remains independent. A separate validation
client must use its own ephemeral readiness path before construction so closing
it cannot remove the running bot's heartbeat.


## Natural recall presentation, 2.7.2

Presentation is selected from the focused human request. It never changes private
source metadata, approved attribution, graph confidence, correction, withdrawal or
the usage ledger. Broad year questions can retrieve labeled exports without
asserting a calendar date or announcing the export label. Explicit timing/evidence
requests retain concise relevant qualifications; filenames are never dated proof.

Content-free character audits share the seven-day manual smoke-test retention and
withdrawal cleanup path above. Keep only source/message references, sample counts,
generic defect flags and timing. Do not retain raw conversations, private preference
values or generated answer text in these artifacts. Structural scans do not replace
contextual semantic review or establish personality traits.

Version 2.7.3 adds bounded recent quotation lookup for referential timing/evidence
questions. It searches current attributed source text and rechecks at render time.
There is no persisted bot-memory cache, new derived state or schema change.


## Context-aware study packets, 2.8.0

Schema-1 sources/graph and four-hour pacing are unchanged. Study version v2
reopens prior anchor eligibility at the next existing dispatch boundary, never
resets the lease or creates a ledger. At most six authored snippets now use
1,000 UTF-8 bytes each; at most two adjacent Slack blocks use 120 bytes each.
Anonymous document-scoped speaker keys, target/bot/context-only roles, position,
parser flags and truncation preserve interpretation limits without raw names.
Native packets explicitly identify absent peer setup. Context blocks cannot
become support quotes. No historical pixel interpretation is added.

Packet selection prefers related sources outside obvious shared contexts.
Humor/style support rejects native pairs less than six hours apart (including
channel changes) and same-export pairs within ten blocks. Separate corpora or
export windows are candidates for contextual review, never proven independent
episodes. Review must reject a pattern if setup cannot establish recurrence.
Tentative observations retain sampling uncertainty, source dates, expiry, exact
quotes and existing correction/withdrawal/veto checks. Existing qualified claims
are not retroactively changed; current production has no automated style/humor
observations to retire. The 16,000-byte request guard and maintenance cap remain
authoritative; oversized packets pause without a paid call.
