# Run progress

## 2026-10-05: emotional judgment

- Base: `0d116e9bad509317d9a4e9af1bca5232594612d9`, fetched from `origin/main`.
- Worktree: provisioned for this run; branch
  `feature/trubot-daily-2026-10-05-emotional-judgment`.
- Selected increment: sincere, topical engagement with supported excitement and
  difficult news, without blind agreement, current-fact invention, or impersonation.
- Acceptance: the White Sox enthusiasm, correction, and reaction fixtures receive
  warm, relevant replies. Rival preferences remain valid; unverified playoff facts
  stay uncertain; clear follow-ups receive replies; unrelated conversations abstain.
  Family/outdoor milestones and grief receive appropriate tone. No invented human
  actions or forced Thomas Jones references.
- Reproduction: production version 2.1.0 ran 20 synthetic samples through its
  real Discord handlers and Responses adapter. Several baseball replies undercut
  excitement or changed the subject; one current-fact answer asserted an unsupported
  negative. One clear follow-up abstained. No Discord writes occurred.
- Implementation: added emotional/contextual guidance and fictional identity
  boundaries while preserving all 20 curated legacy exchanges. The initial cache key was v5; the correction uses v6.
  The final application version is 2.1.2. The runtime default is GPT-6 Luna. It passed
  the character rubric more reliably than GPT-5.6 Luna on the same candidate
  prompt and fixtures. Added explicitly fictional judgment examples, synthetic
  fixtures, and a bounded evaluator.
- Evaluation: before/after reports and rubric review are saved under `evaluations/`.
  The evaluator tests event routing, real model generation, and captured posting;
  it does not connect a second Discord session or post test chatter. Its CLI exit
  status measures transport only. Agent rubric review is required for tone/fidelity.
- Baseline production: pi5, aarch64, Ubuntu 24.04.4, wcb-bot 2.1.0, healthy;
  immutable image digest `sha256:0694bdcf0cda679dbda7a9229f23e88638729f13204cb1d124beccb38023d2e0`.
  Last 24 hours: one request, one post, zero response failures and zero ERROR lines.
- Attribution: authenticated allowlisted author metadata was corroborated with
  guild membership. No raw messages or account IDs are retained in this repository.
  Repeat verification and pin identity privately in the ingestion increment.
- Cost: API token counts are measured by the evaluator. Monthly app usage is
  currently unknown and has no spending guard. No paid infrastructure is added.
- Validation: all six local gates passed, including 85 tests and 93.22%
  branch-inclusive coverage. The initial candidate passed 28 synthetic samples,
  then production evaluation exposed an unsupported fandom aside. These small,
  unblinded samples do not prove universal fidelity.
- Implementation commit: `d157fde6a44273faff36471ff45eab0cd299abda`.
- [PR #22](https://github.com/jdegregorio/wcb-discord-bot/pull/22) merged as
  `ba8cefc4c70c0194808ba8a814261860eedc1a6d`. Fetched main exactly matched the
  tested source tree. [PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37414805163)
  and [merged-main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37414918536)
  both passed the complete quality gate.
- Initial release: [v2.1.1](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.1.1)
  targeted the tested merged commit. [Image build](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37415052700)
  passed for arm64 and amd64. The timer adopted immutable digest
  `sha256:c83b3963941684a0fd274b8488046a8153ed7369b72a619e666983588cf2cd11`.
  Installed source hashes, model, version, readiness, and zero restarts matched.
- Production evaluation: 14/14 transport checks passed, including 3/3 White Sox
  enthusiasm checks. One other reply invented not rooting for the Sox while
  correctly acknowledging the unknown playoff result. Full-contract rubric
  review was 13/14. Actual outputs and health are retained in the v2.1.1 reports.
- Recovery: 2.1.1 was marked prerelease and removed from stable discovery; its
  tag and digest were not changed. The prior 2.1.0 digest was restored through
  `pi-app deploy wcb-bot 2.1.0` and verified healthy. Stable discovery selected
  2.1.0, preventing the timer from reintroducing the rejected candidate.
- Correction: explicitly keep baseball allegiance unspecified and limit uncertain
  sports replies to uncertainty or an update request. A direct allegiance probe
  was added. Low reasoning and a 512-token total ceiling for inferred follow-ups improve contextual
  judgment on the same low-cost model. No extra generation pass is introduced.
- Corrective candidate: all six required local gates passed with 89 tests and
  93.22% branch-inclusive coverage. Agent review accepted 30/30 synthetic
  samples; all transport checks passed, with complete usage and no provider
  errors. Exact source hashes and usage are retained in the v2.1.2 review.
- Corrective implementation commit: `883e10ae3dad60beea531b030c413311348ffffd`.
- [PR #23](https://github.com/jdegregorio/wcb-discord-bot/pull/23) merged as
  `c51a60da23c8580c61572e774ef097e67b05fa10`. Fetched main exactly matched
  the tested candidate tree. [PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37417436388)
  and [merged-main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37417538110)
  passed the complete quality gate.
- Corrective release: [v2.1.2](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.1.2)
  targets the tested merged commit. [Image build](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37417601295)
  passed for arm64 and amd64. Stable discovery selected 2.1.2 and the existing
  release timer adopted it. The confirmed-host `pi-app deploy` call verified
  the app was already running the same healthy version.
- Final production image: `sha256:dd5b272b4d5b72b5eaf8dd2f967f8a284d8fb0291d9dc9a2c108d6776ecc7eb4`.
  OCI revision, installed source hashes, GPT-6 Luna default, and app version
  matched the tested candidate. The previous recorded image is healthy 2.1.0.
- Final production validation: 15/15 synthetic transport checks and agent rubric
  checks passed, including 3/3 Sox cases, grounded uncertainty/allegiance,
  follow-up participation, core voice, grief, and abstention. Zero provider
  errors and zero Discord writes. Fresh readiness and successful health check;
  zero restarts, response failures, ERROR lines, or disconnects since startup.
  The observation window was 2 minutes 40 seconds, with no live league
  generation during that window. This verifies the released handlers and API
  path, not long-term behavior or human character fidelity.
- Handoff: the plan, prioritized backlog, outputs, usage, source hashes, CI links,
  immutable release/digest, and rollback evidence are saved in Git. Archive the
  managed run worktree after the evidence PR passes CI and merges.
- Follow-up: persistent spending guard, then private verified ingestion and retrieval.

## 2026-10-06: persistent spending guard

- Base: `f70363361862fdbb8dc50b5e4719ddbf0a63403e`, fetched from `origin/main`.
- New managed worktree: `trubot-daily-20261006`; branch
  `feature/trubot-daily-20261006-budget-01`. Joe's primary checkout was untouched.
- Reconciled prior work: emotional-judgment/evidence PRs are merged and 2.1.2 is
  healthy on verified pi5, aarch64, Ubuntu 24.04.4. Open PRs are dependency updates;
  no unfinished evolution improvement overlaps this increment.
- Selected increment: private persistent API usage accounting and a UTC monthly
  spending guard, enabling reliable future ingestion and evaluation within budget.
- Acceptance: every provider attempt reserves conservative cost atomically;
  reservations survive restarts and concurrent channels. Tokens, cached input,
  model, pricing version, and estimated dollars are recorded without content.
  Retries, empty outputs, abstentions, evaluations, and ambiguous failures count.
  Missing/unsafe state and unpriced models stop calls. Runtime gets USD 18 and
  maintenance gets USD 2 of the USD 20 monthly allowance. Synthetic explicit
  exhaustion explains the pause; inferred and ambient exhaustion remains silent.
- Reproduction and fix evidence: `evaluations/2026-10-06-budget-before.json` and
  `budget-after.json`; before two calls, after zero calls on depletion, no Discord
  writes. Live candidate acceptance is 10/10 plus 2/2 held-out checks, reviewed
  separately for warmth, relevance, factual restraint, and identity boundaries.
- Implementation: version 2.2.0, SQLite schema 1, integer nanodollar estimates,
  fail-closed `mode=rw` opening, bounded text input/output, disabled hidden SDK
  retries, separately accounted adapter retries, retained uncertainty across
  months, and 13-month settled-record retention. Personality/model unchanged.
- Required local gates passed: locked all-group sync, format check, lint, strict
  types, 123 tests (94.15% branch-inclusive coverage), and distribution build.
- Storage: prepared `/srv/app-data/wcb-bot` as UID/GID 10001, mode 0700, with
  an explicitly initialized private ledger at 0600. Current production root
  filesystem is read-only; `/tmp` is ephemeral. No raw messages or derived personal
  data are stored. The storage runbook defines backup, correction, deletion,
  restoration, schema compatibility, and rollback limitations.
- Platform prerequisite: [PR #8](https://github.com/jdegregorio/pi-platform/pull/8)
  changes only wcb-bot Compose storage/environment. Base
  `4d50c8591b700697d10dd14ae9d6bc9511e9c6df`; candidate
  `55aa25ea11cc23a40f0c966c8ac9055d91f8f3f9`. Platform CI passed; live candidate
  Compose configuration validated quietly without exposing secrets.
- Baseline production: 2.1.2 at
  `sha256:dd5b272b4d5b72b5eaf8dd2f967f8a284d8fb0291d9dc9a2c108d6776ecc7eb4`,
  healthy, zero restarts. Last 24 hours: zero requests, posts, response failures,
  or ERROR lines. No league test chatter or historical backfill occurred.
- Cost: actual API tokens are measured. Dollar estimates are conservative and
  source-backed, not provider billing. Earlier October app spending remains
  unknown; the first fully covered month will be November. No paid infrastructure
  is added. One initial staging cleanup failure retained its accounted charge.
- Candidate source hashes and rubric review are saved under `evaluations/`.
  Release, deployed digest, merged identifiers, backup/restore probe, and final
  production health/evaluation evidence will be recorded after deployment.
- Follow-up priorities: privately pin verified Andrew identity, bounded incremental
  allowlisted ingestion, preference retrieval, billing reconciliation, and
  off-device backup verification. No identity is guessed or publicly recorded.

- Implementation commit: `12935c6f473c10d8d6adc6ff1e80331037d39ab4`.
  [Application PR #25](https://github.com/jdegregorio/wcb-discord-bot/pull/25)
  merged as `d7c3f341cf5e6043f5bda4effb05ba5ea7483bc7`.
  Fetched main exactly matched the tested candidate tree.
  [PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37435390350)
  and [merged-main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37435553235)
  passed the complete quality gate.
- Platform [PR #8](https://github.com/jdegregorio/pi-platform/pull/8) merged as
  `f3e4fbcab12c41c9fcd4edb8a170441f092c224d`.
  [PR CI](https://github.com/jdegregorio/pi-platform/actions/runs/37435110141)
  and [merged-main CI](https://github.com/jdegregorio/pi-platform/actions/runs/37435400570)
  passed. The existing platform timer adopted it and reconciled only wcb-bot.
  Its prior 2.1.2 image remained healthy with the new bind mount. Live permissions
  are UID/GID 10001, directory 0700, and database 0600. No sudo permission was
  assumed; existing deployment group permissions and platform timers were used.
- Release: [v2.2.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.2.0)
  targets the tested merged commit. The [image build](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37435742228)
  passed and published both arm64 and amd64 images before deployment.
- Deployment: verified pi5 hostname, aarch64, and Ubuntu 24.04 again, then called
  `pi-app deploy wcb-bot 2.2.0`. The app transaction pulled, replaced, waited for
  health, and recorded the immutable version. Current digest:
  `sha256:cada129155dd83f1cd3c758cc3a6bcf46f60b586ccc547e90272a8c9c57ac592`.
  ARM64 architecture, OCI revision, installed package version, and all 13 source
  hashes match the tested release. Previous recorded version/digest is healthy
  2.1.2 at `sha256:dd5b272b4d5b72b5eaf8dd2f967f8a284d8fb0291d9dc9a2c108d6776ecc7eb4`.
  No rollback was needed. An image rollback preserves the ledger but 2.1.2 does
  not enforce this new guard, as documented in the storage runbook.
- Production acceptance: 13/13 synthetic transport and agent rubric checks
  passed through installed release handlers and the real API. Three Sox cases
  share supported excitement without invented sports facts. Grief, family pride,
  uncertainty, identity boundaries, core Thomas Jones voice, mistaken bot-history
  recovery, and inferred abstention remain appropriate. No missing usage or
  provider errors. All outputs are synthetic and retained in JSON reports.
- Depletion acceptance on the installed release: 10/10 cases passed with a
  disposable ledger copy and fake provider. Eight explicit triggers captured a
  pause message, two inferred triggers stayed silent, and zero provider calls
  occurred. The live ledger was never depleted or reset. CI also covers ambient
  silence. No test chatter was posted into league channels.
- Persistence evidence: 13 candidate attempts survived container replacement;
  after production checks the ledger retained 26 settled attempts. Measured
  totals: 64,249 input tokens, 55,983 cached input tokens, 653 output tokens.
  Conservative estimated cost: USD 0.00191958, all maintenance; runtime USD 0.
  This includes the initial disposable candidate cleanup failure. Earlier October
  spend is still unknown. No paid infrastructure was added.
- Health/error evidence at 2026-10-06T08:32:08Z: Discord readiness was fresh,
  the healthcheck exited 0, and the container was healthy with zero restarts.
  Since startup at 08:27:03Z, zero response failures, ERROR lines, disconnects,
  or budget pauses occurred. There were zero actual league generations during
  this five-minute, five-second window, so no long-term error-rate claim is made.
- Recovery evidence: consistent on-host SQLite backups passed `quick_check`;
  disposable restored copies had identical record counts and estimated balances.
  A final backup includes all 26 attempts. Neither probe replaced live state.
  Backup files are 0600 inside 0700 directories. Encrypted off-device recovery
  and administrative provider billing visibility remain unverified follow-ups.
- Validation staging recovery: Docker file-copy could not access the temporary
  tmpfs destination. Fixture staging switched to tar through a container process;
  installed code and live state were unchanged. Staging failures made no provider
  calls. Production acceptance was rerun successfully after staging completed.
- Evidence handoff: final output, source hashes, cost totals, health, error counts,
  and backup/restore probes are retained in this repository. The supplemental
  evidence PR also makes the retention test independent of a fixed future date
  and documents an executable read-only-source backup command. Runtime source
  and the immutable release remain unchanged. Archive this run's worktree only
  after the evidence PR passes CI and merges.

- Final evidence is carried by [PR #26](https://github.com/jdegregorio/wcb-discord-bot/pull/26),
  with initial evidence commit `f44ee0e`. Production remains on the immutable
  tested 2.2.0 commit; the evidence changes do not require another runtime release.

## 2026-10-07 - verified private evidence intake (v2.3.0)

- Run began at 2026-10-07 08:16 UTC. Base:
  `9ac5f50ae2d753f36326d9582977f31859a9c923`. New managed worktree:
  `/Users/jdegregorio/.codex/worktrees/trubot-daily-20261007/wcb-discord-bot`,
  branch `feature/trubot-daily-20261007-0816`. Primary checkout was not changed.
  No unfinished evolution PR exists; eight open dependency PRs are separate work.
- Selected acceptance: uniquely corroborate and privately pin Andrew's stable
  account, ingest only attributed text within the existing allowlist, preserve
  timestamps/checkpoints across restarts, handle edits/deletions and interrupted
  catch-up, and keep replies responsive. No preference inference in this increment.
- Authenticated audit: 400 recent allowlisted messages inspected for metadata,
  one exact-name candidate, 25 corroborating author records across three channels,
  stable account username and guild-member identity agree. No raw text retained
  by the audit and no account IDs published. Private audit and evidence database
  are app-owned mode 0600 inside the existing 0700 volume directory.
- Installed v2.2.0 baseline handler had no durable attributed intake path:
  `evaluations/2026-10-07-ingestion-before.json`. Candidate handler acceptance
  passes 8/8, covering capture, attribution exclusion, resumable catch-up,
  uncached edits, failed correction, deletion, continued replies on storage
  failure and retention: `2026-10-07-ingestion-candidate.json`. All posts captured
  in synthetic channels; zero Discord writes and zero API calls by this harness.
- Implementation: separate private schema-1 SQLite evidence store, explicit
  initialization from the corroborated operator audit, fail-closed permissions
  and identity, stable-member REST revalidation, approved/configured channel
  intersection, one 50-message oldest-first page per channel per five-minute
  cycle, atomic cursor/evidence transactions, and live captures that never skip
  historical pages. Raw edit/delete hooks clear old text; fetch-start timestamps,
  edit versions and deletion markers prevent stale-snapshot resurrection.
- Retention: default 180 days, configurable 1-365; 4,000 text characters and
  10,000 messages maximum, no attachments/other people's text. Two source rechecks
  per channel per cycle repair missed offline changes. This is eventual repair,
  not full-history freshness. Future extraction must revalidate source evidence.
  Raw evidence does not enter prompts yet. Recovery/correction/deletion are
  documented in storage.md; learning backups retained at most seven days.
- Candidate live character regression: 10/10 main cases plus 2/2 held-out cases
  passed separate agent rubric review. Sox excitement remains specific and warm;
  uncertain sports facts, rivalry, grief, family pride, clear follow-up, abstention
  and identity injection remain appropriate. Tone is casual and restrained; this
  is a small sample, not proof of universal fidelity. Reports are synthetic JSON.
- Measured candidate API usage: 29,694 input, 21,628 cached input, 353 output
  tokens; 12 settled maintenance attempts, no provider errors or missing usage.
  Conservative added estimate USD 0.00140103. Intake adds no API/infrastructure
  cost. At 16:48 UTC the existing ledger reports USD 0.004058255 estimated total,
  USD 0.00332061 maintenance and USD 0.000737645 runtime, 41 settled attempts.
  Earlier October spending remains unknown; estimates are not billing records.
- Bounded authenticated candidate intake: membership revalidated, seven source
  messages captured privately, four configured channels considered, maximum 50
  scanned per channel, two nonempty channel cursors advanced. Attribution query
  confirms only the pinned human/guild. No model calls, Discord posts or new access.
- On-host consistent learning backup passed `quick_check`; a disposable restored
  copy preserves identity, counts and checkpoints. Off-device backup remains
  unverified. Existing usage ledger was untouched by learning initialization.
- Required gates passed before PR preparation. Fixture defects (missing display
  name, mixed test clocks, incomplete policy constructor) were fixed before
  accepting the harness. Background transport failures are retried without
  exception payload logging. Final gate and release evidence follow below.
- Previous healthy production image: v2.2.0,
  `sha256:cada129155dd83f1cd3c758cc3a6bcf46f60b586ccc547e90272a8c9c57ac592`.
  Target verified pi5/aarch64/Ubuntu 24.04.4. Docker/deploy group access is present;
  passwordless sudo is unavailable and is not required by the app transaction.
  Pre-release 24-hour log aggregates: zero ERROR lines, zero response failures,
  15 Discord disconnect notices and three posts; readiness remains healthy.
- Automatic review rejected broad printing of a production environment file.
  No values were printed. A safer helper-source/status inspection succeeded,
  so deployment review has no remaining permission blocker. Review-service
  timeout/capacity failures earlier were successfully retried within policy.
- Final pre-PR gates: locked all-group sync, formatting, lint, strict typing,
  156 tests (96.43% branch-inclusive coverage), package build and diff checks pass.

## 2026-10-07 complementary run: durable learning withdrawal

- Initial base: `9ac5f50ae2d753f36326d9582977f31859a9c923`; new managed worktree
  `trubot-daily-20261007-1512`. Joe's primary checkout was untouched.
- Reconciliation: an earlier active run had no PR during the initial dashboard
  check. Private state inspection later exposed its incompatible in-progress
  schema. No state was overwritten or deleted. Its fresh account audit and the
  current authenticated audit agreed after converting string IDs to integers.
  This run's duplicate prototype is preserved locally at `f81a554` on
  `feature/trubot-daily-20261007-1512` and is not part of the released increment.
- Dependency: prior-run [PR #27](https://github.com/jdegregorio/wcb-discord-bot/pull/27)
  merged with CI passing as `37f15ed83954728e9a27451cb9d4ab218fdf5b9c`.
  The complementary branch was rebased onto that fetched main, rather than
  releasing a competing ingestion schema. Live v2.3.0 is healthy at
  `sha256:e54ef0e705df983c7c0b05e457162c8dae5953687e9d406e6374ce77aa84822a`.
- Selected increment: operator withdrawal that cannot be undone by restoring
  stale private evidence, so future learning has a reliable revocation path.
  Version 2.3.1 retains schema 1 and the existing app volume.
- Reproduction: the installed v2.3.0 runbook deletion followed by a compatible
  mode-0600 stale backup restore reinstates the old identity and accepts evidence.
  `evaluations/2026-10-07-withdrawal-before.json` records one of seven new
  acceptance criteria present. This demonstrates a recovery gap, not identity
  confusion or contamination in current production.
- Acceptance: command erases records/identity and documented local learning
  copies; durable marker blocks old restores, initialization, and in-flight
  transactions. A loaded worker stops without Discord reads. Failed cleanup
  remains disabled and a retry succeeds. Spending state and normal replies remain
  available. No real production withdrawal or deletion is performed in validation.
- Candidate: synthetic installed-handler/library probe passes 7/7 locally and
  on ARM64. Unit coverage includes unsafe copy targets, symlink markers, disk
  synchronization failure, stale restores and loaded-worker shutdown. Earlier
  probe staging missed restored-file permissions and was corrected before the
  before/after evidence was recorded. Reports contain only synthetic data.
- Cost: zero API calls, zero Discord writes, zero added paid infrastructure.
  This increment changes no prompt, model, usage ledger, or monthly limits.
- Limitations: off-device deletion/recovery remains unverified. Older images do
  not honor the marker; rollback must preserve the erased identity and must not
  restore stale learning state. Prior individual corrections still require
  reapplying source invalidations after backup restoration. Retrieval remains next.
- Local gates and PR/release/deployment identifiers will be added after verification.
- Final pre-PR gates: locked sync, format, lint, strict types, 169 tests with
  96.49% branch-inclusive coverage, package build and diff check all passed.
  Final ARM64 candidate probe is 7/7 after the directory-sync and runtime
  composition checks. Provider calls and Discord writes remain zero.

## 2026-10-07: Historical league conversation corpus

Joe explicitly authorized historical league Slack exports and broad readable guild
access for development, including older Slack files attached in Discord. This
complementary import increment starts at main
`d5369a7f7b228798095073807af6c34757112d5f` in an isolated managed worktree.
Joe's source checkout remains on its existing revision; private workspace copies
are outside tracked source and excluded from Git and Docker build contexts.

Before: native intake retained only recent target messages, with a default 180-day
floor, and could not import Slack files or preserve peer conversation context.
After: the version 2.4.0 candidate adds a private operator importer with lossless
raw exports, SHA-256 document deduplication, origin records, exact approved alias
attribution, speaker order/line spans and bounded adjacent-context lookup. It
flags missing calendar dates, grouped continuations, thread quotes, previews,
reaction UI, bots and system notices. It also captures 115 native visual episodes
with 96 lossless image assets (62,571,650 bytes), anchored to messages and nearby
speaker context. Twenty-eight external embed references retain missing-pixel
markers; no attachment download was skipped in this scan. The corpus shares verified learning identity
and withdrawal, but does not yet influence generated replies.

Discovery used the existing bot token in production without printing/copying it.
It read the earliest 100 messages of accessible guild text channels: 15 channels
scanned, nine denied history access, 16 supported text attachment occurrences.
Together with 12 supplied upload occurrences (nine unique), the combined manifest
has 28 entries and 16 unique raw exports across 12 legacy league channels.
Candidate import produced 4,299 grouped speaker blocks, 412 target-attributed
blocks and 405 candidate voice blocks, with 27 distinct origin records. One
identical upload origin naturally deduplicates too. Counts are not individual
Slack messages; source date labels do not prove actual message dates.

All 196 tests pass with 96.27% branch-inclusive coverage. Format, lint, strict
source typing, locked sync and package build pass. Real-file disposable import,
lossless hash verification, exact alias checks, adjacent context, duplicate replay,
withdrawal cleanup and stale-restoration refusal pass and lossless image hashes pass without model calls or
Discord posts. See [candidate evidence](evaluations/2026-10-07-historical-import-candidate.json).
The daily evolution and weekly recap prompts now include authorized Slack sources,
private storage locations, contextual evidence studies, historical/current belief
uncertainty and full native Discord context as a separate planned increment.
Existing schedules, execution environment, models and notification policy remain.

Visual capture includes no OCR or inference and does not reconstruct missing
legacy Slack images. The daily/weekly prompts now require actual pixel inspection
for image-dependent learning and separate quoted image text from authored voice.

Release, production import, backup/restore and final health evidence are pending
at this candidate checkpoint. No claim of improved generated voice or complete
all-years native Discord backfill. No ingestion API cost or paid infrastructure.
Next priority is source-backed contextual study and bounded retrieval, validated
on held-out exchanges before runtime use; native peers/threads/backfill and
unknown-date handling remain explicit roadmap work.
