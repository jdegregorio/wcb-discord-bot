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


## Specific self-report support (2.9.0)

Graph schema remains 1. New automated observations carry `support_basis`, either
`corroborated` or `explicit_self_report`. The latter is restricted to one complete
12-300-character, untruncated first-person claim/preference in the anchor source.
A separate contextual review must confirm literal authorship and a summary limited
to that particular statement. It never establishes a recurring humor/style trait
or enduring/current preference. Both passes use the existing maintenance ledger;
four-hour production pacing, tentative status and 30-day expiry remain unchanged.

Trusted maintenance code can pass an exact eligible `anchor_ref` to
`GraphDistiller.cycle`. This does not expose a Discord command or bypass channel
scope, current source fingerprints, study cooldown, operator veto or withdrawal.
An unavailable, retired or already studied requested anchor does not fall through
to a different study. Never clear checkpoints or create a new production ledger
to force a study. Disposable evaluation clones may simulate the next due cycle;
record that simulation separately from actual production learning.

The support basis and source dates are internal grounding metadata, not mandatory
conversation disclaimers. Existing graph lookup and render revalidate every support.
Single-source observations share source correction, deletion, retirement and
withdrawal cleanup. Compatible image rollback leaves graph and usage state intact;
retire a bad observation separately through the existing graph operator command.
Private evaluation copies must be removed when their content-free evidence is saved.

## Content-free study diagnostics (2.9.1)

Study events report only fixed pipeline stage, cause/outcome, bounded source count,
study-adapter request count and monotonic elapsed milliseconds. Requests are calls
to the study adapter, not proof of provider network attempts or billed requests;
the usage ledger remains authoritative. No raw exception strings, classes, paths,
response bodies, message IDs, source hashes, quotes or generated answers are logged.
No new database, schema or retention boundary is introduced.

`Graph study paused` distinguishes evidence availability, budget exhaustion/state,
request context bound, malformed/incomplete result, provider connection/status/access,
Discord access/transport, timeout, storage and unexpected failures. The stage shows
whether the failure occurred during population, selection, source refresh/check,
extraction, prior-memory lookup, review or commit. A source check inside a provider
adapter retains the validation stage if it fails before the request. Categories
identify a class of failure, not a retrospective root cause. Evidence unavailable
may include withdrawal, changed support, permissions or unavailable private state;
inspect the existing private status and source rules without relaxing them.

Completed studies distinguish insufficient support, no proposal, invalid proposal,
invalid review, reviewer rejection and accepted observations. Normal unverified,
paced and no-candidate skips are DEBUG only, avoiding warning spam each poll.
Cancellation propagates and never claims failure or completion. Diagnosis does not
retry failed work or reset the four-hour lease, reservations, vetoes or source checks.

Use `scripts/evaluate_study_diagnostics.py --require-diagnostics` against an installed
wheel for synthetic fault isolation. It creates disposable synthetic learning/graph
stores and mocked transports, never constructs a Discord client or reads credentials,
never opens live learning/budget stores, and makes no provider or Discord call.
Its success proves classification and isolation, not improved human fidelity.
Actual owner-authored development Discord replies remain a separate release gate.


### Provider evidence contracts, 2.9.3

Extraction/review schemas are generated from the bounded current packet and prior
observation count. They enforce existing text/array bounds and supported indexes,
with a complete anchor quotation for eligible singleton self-reports. The same
local validator, review, fingerprint checks and final source-locked commit remain.
No graph migration, new file, retention change or source population is needed.
The study provenance/checkpoint version stays unchanged: existing outcomes and
four-hour pacing do not reset. Rollback to 2.9.2 remains data-compatible and
honors withdrawal. Schema bytes enter the existing maintenance reservation.


## Source-checked voice, 2.10.0

The legacy catalog contains lookup keys only. Each reply resolves eligible current
archive answer/setup pairs under existing source transactions and guild gates.
At most three separated pairs, 1,200 characters per block, are supplied with source
lines, exact alias attribution and unknown-date metadata. Requested years require
current matching export-period hints, never dated-message proof. Quotes, ambiguous
thread/link/media context and bot setup cannot establish a voice pair. There is
no persistent voice cache, new database, graph observation or backfill. Withdrawal
and removal therefore erase this route as well as normal recall. The usage ledger,
four-hour study pacing and existing storage/backup boundaries stay unchanged.
Older images retain unconditional catalog examples; rollback must not be used to
restore private-derived behavior after withdrawal. This release has no migration.


## Recent native conversation recall (2.11.0)

Recent-message questions use at most three verified native sources from the last
fourteen days, within the configured retention period. They select chronologically
for broad recall and retain topical filtering for specific questions. Undated
historical exports and voice examples cannot fill a recent-recall gap.

After mandatory source refresh, the remaining six-second budget can fetch at most
two same-channel human neighborhoods. Each carries up to five short context rows,
source dates and explicit reply links. Peers remain context; adjacency does not
prove a reply relationship. Bot/webhook, expired, future, cross-guild and denied
context is excluded. Source/media gaps stay explicit internally. Historical pixels
are not retrieved here. Context is ephemeral and never added to learning or the
memory graph. Source edits, deletion and withdrawal invalidate the recalled focus.
Full native history, durable peer/thread graph coverage and broader conceptual
recall remain future work. See the research/progress records for measured results.


## Rolling conversation recall (2.11.1)

Authored recall such as "quote something from the past week" or "what did you say
in the last 48 hours" uses verified native timestamps. Numeric and ordinary spelled
hours/days/weeks define rolling durations, intersected with current retention.
Selection and rendering both recheck the window; at most three native sources and
two human neighborhoods are supplied. Empty, zero or unknown quantities cannot
fall back to undated archives or voice examples. Named calendar months/days remain
outside this parser; explicit year recall keeps its existing provenance rules.
No new state, retention, provider call, model, participation or spending policy.


## Conditional episode abstractions (candidate 2.12.0)

Reviewed humor/style imports can optionally contain `abstraction`: bounded
`conditions` and `limitations` strings (1-240 characters each), and zero to two
`counterexamples` containing eligible attributed human source references. Require
2-3 distinct separated support sources. Sampling separation is only a mechanical
screen, not proof of independent episodes; private review and confidence basis
remain necessary. Bot/peer assertions and unavailable sources cannot support or
qualify a pattern. This milestone uses reviewed imports; the automatic extractor
continues its existing schema and four-hour pacing until a separate studied change.

Counterexamples become fingerprinted `counterexample-of` edges. Their edits,
deletions, archive suppression, expiry or failed native freshness invalidate the
whole observation just like changed support. A complete neighborhood, including
counterexamples, must fit the existing five-source bound. Retrieval refreshes
native support and contrary sources before optional neighborhood reads. All
fields remain under source withdrawal and graph backup cleanup. No schema
migration, hosted service, extra provider call or participation expansion.

Ordinary relevant replies receive the conditional summary and limits instead of
pattern-only support quotations. Shared factual support remains available.
Explicit quote/evidence/time requests retain current source passages, with
counterexamples labeled separately. Date/confidence/expiry remain internal.
An abstraction is an interpretation, not an authentic quotation, command or
permanent preference. Keep private derived observations and manifests off Git.

Production has no newly imported abstraction while the run's specific OpenAI
payload approval is pending. The offline graph copy lives only under the private
app-volume smoke-test directory, mode 0700 with files 0600, seven-day manual
retention and withdrawal cleanup. Do not import it automatically on deployment.

Rollback to images predating this support requires retiring new abstraction
nodes using `trubot-graph remove --id <private-observation-id>` BEFORE the older
image resumes replies. Older readers do not validate contrary-source fields.
Preserve source and spending stores; never replace them with the study copy.
Record and verify observation removal and readiness through the locked pi-app
rollback transaction. Current production graph is unchanged, so this run has no
new live graph state to retire yet.
# Conditional automatic patterns, 2.13.0

Automatic humor/style proposals now require conditions and limitations, with 0-2
exact attributed contrary excerpts. The writer stores their current source refs
in the existing abstraction contract, never as an extra factual belief. Support
must still be 2-3 separated sources, with tentative status and 30-day expiry.
All support and contrary-source edits, deletions, retirement and withdrawal remain
authoritative. Checkpoint cohort and four-hour lease/retry pacing are unchanged;
new extraction provenance does not force a historical replay. No schema migration,
new corpus intake, volume or ledger is introduced.

Rollback to the recorded previous 2.12.1 is compatible with conditional records:
it includes the H21a reader, counterexample validation and withdrawal lifecycle.
Older readers without that contract are not safe for newly populated patterns.
The selected prior private pattern remains separate from this synthetic-only
conformance work and requires its recorded validation prerequisite.

### 2.14.0 behavioral observation compatibility

The existing schema-1 graph accepts `value`, `emotion` and `relationship` nodes
only with qualified abstractions. The shared observation domain registry governs
write, sweep and retirement. New records retain domain metadata; old records lacking
that metadata remain readable. No source migration or private human population is
performed by the release. Older images cannot correctly sweep or retire these new
kinds. Before rollback after actual population, preserve a private graph backup and
retire/suppress new-domain observations using the current version; never restore
withdrawn sources or reset spending state. The release validation populates only
isolated invented stores, so current production rollback has no new-kind data risk.


## Bounded historical episode study context, 2.15.0

Historical study packets may include up to three adjacent blocks before and after
an attributed source. Admitted rows contain complete text, anonymous speaker keys,
roles, offsets and parser flags. Rows above 600 UTF-8 bytes or outside the request
allowance are counted as omitted context, not clipped into misleading fragments.
The complete extraction envelope is at most 14,000 bytes, leaving normal review
headroom within the unchanged 16,000-byte provider ceiling. Lowest-ranked related
sources may be excluded before extraction; the anchor and surviving indexes stay
aligned. Once extraction begins, both passes retain identical source/context rows.
Large priors still fail closed at the adapter rather than dropping contradictions.

No new graph schema, categories, private corpus, retention policy or persistent
context copy. The immutable export digest supplies context provenance; document
suppression/removal invalidates target support and derived observations. Native
sources retain their target-only scope, freshness and missing-peer labels. The
checkpoint cohort and four-hour pacing remain unchanged; new extraction provenance
does not replay old sources. Existing withdrawal, correction, backups and spending
apply. Rollback to 2.14.0 is data-compatible; this release populates no human trait.


## Complete reviewed episode studies, version 2.16.1

`trubot-study --episodes /var/lib/trubot/private-study/episodes.json` is an operator
maintenance command. Its JSON file must have a private owner and directory, be at
most 4,096 bytes, and contain only `schema: 1` and `episode_refs`, an ordered array
of one to six distinct references. The first is the anchor. Discord references
use `kind: discord`, integer `message_id`, and optional integer `channel_id`;
Slack references use `kind: slack`, exact SHA-256 `document`, and integer `ordinal`.
Use reviewed source references, not copied text, guessed aliases or file-date hints.
The command accepts no instructions, summaries, access grants or new evidence.

The source member is authenticated again with a plain bot HTTP client. Native
channels retain the runtime intake intersection. No gateway or Discord send is
started, and the command owns no application readiness file. Extraction/review use
current source text and the existing maintenance ledger. The complete requested
set must be available, unretired, untruncated and fit the existing request bound;
otherwise no selection lease or paid extraction is acquired. Four-hour pacing and
anchor retry remain shared with the running learner. All requested source indexes
remain ordered in both passes. Context rows can still have explicit size gaps.

Output is content-free completion/outcome metadata. Exit 2 means not completed or
unavailable, including pacing; `completed` does not mean accepted, and accepted is
still tentative two-pass model review, not human validation. Native source refresh,
exact quotation, independent pattern support, contrary-source links, atomic commit,
correction, retirement and withdrawal remain mandatory. This path does not change
automatic lexical sampling or populate a trait merely because refs were selected.
It provides a usable maintenance path for cross-topic episode/counterexample study.
Private manifests share the source owner's retention/deletion responsibilities;
do not publish them or retain raw/derived human data in test artifacts.

The installed command caches only text/thread channels accepted by the pinned source
guild and configured intake intersection. Reply-only development channels are skipped
without becoming learning evidence. A denied HTTP read stops the command. Version
2.16.0 failed this mixed-allowlist acceptance and was rolled back; its prerelease
status excludes it from stable discovery. Version 2.16.1 passed authenticated
installed-command completion with disposable invented evidence and preserved the
production heartbeat. Rejection receipts do not establish human extraction quality.


## 2.17.2 optional recovery

Private source packets are revalidated through the production handler before an
optional exact-repeat recovery. Changed, deleted, withdrawn, denied or unchecked
packets receive no extra reservation/provider request. The already generated draft
is retained; this does not retract a first request already in flight. No schema or
state migration. Existing withdrawal marker, correction/expiry and spending state
remain authoritative. 2.17.0 and undeployed2.17.1 are prereleases; healthy2.16.1
is the compatible recorded rollback.


## Atomic reviewed imports, 2.18.0

### Preview a reviewed rollout, 2.25.0

Run `trubot-graph import --manifest <private-manifest> --dry-run` before a curated
rollout. The same complete-batch validation exercises prospective replacements,
contradictions and source provenance under the learning lock, then rolls back every
graph write. Existing beliefs, edges, checkpoints and graph backups remain intact.
The content-free result reports validated and committed counts; committed is zero.
The flag is rejected on other commands.

A successful preview is a check at that moment, not a saved approval. Import without
the flag revalidates current evidence, expiry and withdrawal before committing.
Keep manifests private and ephemeral. Population requires contextual human evidence,
contrary cases and actual reply validation in addition to a successful preview.
On failed behavioral acceptance, retire only the new observation with the existing
remove command; do not restore sources or the spending ledger.

The private `trubot-graph import --manifest` format stays schema 1. Its complete
one-to-100 observation batch now shares a source/withdrawal lock and graph transaction.
Distinct nonempty string IDs are required; an invalid later item rolls back additions,
replacements and contradiction status changes. Validation rejection preserves prior
graph backups. Successful import retains existing backup cleanup; a subsequent file
cleanup failure can still require operator recovery after the database commit.
No cross-filesystem atomicity is claimed. Raw and derived manifest contents are never
logged. Remove ephemeral reviewed manifests after import; production graph state is
the retained derivation and follows source correction/deletion, expiry and withdrawal.

This rollout may retain a small locally reviewed tentative abstraction with explicit
non-human extraction provenance, source links, conditions, applicability controls and
30-day expiry. Local Codex review is not independent human validation. Do not restore
retired or corrected observations from a stale manifest or remove the withdrawal marker.
Rollback the memory by retiring its recorded observation ID, not restoring a learning
or spending database. No source schema, study pacing or allowance changes.

## 2026-10-12 05:00 selective voice release

2.18.1 makes no storage/schema/intake change. Real learning and graph counts remain
unchanged with zero active human abstractions. Two actual installed-handler fixtures
use disposable invented stores and distinct readiness before construction; source
removal/withdrawal and production heartbeat pass. Private refs, counts and public
helpers live under the app volume smoke-tests/2026-10-12-0500 directory, 0700/0600,
existing manual seven-day retention and withdrawal cleanup. Raw contextual/rendered
answers are erased. Existing billing/backup coverage limitations remain unchanged.

## Abstract memory projection, 2.19.0

No schema or storage migration. Ordinary guidance omits audit prose/counts from
provider context and suppresses competing raw voice examples. The graph retains
confidence basis, support/counterevidence and extraction provenance for correction
and explicit evidence. Dates, expiry, status, conditions and limitations still
reach the reader; source freshness, invalidation, retirement and withdrawal stay
authoritative. This does not populate a new human abstraction. Run evidence keeps
content-free private refs/counts, synthetic fixtures and public helpers on the
existing app volume under 0700/0600 with the existing manual seven-day/withdrawal
cleanup. Human/reply renderings and candidate overrides are erased.

2.19.1 completes ordinary would/could/should/current-response wording without a
storage migration. Explicit quote/evidence/past-word support stays available. The
same marker, invalidation, backup, expiry and private evidence retention apply.
No new human abstraction is populated.

For development evidence transfers, create the local staging directory with mode
0700 and transfer files with mode 0600 before collecting human material. Do not
inherit the workstation's default umask. Verify these modes before rendering or
transport, then erase temporary raw images/archives after review.


## Authenticated memory author scope (2.19.2)

This scope is ephemeral typed metadata on an app-created memory message. It contains
only source/other/unknown author categories, not names, account IDs or new personal
observations. Identity comparison uses the existing pinned private store and focused
message author, not the requesting reactor. No schema, retention, source intake,
backup, study pacing or ledger changes. Current identity and withdrawal are rechecked
before packet admission and optional repeated-reply recovery. Image pixels remain
attached to their focused human message. Compatible rollback preserves graph, sources,
withdrawal and spending state, but restores the earlier attribution defect.


## Complete live conversational setup, 2.19.3

Native human neighbors and same-channel parents, plus historical adjacent blocks,
are supplied as complete text up to 600 UTF-8 bytes per message. Oversized context
is omitted with an explicit gap rather than silently clipped. Native source/media
gaps, speaker roles, reply links, same-channel scope, bounded reads and mandatory
source freshness remain authoritative. Historical bot context is labeled separately
from peers. Authored-source text ceilings remain unchanged. This does not broaden
intake, persist peers, populate a human trait or add provider/HTTP requests. Existing
withdrawal, spending, privacy and compatible rollback remain unchanged.


## Stale passage recovery, 2.20.0

The existing optional refresh can recognize exact12-word normalized old bot spans
inside a changed answer. Same authoritative source revalidation/ledger and at most
one extra generation; no new persistent state, schema, intake, privacy or recovery
boundary. Immediate continuity, short wording and intentional quotes/references stay
eligible for reuse. Rollback2.19.3 is data-compatible. This run's private content-free
refs/counts/metrics, public helpers and invented fixtures use the app-volume
smoke-tests/2026-10-13-0100 directory,0700/0600, seven-day manual retention/withdrawal
cleanup. Candidate package override is temporary and removed after installed checks.
Raw human/answer text is not retained in actual smoke records.


## Native automatic pattern context gate, 2.20.1

Native automated study packets still contain target-only text, lacking durable peer
setup, linked replies and context-source invalidation. All automatic pattern domains
(humor/style/value/emotion/relationship) now reject native support or counterevidence.
Source kinds come from authenticated snapshots. Model-supplied context labels cannot
open this gate. Contextual archive pattern studies and explicit operator-reviewed
native observations remain eligible under their existing validation contracts.

A restored older automatic native pattern is blocked by lookup/describe before
sweeping. The normal source sweep erases such nodes and removes graph backups through
the existing invalidation path. No database migration, checkpoint-version change,
new corpus, new provider payload, automatic history replay, allowance change or new
service. Production has zero active patterns at rollout, so no observed populated
human pattern is erased. Preserve source correction/deletion/withdrawal and expiry.
Rollback2.20.0 is data-compatible but restores the permissive learning boundary;
keep native automatic population paused until H54b durable context provenance and
invalidation are implemented and evaluated. Synthetic acceptance artifacts retain
only content-free private message references/flags and public helper code in
smoke-tests/2026-10-13-0500,0700/0600, under the existing seven-day manual retention
and withdrawal process. Disposable synthetic databases are removed after each test.


## Native dependency metadata, 2.21.0

Existing native reply retrieval now records content-free source-to-context links in
memory-graph.sqlite3. At most100 captures/up to five human dependencies each/30-day
capture lifetime, plus the native source retention floor. Speaker/channel/message
IDs, source/capture timestamps, reply relations, full text hashes, media-presence
markers and coverage gaps remain private. Original pixels are not represented by
these hashes, and no peer text or derived human interpretation is persisted.

Shared learning-lock checks reject raced captures. Known peer edits/deletes and
source changes erase links and graph backups; current target-neighbor rows also
block stale restored metadata after correction. Missing graph/denied setup reads
leave ordinary replies available. Withdrawal erases this graph state and preserves
the spending ledger. No schema migration, source replay or new provider/Discord
request. Optional metadata comes from the existing live collector, not a new intake.

A capture records observed bounded setup, not current visibility or complete context.
The automatic native pattern gate remains closed. H55b must add fresh per-dependency
reads before studies/both provider passes/commit, full contextual packets and held-out
validation before opening it. No new abstraction or measured reply-quality gain.
Rollback2.20.1 is schema-compatible and retains the pattern gate, but stops the new
capture lifecycle; sweep/remove native_context and orphan native_context_dependency
nodes with2.21.0 before a deliberate downgrade after capture. Do not restore source
or spending databases to roll back code. Synthetic smoke artifacts keep only
content-free refs/flags/public code under private app-volume0700/0600 and existing
seven-day manual retention/withdrawal cleanup; disposable databases are erased.

## Native dependency reconciliation, 2.22.1

Existing schema1 captures remain content-free and retain their original30-day lifetime.
A round-robin checkpoint in the existing graph rotates up to two eligible captures per
learning cycle. Source and retained dependency messages are read within the existing
allowlist/pinned guild; peer text is ephemeral and never added to source storage.
Fingerprint/reply/media-presence/time/author changes and403/404 remove the matching old
capture, orphan dependencies and graph backups. An old verifier cannot delete a newer
capture. Transient transport errors/timeouts preserve observed metadata and establish
no fresh visibility. Unknown original pixels and uncaptured messages remain gaps.
Withdrawal/identity/scope are checked before each network stage; source events and the
final shared-lock check remain authoritative. No new schema, source replay, provider
request, ledger or service. No automatic native pattern eligibility.
Rollback2.21.0 is data-compatible and ignores the new content-free rotation checkpoint,
but stops offline dependency repair. Do not restore source/spending databases. Temporary
invented stores/candidate overrides are removed; content-free private smoke refs follow
existing0700/0600, seven-day manual retention and withdrawal cleanup.

The2.22.1 correction uses one current bounded history page for retained dependency
IDs, plus an exact same-channel parent read if needed. Freshness/attribution checks
still apply to every dependency. No new neighbors enter learning/context; missing
nonparents erase obsolete captures without guessing message deletion. No preserved
freshness certificate or automatic native pattern permission. [Transport study](evaluations/2026-10-13-native-freshness-study.md).

Final2.22.1 matches every retained dependency using current bounded around-page reads;
one exact current same-channel source parent may be fetched separately. Maximumtwo
captures/sixHTTPreads/sixseconds; no copied new neighbors, fresh certificate or native
pattern permission. Compatible rollback2.22.0 preserves data/gate but restores the
individual-read partial-result limitation. Original2.21.0 is also schema-compatible
but stops background repair. Do not restore source or spending stores. All prototype
package overrides, synthetic fixture stores and captured-cohort copies are removed
before completion. Only content-free refs/counts/flags/public helpers and source hashes
remain under existing0700/0600, seven-day manual retention/withdrawal cleanup.


## Native study boundary freshness, 2.22.2

The existing study lease/cohort now receives current native HTTP reads before each
of two maintenance provider attempts and before the reviewed-observation commit.
Initial preflight still fails before a provider reservation. Source changes or denied/
transient reads stop the study; transient failure does not imply deletion. Existing
source locks, fingerprints, correction/withdrawal and conservative uncertain spending
reservations remain authoritative. Four read stages, at most six sources/24 HTTP reads
per study, six seconds per stage/four per read. No maintenance retries, new ledger,
schema, checkpoint cohort, peer intake or native automatic pattern eligibility.
Rollback2.22.1 is data-compatible but restores the stale study boundary. Preserve
source/spending stores. Content-free private refs/counts and public helper code use
the existing app-volume smoke-tests/2026-10-13-1700 directory under0700/0600 and the
existing seven-day manual retention/withdrawal cleanup. Invented fixture stores and
package overrides are erased after validation; no source excerpts or replies retained.

## Native study setup dependencies,2.23.0

Studies bind existing private content-free captures, freshly rechecking source and
retained dependencies before both provider attempts and commit. Study payloads stay
target-only. Linked observations store bounded capture metadata and interpreted-with
edges; no peer text copied. Shared-lock checks reject changed captures. Recall validates
current semantic fingerprints; identical recaptures preserve observations/edges.
Changed/erased/evicted/expired captures retire linked observations and source-cohort
study checkpoints; corrections and graph backups follow existing source lifecycle.
No schema migration, checkpoint version/replay, model, extra provider attempt or service.
Maximum6sources/5dependencies,3HTTPreads per captured source/18per boundary/72per study;
each boundary still6seconds. Transients preserve old capture without certifying freshness.
New local context metadata is stripped before reply rendering. Native automatic patterns
remain closed. Human context interpretation/held-out quality are separate prerequisites.

Before downgrade to2.22.2 or earlier, erase only context-dependent observations and
linked study checkpoints and graph backups using the current private graph transaction;
older readers ignore their new invalidation metadata. Preserve source/capture/spending
stores. No data restore for code rollback. Content-free refs/flags/public helper code
in smoke-tests/2026-10-13-2100 use existing0700/0600,seven-day manual retention and
withdrawal cleanup. Disposable invented stores/process overrides removed after validation.


### H68 reply rendering,2.26.1

No storage migration or source mutation. Complete stored authored text is eligible
up to6,000UTF-8bytes; above that limit the reply packet contains provenance and an
internal gap, never an incomplete prefix or adjacent peer substitute. All-omitted
packets disable optional voice examples. Existing identity, correction, deletion,
withdrawal, graph and backup rules remain authoritative. Native intake's separate
character limit is unchanged. Rollback2.26.0 requires no database restoration.


## Final reply publication check (2.26.6)

Generated drafts containing retrieved private memory recheck the same source packet
and authenticated author scope immediately before Discord send. A changed/removed/
withdrawn/unavailable packet discards the draft; no automatic regeneration, source
restore, ledger reset or disclosure of draft text occurs. Existing bounded native
refresh reads apply again. Replies without retrieved private memory and recipient
abstentions need no final memory read. This adds no store/schema/retention exception.
The external send is not atomic with the source check; corrections after the check
still require the normal operator/source lifecycle. Avoid restoring data to roll back
this runtime-only release. Private test clients keep distinct heartbeat paths.


## Pattern qualification, 2.26.7

All newly imported pattern domains, including humor/style, require a conditional
abstraction,2-3separated distinct supporting sources and bounded conditions/limits.
Preview rejects an unqualified batch atomically. Lookup/describe/sweep check stored
node kinds even when old data.kind metadata is absent; malformed, unqualified or
single/shared/duplicate support patterns cannot supply guidance. Qualified legacy
conditional patterns and literal claims/preferences remain supported. Sweeps erase
invalid derivations and existing graph backups through the normal lifecycle.

No migration, source mutation, intake, paid pass or infrastructure is added. Review
and explicitly reimport a corrected observation when appropriate; never manufacture
missing conditions automatically. A normal sweep may permanently erase ineligible
old observations. Rolling back code does not restore erased data; avoid source or
usage-ledger restoration. Earlier images can re-admit unqualified restored patterns,
so use the current qualification tool to inspect/retire them before deliberate
downgrade. No new private human observation is populated in this run.


## Evidence-owned concept aliases, 2.26.8

New about/exemplifies edge evidence includes its reviewed aliases. Lookup keeps
shared concept traversal while requiring a current alias-owning observation; it
uses the same64-observation freshness cache, four results and five unique sources.
Node aliases remain unchanged as fallback for legacy edges, preserving readable
state without migration or a new provider call. Per-observation replacement,
remove, source correction/deletion and expiry stop retired routes from activating
valid neighbors. Duplicate entity/concept relationships in one import are rejected
atomically. Unknown dates, attribution, counterevidence and withdrawal remain.
Already lost legacy aliases require contextual review and reimport, not guessing.

No schema migration, new paid service or runtime spending change. Previous code
can read this schema but ignores new edge aliases, so rollback may narrow lookup
coverage for newly imported relationships. Authoritative human sources remain
unchanged. This run imports no new production human observations. Research
candidate manifest and temporary graph are erased after rejection. Content-free
receipts retain existing0700/0600,seven-day manual retention/withdrawal cleanup.


## Explicit human reply subject,2.27.6

Existing same-channel reply-reference fetch retains the human author's authenticated
ID ephemerally. Complete bounded referenced text may supply a generic memory query;
it is neither persisted as a source nor attributed to Andrew. Bot/unknown/denied/
cross-channel/incomplete/oversized/image-dependent references cannot supply a topic.
No schema, source mutation, new read/provider pass or storage/retention expansion.
Existing source correction/deletion/withdrawal/expiry, author ownership and final
source packet checks remain. Code rollback needs no data or spending restoration.
Private content-free refs/counts/grades use the app volume smoke-tests/2026-10-16-2100
under0700/0600 with existing seven-day manual retention and withdrawal cleanup.
Disposable candidate package and validation helpers are erased after installed checks.


## Fresh native study setup, 2.28.0

The existing retained native dependencies are freshly read at the initial boundary,
projected once as source-local anonymous speaker/position/reply rows, then frozen
identically for extraction and independent review. Every existing pre-attempt and
pre-commit source check remains. Original selected cohort and local fingerprints
stay authoritative. Peer setup is context only, never authored support. Absent
captures keep the explicit target-only gap; empty captures/media/oversized omissions
remain honest gaps. Complete rows at most 600 UTF-8 bytes enter the existing measured
14,000-byte extraction envelope; the adapter retains its 16,000-byte final bound.
Raw peer text never enters graph/checkpoint/log payloads. Discord IDs are removed
from provider setup rows; existing private dependency IDs stay local. Source-local
anonymous links can point outside supplied context and do not prove complete coverage.

No new Discord/provider request, study cadence, cohort version, source discovery,
intake, schema, model or budget. Joe's explicit source-study authorization covers
existing readable peer context through the current app-scoped provider. The automatic
native pattern gate remains CLOSED even when fresh context is supplied. Contextual
semantic qualification and independent held-out usefulness are separate next work;
this does not populate a human abstraction or establish reply-quality improvement.
Existing correction/delete/access/expiry/withdrawal and interpreted-with invalidation
continue to govern memories and backups. Rollback is schema-compatible; do not restore
source or spending state. Already accepted observations retain their dependency
lifecycle, but older code resumes target-only future studies. Private validation
receipts use existing app-volume smoke-tests, 0700/0600, seven-day manual retention
and withdrawal cleanup; content-free references/results only.


## Fresh source media continuity,2.28.1

All already verified native reply sources supply ephemeral source-media presence
before optional neighborhood reads. These source-only fallbacks have no captured
source/dependency metadata and never call record_native_context. Successful full
captures retain existing graph recording, source binding and lifecycle. Empty
media-only setup is rendered with conservative missing-setup uncertainty plus its
exact source warning. Unknown media remains unknown; additions/removals or unknown
transitions stop final publication even when setup reads time out. Presence does
not inspect pixels or fingerprint a replacement attachment or preview.

No new persistent source/peer data, schema, migration, paid pass or Discord read.
Existing app volume/read-only container/tmp boundaries remain. Downgrade is schema
compatible; do not restore source or spending stores. H85 and automatic native
pattern gate are unchanged. Private content-free refs/hashes/counts/rubric booleans
use app smoke-tests/2026-10-17-0500,0700/0600 and existing seven-day manual retention
and withdrawal cleanup. Raw excerpts, generated answers and personal derivations
must not be retained in smoke receipts or public notes.


## Aurora public-evidence state and operations, 2.29.0

Before enabling, run `docker exec wcb-bot trubot-aurora init` once on pi5. This creates
only `/var/lib/trubot/aurora.sqlite3`, private0700parent/0600file, on the existing
persistent volume. Never reinitialize an existing store. Inspect with
`docker exec wcb-bot trubot-aurora status`. Set the non-secret
`TRUBOT_AURORA_CHANNEL_ID` in app deployment configuration to an existing allowed
source-guild text channel; default0is off. Optional `TRUBOT_AURORA_STORE_PATH`
selects an already initialized private app-volume path. It is not created at runtime.

Rows contain local morning date, station/region, public Kp and qualifying observation
timestamps, outcome and bot message reference. They contain no human text, preference,
private source, image bytes or generated caption. Claims commit before any timing or
image call; attempting/failed/deferred/send_uncertain rows all suppress replay that
night. A post can be lost after an ambiguous send, but is never automatically doubled.
Rows older than35days are removed on the next successful new-night claim. No generic
source/ledger restore is part of rollback. Older images ignore this additive store.

The worker shares existing daily caps/cooldowns and quiet time, but explicitly
requested morning posts do not need recent group activity. It checks current pinned
source identity/withdrawal before preparing and sending, so withdrawal pauses it.
Aurora state is public-weather/bot-delivery metadata, not Andrew-derived learning.
Operator deletion is safe only with the feature disabled and a preserved duplicate
prevention decision. Keep state in normal app-volume backups; retain the spending
ledger independently through every image or code rollback.

Images API modelGPT Image2, qualitymedium, size1536x1024, n1, opaquePNG, text-only
prompt at most2000bytes. Text inputUSD5/M, image outputUSD30/M, primary pricing checked
2026-10-17. Reserve prompt bytes plus1024 and16384output tokens before network I/O;
settle actual provider usage without cached discounts. Missing/unsupported usage or
ambiguous provider failure retains the full reservation. Over-bound usage halts the
same ledger. The fixed request's documented output estimate is aboutUSD0.041 plus
prompt; first live previewUSD0.04172. One typical image every day would be roughly
USD1.30/month plus timing checks, within the existing18runtime/2maintenance/20total
cap. This is an estimate, not provider billing. No request retries or paid data service.
Generated files stay in memory for normal publication; no new raw-media retention.


Enabled2.29.1on2026-10-17: public aurora state explicitly initialized on the existing
volume; platform PR9 adds only the non-secret existing destination. Intermediate
2.29.0remained off while incomplete response reads were corrected. The bounded reader
now consumes chunks through EOF. Actual collector coverage and private synthetic
image/duplicate/gateway evidence are in the current study. No real qualifying night
has been observed. The default local configuration remains opt-in/off. Production
stores no test claims; HTTP-only smoke claims are disposable and readiness-isolated.


## Selective public context,2.30.0

No storage migration or new database. Public observation payloads and function-call
items are ephemeral,store=False,and never imported as human evidence. No private
conversation enters public HTTP. Same usage.sqlite3 runtime/maintenance pools;
each of at most two selected-skill model requests reserves independently. No image
call or added paid service. Only content-free skill names enter application logs.
The current run's private receipts use smoke-tests/2026-10-17-1300,0700/0600,
existing manual seven-day retention/withdrawal cleanup,no raw source or answer text.
Rollback2.29.1is schema-compatible;preserve source/spending state and existing aurora
claims. Do not restore those databases to roll back this code-only capability.


## Requested-scene operational claims, 2.31.0

Explicitly initialize `requested-scenes.sqlite3` beside the configured learning file
in the existing0700app volume with `trubot-scenes init --path <absolute-private-path>`.
Default CLI path is `/var/lib/trubot/requested-scenes.sqlite3`; a custom learning path
uses that file's directory in app composition. `trubot-scenes status --path ...`
reports only outcome counts. Runtime opens existing private0600state with mode=rw;
missing state/schema/ownership failures stop paid image attempts and do not initialize
or reset any allowance. Initialization refuses existing files and symlink directories.

Schema1 stores request/channel SHA256operation keys, claim timestamps and terminal
outcomes. No raw account/message IDs, source text, request text, human abstractions,
image prompts or generated image bytes are stored. Images are ephemeral until normal
Discord publication. Global ten-minute cooldown and three requested attempts per UTC
day count failed/blocked/uncertain attempts conservatively, across channels/processes.
Claims older than35days are pruned on a new request; original requests older than five
minutes cannot enter, including after restart. A limited request is also deduplicated.
Scheduled morning timing/claims remain separate; both share the same USD18/2/20ledger.

Withdrawal/current identity checks stop generation and publication. Operational hashes
remain as duplicate-spend prevention, like the spending ledger; they contain no source
corpus. Never reset/restore spending or operational claims on code rollback. This new
file is not evidence/graph state and creates no personal-data backup. If it is missing,
inspect why and explicitly initialize only a new deployment; uncertain claims stay
closed. Normal corrections/deletion/access checks invalidate a pending source request.
A send and final check cannot be atomic across Discord; nonce enforcement/durable
claims prevent automatic repeats, not a false promise of exactly-once delivery.
Rollback to2.30.0 ignores the new file and preserves both spending and source state.
Private validation receipts remain content-free0700/0600with existing seven-day manual
retention and withdrawal cleanup; preserve only references/pass/fail, not answer text.
