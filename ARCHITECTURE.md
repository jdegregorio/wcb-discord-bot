# Architecture

Trubot is intentionally a small service. The design separates policy from I/O
so Discord events, OpenAI requests, timing rules, and the personality can change
independently without hiding behavior behind a framework.

## Runtime flow

```text
Discord event
    │
    ▼
TruBotClient ── validates channel + trigger ──┐
    │                                         │
    │                                  ParticipationTracker
    │                                  + AttentionTracker
    │                                  (pure per-channel policy)
    ▼                                         │
recent Discord history + verified source/graph memory ◄──────────────────────┘
    │
    ▼
OpenAITruaxResponder
    ├── personality + mode contract
    ├── atomic persistent usage reservation per attempt
    ├── Responses API / gpt-6-luna
    ├── service_tier = default (standard)
    ├── reasoning.effort = low for inferred follow-ups, none otherwise
    └── store = false
    │
    ▼
bounded Discord reply
```

## Boundaries

- `config.py` parses and validates the entire environment at startup. Secrets
  cannot appear in the settings representation.
- `personality.py` owns character instructions and legacy lookup keys.
  The stable fictional voice and Thomas Jones devotion are product behavior,
  available without retrieval. Real biographical and historical claims require
  attributed evidence; new banter is never evidence of Andrew's actual words.
  `voice_memory.py` resolves at most three current attributed answer/setup pairs
  through the existing private memory scope, with correction, year and withdrawal
  gates. Only distinctive literal terms shared with the preceding setup admit a
  voice pair; broad topic expansion, answer-only matches and filler do not. Examples
  describe a context, not a biography or habitual trait. Synthetic
  judgment illustrations remain separate and never supply personal evidence.
- `memory_author.py` carries typed application-owned source-author scope from the
  pinned human identity and the focused message author. Raw display names, channel
  content, peer claims and old bot replies cannot provide this binding. The adapter
  applies it in instructions and beside the focus, including visual focus. Conflicting
  or missing authenticated focus scope is conservative; withdrawal or identity change
  removes stale memory before dispatch. A repeat attempt revalidates the same scope.
- `openai_responder.py` is the only OpenAI dependency. It produces a plain
  string through the Responses API and normalizes accidental speaker prefixes.
- `participation.py` is a synchronous state machine. Given channel activity and
  time, it decides whether an ambient reply may be scheduled. It performs no
  sleeping, network access, or Discord calls.
- `attention.py` retains a short-lived per-channel window after an explicit
  summon. While active, the model can answer a clear follow-up or abstain without
  posting.
- `history.py` retrieves the newest messages inside both a count cap and an age
  window, restores chronological order, converts Discord objects into
  provider-neutral conversation messages, ignores other bots, and bounds
  untrusted content.
- `discord_client.py` is the orchestration shell. It owns pending tasks,
  per-channel response locks, reactions, replies, and graceful shutdown.
- `health.py` ties container readiness to the live Discord session rather than
  merely proving that a Python process exists.
- `budget.py` owns the private SQLite ledger. Transactions serialize reservations
  across channels and processes. Integer nanodollars avoid rounding drift. Runtime
  opening uses SQLite `mode=rw` so lost storage cannot reset the allowance.
- `learning.py` owns the separate private evidence store, verified identity,
  provenance, atomic scan checkpoints, edit invalidations, deletion markers,
  retention and content-free operator status. It never calls a model.
- `ingestion.py` revalidates the pinned member and coordinates bounded history
  catch-up plus rotating source reconciliation. Live captures never advance
  scan checkpoints. The worker runs beside response generation, with lifecycle
  tied to Discord readiness, resume, disconnect and shutdown.
- `memory.py` combines bounded lexical source recall with reviewed graph traversal.
  A typed RenderedMemory packet carries the voice-example admission policy.
  Ordinary abstract guidance omits review prose/counts and suppresses raw voice
  examples; literal evidence keeps its source text. Dates, status and scope persist.
  It materializes current raw evidence and qualified observations only after native
  source verification, preserving attribution and unknown dates.
- `graph.py` owns private typed nodes/edges, incremental population and study checkpoints.
  Sources, captured image hashes, episodes, the verified person and qualified
  concepts/observations are connected on the existing volume. Runtime compares
  evidence fingerprints; source mutations erase invalid derived state and backups.
  Historical visual interpretation remains future work.
- `distillation.py` runs bounded two-pass text studies beside replies. Durable pacing,
  exact quote validation, native refresh and atomic source fingerprint checks gate
  tentative observations. Source invalidation reopens affected studies, and operator
  retirement blocks automatic reuse of unchanged supporting evidence.
- `study.py` exposes the trusted complete-episode maintenance command. A plain
  HTTP client reauthenticates the pinned member and source channels. Exact source
  selectors keep cross-topic support and contrary examples in both study passes,
  retaining pacing, provenance, withdrawal and the existing maintenance ledger.
  It owns no application heartbeat and starts no gateway or Discord send.
- `app.py` is the composition root. Importing any module is side-effect free.

Operator withdrawal writes and synchronizes a private marker beside the learning
database before erasing source records and identity. Every learning transaction
checks the marker before and after acquiring its database lock. Workers stop before
Discord reads, and initialization also refuses a withdrawn store. This prevents
old backup restoration from restarting learning while preserving usage accounting.

## Participation invariants

For each channel, the tracker retains a rolling set of human activity, the last
successful Trubot reply, a UTC daily ambient count, and a monotonically
increasing revision.

1. Every new human message invalidates the previous quiet-period revision.
2. An ambient task can post only if its revision is still current after the
   delay.
3. At least the configured number of distinct humans must remain inside the
   activity window.
4. A successful direct, follow-up, reaction, or ambient reply starts the ambient
   cooldown.
5. Only ambient replies consume the daily quota.
6. Restarting clears ephemeral state; it never manufactures historical state
   from Discord messages.

The event loop serializes tracker mutations. A per-channel `asyncio.Lock`
prevents direct, follow-up, reaction, and ambient generations from posting
concurrently.

## Failure behavior

- SDK retries are disabled. The adapter reserves each bounded transient retry
  separately and retains uncertain charges after errors or cancellation.
- Direct and reaction failures receive one short in-character fallback; inferred
  follow-up and ambient failures are logged and stay silent to avoid unsolicited
  error spam.
- Failed generations do not consume the ambient quota.
- Discord send/fetch failures are logged with IDs, never message contents or
  credentials.
- Disconnecting removes readiness immediately. Resuming recreates and refreshes
  it; shutdown cancels pending ambient work and closes the OpenAI client.

## Privacy and safety

Configured rolling Discord history, bounded attributed source/graph evidence,
and at most two live image inputs can be sent to OpenAI. Private raw stores and
derived graph data stay on the existing volume; no full corpus is injected.
Responses are requested with storage disabled. The API receives a stable SHA-256 identifier
scoped to the Discord guild and requesting user, not their display name or raw
Discord ID. Generated messages cannot create Discord mentions.

The ledger stores only cost metadata, not conversation or personal data. Production
mounts `/srv/app-data/wcb-bot` at `/var/lib/trubot`; the remaining root filesystem
stays read-only. The storage runbook defines retention and recovery.

Learning state uses a separate schema-1 SQLite database on the existing private
volume. Runtime requires owner-only permissions and existing state; missing,
corrupt or unsupported state pauses learning. It never invents a replacement
identity. Background batches are bounded to 50 messages per allowed channel and
separate from channel response locks. Every cycle validates the pinned human
member through authenticated Discord REST without enabling privileged member
intent. Other authors and bot/webhook messages never become Andrew's evidence.

Edits blank old text before refetching; fetch-start timestamps and source edit
versions prevent older snapshots from overwriting corrections. Deletion markers
win over in-flight scans. History pages and cursors commit atomically, so failed
or interrupted scans can resume without losing evidence. Offline changes are
repaired by bounded rotating verification; retrieval refreshes selected native sources before use. Graph derivations require
all their native supports to refresh within a bounded verification budget, and
retain unknown-date qualifications for operator-attributed Slack sources.


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


## Focused quotation recall (2.11.3)

Timing and evidence requests prioritize one explicit quotation in the current
question. Implicit quotation lookup follows only an uninterrupted timing/evidence
chain, stops at a new subject, and rejects ambiguous quotations. Every key still
requires current attributed source support; bot/peer wording never establishes a
human statement. Named topics retain topical search. Qualified day/month/year
questions use timing presentation, while ordinary recall keeps natural language.
Unrelated voice examples are omitted from quotation lookup. No new provider call,
source scope, storage schema, model, participation rule or spending allowance.


## Conditional episode memory candidate

Candidate 2.12.0 represents reviewed humor/style abstractions with conditions,
limitations and linked human counterexamples. Source changes invalidate the whole
pattern. Ordinary relevant context uses the summary; explicit evidence requests
keep source passages. Existing factual memory, five-source bound, fresh native
checks, withdrawal and spending remain. This is enabling work with 24 regression
cases; measured human fidelity is still open. The private pattern remains offline
pending specific OpenAI payload approval. See the evolution research and storage
notes for validation, lifecycle and rollback boundaries.


## Human focus for imaginative follow-ups (2.12.1)

Inferred follow-ups can carry at most 600 characters from the immediately
preceding human setup. Typed conversation, memory, reference and focus origins
prevent retrieved evidence or detached older messages from supplying that topic.
Intervening human chat disables the anchor. The latest question and image pixels
remain focused, recipient judgment remains separate, and added context is reserved
in the existing spending ledger. No extra request, source scope, state or model.

Playful and hypothetical choices may be delivered straight within the fictional
scene without evidence of Andrew's actual favorite or a routine conditional hedge.
Such choices never become human facts. All source, withdrawal, recipient and
emotional rules remain. Earlier amplified humor prototypes failed their research
criteria. The character contract now explicitly distinguishes comic performance
from historical claims and is evaluated with held-out banter and factual controls.
Conditional episode storage
from merged #62 is included as enabling code; its selected private pattern is
still offline and its behavioral study remains open.

## Conditional behavioral domains (2.14.0)

A shared observation registry connects extraction, graph write, sweep and
retirement. `value`, `emotion` and `relationship` use the same conditional
abstraction contract as humor/style. New behavioral kinds cannot omit that
contract. Each requires separated attributed support, bounded applicability,
limitations and linked contrary evidence. Automated studies retain independent
review, tentative status, 30-day expiry, four-hour pacing and the current cohort.

Ordinary replies receive domain-labeled summaries with qualifications, not raw
support quotes. Evidence requests retain source access. Values describe observed
priorities, emotions expressed reactions, and relationships observed interactions;
none establishes hidden motives, mental health or private intimacy. Domain coverage
is enabling conformance, not a validated human trait or measured fidelity gain.
Existing schema-1 data remains readable; no intake, source or spending migration.


Historical distillation studies whole neighboring messages (up to three per side),
with anonymous speaker roles and explicit omitted-context counts. Packet admission
measures the same serialized envelope as the provider adapter, keeps the anchor
and source indexes aligned, and reserves review headroom. Independent extraction
and review receive identical evidence; large prior conflicts still stop at the
existing request limit. This changes no graph schema, intake scope or study pacing.


## Complete live conversational setup, 2.19.3

Native human neighbors and same-channel parents, plus historical adjacent blocks,
are supplied as complete text up to 600 UTF-8 bytes per message. Oversized context
is omitted with an explicit gap rather than silently clipped. Native source/media
gaps, speaker roles, reply links, same-channel scope, bounded reads and mandatory
source freshness remain authoritative. Historical bot context is labeled separately
from peers. Authored-source text ceilings remain unchanged. This does not broaden
intake, persist peers, populate a human trait or add provider/HTTP requests. Existing
withdrawal, spending, privacy and compatible rollback remain unchanged.


## Bounded native context dependencies (2.21.0)

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

## Fresh native dependency reads, 2.22.1

`native_reconciliation.py` uses the existing authenticated ingestor/source locks to
refresh focus and each retained human dependency. The graph rotates at most two
captures per learning cycle and conditionally discards obsolete fingerprints,
orphan dependencies and backups. The six-second ceiling includes selection, with
at most six HTTP reads. Identity/withdrawal/scope are checked at every stage.
Complete context text is ephemeral, not new learning intake or a durable certificate.
No provider request or automatic native pattern permission. Contextual provider-study
integration, derived dependency invalidation and human-held-out evaluation remain next.

The2.22.1 correction uses one current bounded history page for retained dependency
IDs, plus an exact same-channel parent read if needed. Freshness/attribution checks
still apply to every dependency. No new neighbors enter learning/context; missing
nonparents erase obsolete captures without guessing message deletion. No preserved
freshness certificate or automatic native pattern permission. [Transport study](docs/trubot-evolution/evaluations/2026-10-13-native-freshness-study.md).

Native study setup lifecycle (2.23.0): an immutable local tuple of existing capture
metadata accompanies the original study cohort. Current-source/page/parent reads
revalidate every retained dependency before attempts/commit. The shared graph/source
lock binds observation interpreted-with edges and rejects local races. Lookup/describe
validate semantic capture fingerprints; identical recapture preserves memory, while
replacement/removal/expiry invalidates observations/checkpoints/backups. No peer text
is persisted or added to study requests. Reply rendering strips this new local
metadata. Automatic native patterns remain closed pending contextual qualification.


`reply_brevity.py` conservatively recognizes ordinary prose excess in a completed
draft. `openai_responder.py` combines brief and repetition guidance in the existing
one optional quality attempt. Explicit content/reference requests and unfocused
ambient replies retain runway. Current-source checks precede private reuse; the
same ledger purpose accounts for the request without optional transport retries.
Unavailable/empty/incomplete/still-overlong repair preserves the original. No new
source context, storage, tool, model or provider study payload is introduced.

The2.24.1 length repair includes the actual fallible assistant draft and a revision
of the original focused message, so accumulated three-part bot acknowledgements do
not define the replacement. Author binding is repeated at that focus; images remain
in the original input exactly once. The serialized extra text joins the reservation.
Repetition-only payloads stay unchanged. No bot draft becomes human learning evidence.

### Bounded short continuity, 2.24.2

The adapter excludes at most five lexical words and sixty characters from substantial
full-echo recovery. This avoids a cosmetic source recheck/provider request after a tiny
answer. First generation/source checks are unchanged; independent brevity repair still
runs. Six-word or longer-than-sixty-character echoes and twelve-word passages retain
existing recovery. No new model, prompt, storage, intake, tool or spending pool.


## Reviewed rollout previews, 2.25.0

The operator import CLI can validate a whole batch with `--dry-run`. Prospective
writes use the same source/withdrawal lock and validation as committed imports, then
roll back. Beliefs, edges, checkpoints and backups stay unchanged. A later commit
revalidates sources; preview grants no enduring approval or authority to channel text.
Private qualified population remains independent of packaged code and needs actual
behavioral acceptance, expiry, source/contrary lifecycle and operator retirement.


### Complete stored authored reply passages,2.26.1

ContextMemory never slices a stored authored passage into a reply prefix. Complete
UTF-8text up to6,000bytes is forwarded; larger sources retain provenance plus an
internal gap, with no authored prefix or adjacent context. All-omitted packets
disable optional voice examples; exact quotation lookup cannot match omitted text.
Other complete sources and reviewed memory remain eligible under existing source
validation. No schema, retrieval, native intake or provider configuration changes.
Actual request size feeds existing reservation. Native ingestion's separate stored
character cap is unchanged; renderer completeness is not full original-source coverage.


### Authored historical recall,2.26.5

ContextMemory projects ordinary factual recall after current source materialization
and graph selection, before serialization. It omits Slack adjacent text/context gaps
on that route and suppresses optional voice examples. Authored paragraphs, source
metadata and graph conflict scope remain whole. Focused context/joke/explanation/
quote/evidence requests retain the existing setup; native episodes and abstract
projection are unchanged. This adds no provider call, storage or prompt instruction.
The conservative lexical request predicate is not a general semantic intent model.


## Qualified pattern boundary (2.26.7)

The shared abstraction contract applies to all five pattern domains at import and
again at graph lookup, describe and sweep. Stored node kind remains authoritative
for old rows without data.kind. Missing/malformed conditions, unsupported support
counts, shared episodes and duplicate supporting text exclude that observation
without hiding unrelated valid memory. Existing source fingerprints, contrary-source
invalidation, native freshness, expiry and withdrawal remain authoritative. This is
an enabling correction, with no new automatic trait, prompt or provider attempt.
