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
  `voice_memory.py` resolves at most three current attributed answer/setup pairs
  through the existing private memory scope, with correction, year and withdrawal
  gates. Examples describe a context, not a biography or habitual trait. Synthetic
  judgment illustrations remain separate and never supply personal evidence.
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
