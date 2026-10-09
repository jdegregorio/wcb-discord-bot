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

### Final evidence for the 08:16 intake run

- Implementation commit `938ff4ce3147fae63cb4cee75767017fd696816b`;
  [PR #27](https://github.com/jdegregorio/wcb-discord-bot/pull/27) merged as
  `37f15ed83954728e9a27451cb9d4ab218fdf5b9c`. The merged tree exactly matches
  the tested candidate. [PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37655433932)
  and [main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37657701466)
  pass. All six gates rechecked on merged main, 156 tests/96.43% coverage.
- GitHub squash, raw REST and auto-merge calls returned server/JSON errors.
  The supported regular merge succeeded with normal protection and passing CI.
  No direct main push, protection changes or check bypass was used.
- Immutable [v2.3.0 release](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.3.0)
  targets that tested merge. [AMD64/ARM64 build](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37659974236)
  succeeded. Existing pi-release-check discovered it and the locked app transaction
  logged `wcb-bot: healthy on release 2.3.0`; no manual rebuild or platform change.
- Verified deployed v2.3.0 digest:
  `sha256:e54ef0e705df983c7c0b05e457162c8dae5953687e9d406e6374ce77aa84822a`.
  OCI revision and installed learning/ingestion/client/app/config hashes match
  release source. Discord readiness healthy, zero restarts, no rollback needed.
- Installed v2.3.0 intake acceptance passes 8/8. Private state grew from seven
  initial messages to 34, with four persistent scan checkpoints. Content-free
  queries verify pinned author/guild, approved channels and aware source timestamps.
  A one-hour observation has 48 successful channel batches, zero learning warnings,
  zero ERROR lines, zero response failures and zero disconnects.
- Installed character checks pass 15/15 after separate rubric review: ten main,
  two held-out and three core voice cases. Sox warmth/relevance, factual restraint,
  grief, family pride, outdoor pride, follow-up judgment, fictional identity and
  Thomas Jones preference remain appropriate. Small samples do not prove universal
  fidelity. Reports are `2026-10-07-character-*-production.json`; no Discord writes.
  Contrary to the preliminary estimate of 13 scenarios, core_voice has three cases.
- Installed evaluation measured 36,977 input, 28,744 cached input and 328 output
  tokens across 15 settled attempts; conservative estimate USD 0.001480565.
  This run's 27 character samples total USD 0.002881595 estimated maintenance cost.
  Final ledger observation: 57 settled attempts, USD 0.00584832 total estimate,
  USD 0.004801175 maintenance and USD 0.001047145 runtime, no uncertain attempts.
  Earlier October spending and billing/off-device backup visibility remain unknown.
- Final private learning backup/restore probe checks integrity, exact pinned audit,
  all scan cursors and 34 source records. Backups stay mode 0600 with seven-day
  retention. No IDs, source text or private derived preferences are exported.
- Concurrent complementary [PR #28](https://github.com/jdegregorio/wcb-discord-bot/pull/28)
  published v2.3.1 during final verification. It adds durable withdrawal to this
  intake path. It was preserved, not rolled back or overwritten. Current healthy
  revision is `d5369a7f7b228798095073807af6c34757112d5f`, current digest:
  `sha256:f822b8fb80daa077d174d0b493928daa0dc56db19fb76d1e9bead4b094ec6990`.
  Installed source hashes match current main. Rebased evidence-only branch passes
  all six gates, 169 tests/96.49% coverage. Prompt/model/responder are unchanged.
  Successor intake acceptance passes 8/8; readiness healthy, zero restarts and
  zero errors/warnings in its first observed cycle. No real learning withdrawal
  or deletion is performed. Fixture /tmp staging vanished on container replacement;
  the self-contained successor probe was rerun through stdin successfully.
- This run adds final evidence only after v2.3.0; it does not take credit for the
  complementary withdrawal implementation. Next roadmap step remains grounded
  preference derivation/retrieval with source freshness and correction propagation.

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
- Final pre-PR gates: locked sync, format, lint, strict types, 169 tests with
  96.49% branch-inclusive coverage, package build and diff check all passed.
  Final ARM64 candidate probe is 7/7 after the directory-sync and runtime
  composition checks. Provider calls and Discord writes remain zero.

- Runtime change: [PR #28](https://github.com/jdegregorio/wcb-discord-bot/pull/28)
  merged normally as `d5369a7f7b228798095073807af6c34757112d5f`.
  [PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37718899000)
  and [merged-main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37718971366)
  passed. Merged main exactly matched the tested tree; all six merged gates passed.
- Release: [v2.3.1](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.3.1)
  targets that tested merged commit. The [image build](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37719061039)
  passed for AMD64 and ARM64 before the app-scoped transaction deployed on
  reverified pi5/aarch64/Ubuntu 24.04.4. No sudo was assumed.
- Running immutable digest:
  `sha256:f822b8fb80daa077d174d0b493928daa0dc56db19fb76d1e9bead4b094ec6990`.
  OCI revision, installed version and all seven inspected source hashes match.
  Previous healthy v2.3.0 is
  `sha256:e54ef0e705df983c7c0b05e457162c8dae5953687e9d406e6374ce77aa84822a`.
  No rollback was needed. Both images retain learning schema 1 and spending state.
- Installed acceptance passes 7/7 with disposable synthetic state. All eight
  installation/continuity checks pass: readiness fresh, real identity still pinned,
  34 real source records preserved, permissions 0700/0600 with UID/GID 10001,
  and existing API attempt counts/estimated balance not reset. No real learning
  withdrawal was performed and no test posts reached Discord.
- Cost snapshot: 57 settled attempts, 141,265 input, 109,007 cached input and
  1,452 output tokens. Conservative app estimate USD 0.00584832 (runtime
  USD 0.001047145, maintenance USD 0.004801175). These include the earlier
  run's character evaluations and normal runtime activity. This complementary
  increment itself made zero provider calls. Earlier October spend remains unknown.
- Recovery: consistent private learning backup passes integrity check and a
  disposable restore preserves counts/identity. Both source and backup remain
  private; live state was never replaced. Off-device recovery/deletion remains
  unverified, with that dependency recorded in the backlog.
- Final health at 2026-10-08T02:48:06.071598+00:00: healthy, zero restarts and fresh readiness.
  Over 287 seconds since startup, zero response failures, ERROR lines,
  disconnects or learning pauses; 4 bounded learning batches completed and
  0 live league posts occurred. This verifies recovery and intake continuity,
  not long-term character fidelity or complete historical coverage.
- Transient GitHub connection failure during PR creation was retried successfully.
  Deployment used the existing immutable transaction and preserved the recorded
  rollback target. Disposable staging was removed after preserving all reports.
  [Evidence PR #30](https://github.com/jdegregorio/wcb-discord-bot/pull/30)
  preserves this rollout without changing runtime source. Its documentation
  conflict with prior-run [PR #29](https://github.com/jdegregorio/wcb-discord-bot/pull/29)
  was resolved by preserving both release records.

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
markers; no attachment download was skipped in this scan. The corpus shares
verified learning identity
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
lossless file/image hashes, exact alias checks, adjacent context, duplicate replay,
withdrawal cleanup and stale-restoration refusal pass without model calls or
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

### Verified historical import rollout

- Runtime [PR #31](https://github.com/jdegregorio/wcb-discord-bot/pull/31) merged as
  `3b9fc24f5100c64f66f30a4aab2f518681480668`. The tested candidate was
  `a73301f9fca9030d7458ffa400a77517202bf88e`; merged main has the identical tree.
  [PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37721030184),
  [main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37721132173),
  and all six repeated local merged gates passed (196 tests, 96.27% coverage).
  Concurrent prior-run documentation was reconciled by preserving both records.
- [v2.4.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.4.0) targets
  that tested merged commit. [Container build](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37721140400)
  passed for AMD64 and ARM64 before deploying through the existing app transaction
  on reverified pi5/aarch64/Ubuntu 24.04.4. Running digest is
  `sha256:02b07f6c17117b708b0e704b514ca6c82012e7d4e8d0d6962995ba518dba9bbf`,
  with matching OCI revision, healthy readiness and zero restarts. Prior healthy
  2.3.1 digest was
  `sha256:f822b8fb80daa077d174d0b493928daa0dc56db19fb76d1e9bead4b094ec6990`.
  No rollback was needed. Rollback retains corpus bytes; older images do not
  implement its cleanup, so withdrawal must use a compatible version.
- Installed CLI synthetic acceptance passes 6/6 without provider calls or Discord
  writes. Real production import confirms 16 documents, 27 distinct origins,
  4,299 speaker blocks, 412 exact-alias target blocks, 405 candidate voice blocks,
  115 native visual episodes and 96 deduplicated original image assets. All
  28 manifest text entries replay as duplicates, with unchanged corpus counts.
  Native visual windows include 11 distinct target messages in 12 episodes.
  This coverage is bounded early-channel development evidence, not full native
  history or completed visual interpretation.
- All ten production data checks pass: exact raw/pixel hashes, Slack attribution,
  adjacent context, native pinned-human attribution and guild scope, source
  timestamps, 0700/0600 permissions, consistent backup/restore, and preserved
  native identity/evidence. The source and image corpus is private on the existing
  app volume. An online archive backup and disposable restore preserve table
  counts and all image hashes. Restore staging used the persistent volume because
  the 62.6 MB image corpus exceeds the 16 MiB ephemeral `/tmp`. Off-device backup
  remains unverified. Temporary production import/validation files were removed;
  workspace originals and the production corpus remain private and available.
- Health at `2026-10-08T03:11:44.957213+00:00` is healthy with fresh Discord
  readiness and zero restarts. During 162 seconds since startup, no response
  failures, ERROR lines, disconnects or learning pauses occurred; four bounded
  learning batches completed. Native learning retains 34 target records.
  Usage remains 57 settled attempts and estimated USD 0.00584832, identical to
  the pre-deploy snapshot. This import made zero model calls and adds no paid
  infrastructure; earlier October spending remains unknown.
- [Installed acceptance](evaluations/2026-10-07-historical-import-installed.json),
  [production data and recovery](evaluations/2026-10-07-historical-import-production.json),
  and [health/usage snapshot](evaluations/2026-10-07-historical-import-health.json)
  preserve content-free evidence. The daily evolution and weekly recap updates
  are verified active with original schedule/model/notification settings.
  They now prioritize contextual studies using actual image bytes, with source
  uncertainty, bounded vision costs, held-out validation and explicit retrieval
  before claims of improved character fidelity.

### 2026-10-07 live memory and vision correction

Joe's baseball test reproduced a real missing capability: the persona prompt
forbade team allegiance, and stored history was not read during responses.
Authenticated Andrew-authored native evidence supports a baseball allegiance.
The 2.5.0 candidate replaces the blanket prohibition with grounded preferences,
retrieves relevant private Slack/native evidence, revalidates native sources,
and supplies image pixels from focus, reply references and recent conversation.
Bot prose and peer preferences remain excluded as personal evidence.

Candidate live acceptance through the real Discord handlers, Responses adapter
and production maintenance ledger passes 5/5: direct and inferred follow-up both
answer the source-supported team; direct and reaction images identify a red triangle, blue circle
and printed label; a prior bot's invented team does not become memory. Sends are
captured, with zero Discord message writes. Unit tests cover attribution, stale
source removal, withdrawal, image bounds, CDN restriction, focus/reference pixels
and image spending reservations. Complete historical interpretation, generated
belief confidence/contradiction management and all-years native context remain
roadmap work.

Production verification: [PR 33](https://github.com/jdegregorio/wcb-discord-bot/pull/33)
merged as `fdcc8bb7817c575a87e5820d82567b7ce556df0b`. PR CI
`37724953704`, merged-main CI `37725067781` and both-architecture publish
`37725155753` passed. Release
[v2.5.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.5.0) is
healthy on pi5 at immutable digest
`sha256:625190b095cf625b300b26ae0a3822844a8bd8230d61c09860718bf391129b2a`.
The platform release timer deployed it; the explicit scoped deployment command
confirmed it was already current. Prior rollback digest is
`sha256:02b07f6c17117b708b0e704b514ca6c82012e7d4e8d0d6962995ba518dba9bbf`.

Installed acceptance passes 5/5 using the released wheel, with no source/dependency
override and zero Discord writes. Health shows zero restarts, errors, response
failures, disconnects or learning pauses and four completed learning batches.
All 16 documents, 4,299 blocks, 115 visual episodes and 96 original assets remain.
The ledger records 102 settled attempts, no unsettled attempts, and conservative
tracked spending of USD 0.011784835 since guard initialization. Earlier October
spend remains unknown. Temporary candidate code, dependencies and private expected
results were removed. Production evidence is
[acceptance](evaluations/2026-10-07-live-context-production.json) and
[health/usage](evaluations/2026-10-07-live-context-health.json).

Joe then requested a living knowledge graph connecting raw exchanges to entities,
distilled concepts, preferences, personality and humor. The current release is
explicitly a foundation, not that graph. [Living memory](living-memory.md) defines
typed nodes/relationships, source provenance and confidence basis, temporal
validity, counterexamples, invalidation, graph retrieval and response-level
acceptance. The daily automation is verified active at 01:00 local time with its
existing model, reasoning, execution and notification settings; its prompt now
directs the next run to implement the first operational graph milestone. The
weekly recap is updated to report graph readiness, continuous updates and source
coverage separately. Implementation is planned, not yet completed.


## 2026-10-08 01:00 run: first connected private graph

Base main is `7e243bbabd66af7cc571f28310feff619e882637`, fetched without resetting
Joe's checkout. All source work uses the new managed worktree
`trubot-daily-20261008-0100` and unique feature branch. No overlapping evolution
PR is open; existing dependency PRs remain separate. The primary checkout is
unchanged. The six-runs-per-day schedule supersedes older cadence notes.

Before: source retrieval depended on keyword/topic overlap. Three private synthetic
paraphrases missed the retained observation's supporting sources and expected
reply terms (0/3). After: entity/concept traversal supplies the connected source
neighborhood to actual direct, reaction and follow-up handlers (3/3), with captured
sends and zero league posts. The graph is private on the existing app volume:
439 eligible target text references, 554 episodes including 115 visual episodes,
96 original image hashes, 11 captured target humans, one qualified claim, one
concept, 1,009 edges and two resumable checkpoints. Raw source stores remain
lossless and authoritative; graph nodes do not copy their text.

A bounded 24-exchange contextual study used the existing maintenance ledger,
validated exact target quotes, and retained one observation with three independent
sources after a separate contextual review. Broader proposals were rejected.
Confidence, timestamps/unknown dates, extraction provenance, status, contradictions
and expiry remain explicit. Runtime source fingerprints and native refetch prevent
stale supports from shaping beliefs. Source changes erase affected derivations and
local graph backups; withdrawal blocks loaded clients and stale restoration while
preserving accounting. Native verification has four seconds per source and six
seconds total to avoid observed two-second Discord refetch timeout flakiness.

All 238 tests pass with 95.88% branch-inclusive coverage; locked sync, format,
lint and strict source typing pass. Synthetic installed-storage-style acceptance
passes 7/7: interruption/restart, connected recall/guild scope, contradictory
preference, online backup/disposable restore, edits/deletion/stale graph restore,
peer exclusion/date uncertainty/suppression, loaded-client withdrawal. Actual
captured generation contexts are 4,161-4,632 bytes; source retrieval took
0.81-3.10 seconds and handler response latency was 3.44-4.58 seconds in the final
three-case candidate sample. A contextual model rubric passes 3/3 with zero
unsupported claims after repairing an observed permanent-allegiance overclaim.

See [content-free candidate evidence](evaluations/2026-10-08-graph-candidate.json).
These are synthetic paraphrases of one studied concept, not independently held-out
human conversations or proof of general character fidelity. Review uses the same
runtime model rather than a human judge. Historical images have graph relationships
but remain unstudied, so no image-derived historical belief enters replies.
Continuous distillation/population, richer entities/humor, native peers/threads and
full historical coverage remain prioritized work. No added paid infrastructure.

The final package build, runtime PR, CI, merged revision, immutable release/image,
installed acceptance, backup/restore, deployed health and final usage are recorded
below as the release cycle completes. Raw studies, responses and expectations stay
private and temporary; no personal conclusion, source ID or message enters Git.


### Verified graph rollout

- Runtime [PR #35](https://github.com/jdegregorio/wcb-discord-bot/pull/35) merged
  as `fdfd2ea52163095255ccafd7728b51b3f488b383`, with the same tree as tested
  candidate `08c6795`. [PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37751230809)
  and [merged-main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37751456378)
  passed. All six local merged-revision gates passed again: 238 tests,
  95.88% branch-inclusive coverage, format, lint, strict typing, locked sync and build.
- [v2.6.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.6.0)
  targets that exact tested commit. [Both-architecture image build](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37751611468)
  succeeded before the existing locked app transaction deployed on reverified
  pi5/aarch64/Ubuntu 24.04. The running immutable digest is
  `sha256:2f21ce0ad4b4819b9dcdc603539bfbe3e7ac2cd3271d416d9c62650a04777412`.
  The OCI revision, installed version and seven installed source hashes match.
  Previous healthy rollback digest is
  `sha256:625190b095cf625b300b26ae0a3822844a8bd8230d61c09860718bf391129b2a`
  (2.5.0). No rollback was needed. Image rollback retains graph bytes; older
  withdrawal tools do not clean them, so use a compatible operator cleanup tool.
- Installed release acceptance uses the actual package with no source/dependency
  override and captures all sends. Connected recall passes 3/3 in direct, reaction
  and follow-up modes, with graph evidence verified in actual generation contexts.
  Installed contextual model review passes 3/3 with zero unsupported claims in
  this sample. Five existing preference, live-pixel and bot-exclusion checks pass.
  Seven installed synthetic graph recovery checks pass without touching the real
  learning identity or invoking real withdrawal.
- Ten production continuity/recovery checks pass. Private graph mode is 0600;
  the pinned identity, 34 native sources, 16 historical documents and 96 images
  remain. Graph population is 439 eligible human references, 554 episodes,
  96 image nodes, 11 captured target humans, one qualified claim and one concept,
  with 1,009 edges and two checkpoints. A private online backup and disposable
  restore preserve counts and connected recall. No live database or ledger was
  replaced. Full source sweep erased zero records in 55.98 ms; paired live/restore
  graph lookups averaged 6.67 ms locally. Source refetch plus graph retrieval took
  0.92-1.65 seconds in installed acceptance, with 3.12-4.20-second reply latency.
- [Installed acceptance](evaluations/2026-10-08-graph-installed.json) and
  [production data/recovery](evaluations/2026-10-08-graph-production.json) contain
  counts and checks only. The final health, accounting and private staging cleanup
  are recorded in the following checkpoint. No historical image understanding,
  continuous distillation or comprehensive personality memory is claimed.


Final health at `2026-10-08T08:59:42.084779+00:00`: healthy readiness, zero
restarts, errors, response failures, disconnects, learning pauses and memory
warnings over 811 seconds. Twelve bounded learning batches completed; there were
no normal league posts in this quiet window. All test sends were captured.
Production and local temporary study copies, private responses, expectations,
candidate modules and disposable restores were removed. Authoritative sources,
the active graph, private seven-day graph backup and usage state remain intact.
[Health/accounting evidence](evaluations/2026-10-08-graph-health.json) records
141 settled attempts, zero unsettled, 450,621 input, 293,990 cached input and
5,942 output tokens. Tracked conservative spending is USD 0.025489775, of which
this run added USD 0.01370494, entirely from the existing maintenance allowance.
Runtime spend is unchanged; no paid infrastructure was added. Estimates are not
billing records, and pre-guard October spend remains unknown. Off-device
recovery/deletion remains unverified. No rollback or permission blocker remains.

Next increment: continuous bounded graph population/distillation with source
invalidation, richer contextual observations and proper held-out conversations.
Preserve the existing spending ledger, withdrawal marker and runtime allowlist.
Image-dependent historical interpretation still requires actual pixel/frame study.


## 2026-10-08 05:00 Pacific run: continuous graph learning candidate

Base `d811d99e333cc2ad7d53a9ff48e43bea391edbf8`, fetched before creating the new
managed `trubot-daily-20261008-0500` worktree and feature branch. No unfinished
evolution PR overlapped. Joe's primary checkout remains untouched at `0d116e9`.

Chosen increment: keep the graph learning from new sources so qualified connected
memory can evolve between operator studies. A synthetic reproduction showed that
new native evidence sorting before the prior Slack cursor stayed outside the graph
(1 source instead of 2). Population now selects missing references in bounded
batches, and a background two-pass text learner creates source-backed tentative
observations through the existing learning lifecycle and maintenance ledger.

One study every four hours considers at most six related excerpts. Exact attributed
quotes, distinct support, conditions, a separate contextual review, source refresh,
atomic fingerprint checks, explicit expiry and recorded conflicts gate acceptance.
Corrections reopen affected studies, withdrawal blocks loaded/restored clients,
and operator retirement prevents automatic reuse of unchanged supports.
Ordinary replies run independently; the learner never posts a Discord message.

All six local gates pass for 2.7.0: 265 tests, 95.67% branch-inclusive coverage,
locked sync, formatting, lint, strict source typing and package build. Synthetic
live acceptance passes 8/8, including actual direct/reaction/follow-up generation
with captured sends, durable pacing, correction and withdrawal. The first fixture
with two exchanges produced zero observations; three distinct dated exchanges
passed extraction and review in 7.62 seconds. Concept-selected questions are not
independent human holdouts, and this sample did not yield a nonlexical alias.
Seven existing synthetic recovery checks also pass.

A private clone of the real graph studied six excerpts (one native, five Slack
with unknown dates) plus ten adjacency blocks in 3.03 seconds. It correctly added
no qualified observation in this sample, using one accounted provider call. Only
counts are public; raw text and derived data remained private and the clone was
removed. This is enabling learning progress, not a measured real-character fidelity
improvement. Native peer setup, complete replies/threads, semantic contradiction
coverage and historical pixel interpretation remain explicit gaps.

[Candidate validation](evaluations/2026-10-08-distillation-candidate.json) separates
synthetic flow evidence from the private rejected packet. No paid service was added.
The conservative 31-day study reservation envelope is USD 1.124928 within the
existing USD 2 maintenance cap. Runtime USD 18 and total USD 20 caps remain.
Release, CI, installed acceptance, live study outcome, backup/restore, digest,
health and final measured usage are recorded after rollout below.

### Verified continuous-learning rollout

- Runtime [PR #37](https://github.com/jdegregorio/wcb-discord-bot/pull/37) merged
  as `59ab845dc2617f9c575f18606e936742b8367940`. Its tree matches tested
  `1437b0cff2abb7e143bcc74bf4ee5b121062bfeb` (`d9c8a29`).
  [Final PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37777789637)
  and [merged-main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37777924644)
  passed. Merged local gates also pass: 265 tests, 95.67% branch-inclusive coverage,
  locked sync, formatting, lint, strict source typing and build.
- Immutable [v2.7.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.7.0)
  targets the tested merged commit. [Both-architecture publish](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37778122825)
  succeeded before the installed locked `pi-app deploy wcb-bot 2.7.0` transaction.
  Reverified pi5/aarch64/Ubuntu 24.04.4. Running immutable image is
  `sha256:880469ddabe26075d43daee59c5d698daac382c4365d0af5e4ea3a37722e4e35`.
  Installed package version, OCI revision and seven runtime source hashes match.
  Previous healthy 2.6.0 image is
  `sha256:2f21ce0ad4b4819b9dcdc603539bfbe3e7ac2cd3271d416d9c62650a04777412`.
  No rollback needed. Image rollback retains graph state; retire any bad new
  observation or restore a verified compatible graph copy separately if required.
  Never replace the usage ledger during recovery.
- Installed acceptance uses the released package with no source/dependency override.
  Live synthetic checks pass 8/8, with three captured direct/reaction/follow-up
  sends and two accounted study calls. Study time was 6.59 seconds. Questions
  were selected from a synthetic concept and did not test independent human
  holdouts or nonlexical aliases. Seven installed synthetic recovery checks pass.
  No real withdrawal or league-channel test post was invoked.
- The actual background worker completed one bounded study and retained zero new
  observations. The graph retains the original qualified claim/concept, 439 human
  sources, 554 episodes, 96 image nodes, 11 captured humans and 1,009 edges.
  Four checkpoints include durable pacing and the rejected anchor. The pinned
  identity, 34 native sources, four approved channels, 16 exports, 4,299 historical
  blocks, 115 visual episodes and 96 original images remain intact. Historical
  pixels remain unstudied. No real-character fidelity gain is claimed.
- Private online pre/post-release graph backups have mode 0600, valid integrity,
  and matching disposable restore counts. The post-release copy also preserves
  the study state and pacing. No live source/graph/usage database was replaced.
  Source correction and withdrawal protections remain authoritative on restore.
  Off-device recovery/deletion remains unverified.
- Accounting after installed validation: 154 settled attempts, zero unsettled,
  480,447 input, 302,405 cached input and 6,679 output tokens. Conservative tracked
  total USD 0.0286188; this run added USD 0.003129025, all maintenance.
  Runtime estimate remains USD 0.001783145. Existing USD 18 runtime / USD 2
  maintenance limits are intact, and no paid infrastructure was added. These
  estimates are not provider billing; pre-guard October spend remains unknown.

[Rollout, acceptance, recovery and cost evidence](evaluations/2026-10-08-distillation-release.json)
contains counts only. Later ingestion cycles preserve the one-study lease; final
health and staging cleanup are recorded below. Next: evaluate genuine
held-out contextual humor/style and improve source neighborhoods and contradiction
coverage. Full native peers, reply/thread history and actual historical frame study
remain separate increments.


Final health at `2026-10-08T12:47:11.398513+00:00`: healthy readiness for 361 seconds, zero restarts,
errors, response failures, disconnects, learning pauses, memory warnings or study
pauses. Eight bounded channel batches completed across two cycles while study
completion remained one, proving the production lease prevented another study.
There were no normal league posts in this window. Usage remained 154 settled
attempts, zero unsettled; all test sends were captured. This is a short rollout
window, not a long-term error-rate guarantee. Private validation code and disposable
studies were removed; only authoritative sources, the graph, documented private
backups and the unchanged usage ledger remain. No routine permission blocker
remains. The evidence-only follow-up preserves runtime source identical to v2.7.0.

## 2026-10-08 user-reported development recall repair

Base `e17574b157f967eebf2c3eeb7126d1a3d9cbeabf`; new managed worktree and unique
feature branch. Primary checkout remains untouched. No evolution PR was open.
Reverified pi5/aarch64/Ubuntu 24.04.4 and healthy v2.7.0, zero restarts, immutable
image `sha256:880469ddabe26075d43daee59c5d698daac382c4365d0af5e4ea3a37722e4e35`.

Authenticated Discord confirms the development guild has two members: its owner
and Trubot. The owner reported baseball and 2020 misses there. A fresh human UI
baseball question reproduced the failure through the running gateway and real send.
Private WCB-scoped retrieval returned five relevant sources; development-scoped
retrieval returned zero. Numeric years were discarded, so a 2020 question selected
unrelated keyword evidence even in the source guild. Imported 2020-labeled exports
exist, but their individual message dates are unknown.

Version 2.7.1 adds owner-only recall in the configured development guild's already
allowed channel and bounded year-aware retrieval. Source attribution, intake scope,
freshness, corrections, withdrawal, graph and usage state remain unchanged. Dated
native evidence outranks export labels; unknown-date graph claims cannot override
the requested period. The daily task now requires actual Discord smoke tests in
this private server, explicitly distinguishes captured-send fixtures, and carries
both reported failures forward. Release and actual post-deploy results follow.

All six candidate quality gates passed: 278 tests, 95.72% branch-inclusive coverage,
locked sync, formatting, lint, strict typing and package build. Regression coverage
includes all three Discord handler paths, owner/guild/channel isolation, unchanged
learning counts, native timestamps, export labels and current-origin removal.

### Verified recall rollout and actual Discord smoke tests

Runtime [PR #39](https://github.com/jdegregorio/wcb-discord-bot/pull/39) merged as
`602e44f9070ac9a089eb3fb6618beb75e4979d72`, with the same tree as tested `96dbf81`.
[PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37791681378)
and [merged-main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37791860508)
passed. All six merged local gates passed again: 278 tests and 95.72% coverage.
Immutable [v2.7.1](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.7.1)
and [both-architecture publish](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37792028135)
succeeded before the locked pi-app deploy on reverified pi5.

Running image is `sha256:d5981cb774329af225d608575e5db684e4769c7ef539cdf2590ed931cdfca7b9`.
Installed package version, OCI revision and all three changed source hashes match.
Previous healthy v2.7.0 remains the compatible rollback target. No schema migration,
ledger replacement, new graph claim or paid infrastructure was introduced.

Four actual owner-authored questions were sent through the authenticated Chrome
Discord UI in the private development server. The running gateway posted all four
answers: direct baseball recall, unmentioned baseball follow-up, a 2020-labeled
historical paraphrase, and an exact historical quotation with the export label and
unknown message date explicit. All four passed private support checks; the quotation
matched an eligible attributed source substring after normalizing punctuation and
whitespace. Three separate maintenance-model reviews passed groundedness, specific
recall and scope honesty. Responses took 2.654-5.900 seconds. No captured send or
injected handler message is counted as a real Discord test. No league test chatter
was posted. Private message IDs and content-free checks are in the app-volume audit;
raw excerpts and derived answer text were removed from that artifact.

One separately built validation client initially shared the running bot's readiness
path. Closing it briefly unlinked that heartbeat and caused one failed health probe.
The bot's regular heartbeat restored readiness without a restart; replies and data
were unaffected. The validation helper was corrected to use its own ephemeral path,
and the daily task now explicitly requires that isolation. Final status is healthy
with zero restarts, response failures, disconnects or learning/memory warnings.
This incident is disclosed separately from the successful recall checks.

Native evidence remains 34 records with zero pending corrections; the graph retains
439 human sources, one claim, 554 episodes, 96 image nodes and 1,009 edges. A current
2020-labeled export contains 75 eligible target blocks. These are grouped blocks,
not dated individual-message counts. Complete native history, larger contextual graph
coverage and actual historical pixel study remain outstanding. Four sampled exchanges
prove this reported routing/retrieval repair, not complete recall or general fidelity.

Ledger after validation: 165 settled attempts, zero unsettled, 510,152 input tokens,
315,945 cached input and 7,035 output. Conservative tracked estimate USD 0.030952825
(runtime USD 0.00386242, maintenance USD 0.027090405). Delta since the first measured
baseline is USD 0.00147874; the earlier reproduction was already included in that
baseline. Provider billing and pre-guard October spend remain unknown. Existing
USD 18 runtime / USD 2 maintenance / USD 20 total limits remain authoritative.

[Content-free release and actual Discord evidence](evaluations/2026-10-08-real-discord-recall.json)
separates sampled support checks, source coverage, the validation heartbeat incident,
health and cost. The daily automation is ACTIVE with its six-run schedule and original
model/settings preserved, and now carries the development context and real-smoke
requirement. No routine access or approval blocker remains.


## 2026-10-08 09:00 natural-memory quality run

Fetched base `be52c3c4386faaa10ae437a435456642876133e7` before creating new managed worktree
`trubot-daily-20261008-0900` and unique feature branch. Prior recall/evidence PRs
were merged; no evolution PR overlapped. Primary checkout remains untouched.
Reverified pi5/aarch64/Ubuntu 24.04.4, app manifest and healthy 2.7.1 immutable
image `sha256:d5981cb774329af225d608575e5db684e4769c7ef539cdf2590ed931cdfca7b9`.
Authenticated membership confirms the private development guild still contains
only its owner and Trubot, and the already-allowed general channel is used.

One fresh actual owner-authored broad-year question reproduced unsolicited
export terminology and a stock exact-date disclaimer through the running gateway.
The existing renderer required this disclaimer. Version 2.7.2 selects content,
timing or evidence presentation from the focused request, preserving the same
source metadata and evidence. Prior bot wording cannot select a disclosure mode.
Broad recall answers should stay natural without claiming unsupported dates;
explicit timing/evidence questions retain relevant uncertainty.

A bounded local audit scanned the latest 100 messages in each of three authenticated league
channels within 14 days: five bot replies and seven target-human messages.
The fourth configured channel is development and is excluded from league counts.
Development latest-40/two-day coverage contained 15 bot replies, including two
explicitly labeled smoke setups; other development exchanges are operator
conversations, not spontaneous league activity. Twelve separately selected eligible
historical human blocks were checked with adjacent source references. Their
calendar dates are unknown and independence across episodes is unproven.
Development contained three metadata disclosures, two unsolicited; the sampled
human blocks contained zero. Median lengths were 12 versus 15.5 words. These
structural counts support a metadata defect, not a general human style or humor
claim. Private content-free audit retains source digest/block/line references.

Automatic approval review rejected raw private excerpts in command logs and a
provider-assisted private-context audit for sensitive egress. A local-only scan
completed without raw output or provider calls. Semantic humor, sincerity, stances,
relationships and full held-out character fidelity were not independently graded;
this limitation remains open. No new persona characteristic was learned.

All six candidate gates pass: 296 tests, 95.79% branch-inclusive coverage, locked
sync, formatting, lint, strict typing and package build. Regression covers focused
request classification, identical grounding across presentation modes, source
removal and immunity to previous bot disclaimers. Live synthetic handler checks
cover direct/reaction/follow-up broad recall, timing, evidence and preferences with
isolated readiness and captured sends. One unmapped lexical team fixture missed
retrieval; adding an explicit query term to that synthetic source produced direct
supported recall. This is a documented vocabulary gap, not added human evidence.

The existing usage ledger and USD 18 runtime / USD 2 maintenance / USD 20 monthly
allowances are preserved. First baseline estimate USD 0.0314292; billing and
pre-guard spend remain unknown. No added infrastructure or schema migration.
Release, required CI, installed checks, actual post-deploy Discord responses,
digest, health, cost and final audit follow after rollout.


### First rollout and source-follow-up correction

[PR #41](https://github.com/jdegregorio/wcb-discord-bot/pull/41) merged as
`49a60d1a622ba0a5f064f821f90432715ab8648f`, identical to tested `35409ea`.
[PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37807424418),
[main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37807585947)
and [both-architecture publish](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37807850522)
passed. Immutable [v2.7.2](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.7.2)
was deployed through the locked transaction on reverified pi5, healthy at
`sha256:2746f2ac877b195147356a91dc2e896e65157088fc9e6a65f4377495380781be`.
All four changed installed source hashes and OCI revision matched the release.

Six actual owner-authored Discord questions produced six running gateway replies.
Five acceptance cases passed: direct baseball, unmentioned baseball follow-up,
broad year recall, exact sourced quotation and exact-date honesty. Ordinary
responses had no unsolicited metadata or replacement stock hedge. The quote
matched a current eligible attributed source substring. Latencies 2.580-4.827 s.
The sixth source question failed continuity: retrieval selected a different passage
and the bot denied having the earlier quotation in its current evidence. This
lookup code was unchanged in 2.7.2. Do not call the six-case acceptance complete.

The same run adds a 2.7.3 repair: a referential date/source question may use a
recent exact quotation as a lookup key, only after matching it against current
eligible authored source text. Bot prose remains non-evidence. Other-guild, peer,
fabricated, changed, wrong-period, stale or withdrawn text cannot satisfy it.
Rendering rechecks the match after materialization. This reconnects the actual
quoted exchange without trusting earlier bot assertions. No new graph claim.
All six gates pass with 299 tests and 95.83% branch-inclusive coverage. A live
synthetic handler source follow-up passes with isolated readiness and the same
maintenance ledger. The final real-source continuity check follows deployment.

The first audit loop incorrectly counted the development channel within the
configured set as league activity. Authenticated channel-guild filtering corrected
the baseline to three league channels, five bot replies and seven target messages.
Public candidate counts and private audit references are corrected. Post-deploy
structural coverage still shows five league bot replies, seven target messages,
20 development bot replies and 12 human blocks. Development window coverage is
latest 40 messages, so counts vary with truncation. Historical learning overlap
is not ruled out; these blocks are not proven independent untouched holdouts.
No new league activity during rollout is a fidelity success claim.

At 16:25:46 UTC, 2.7.2 was healthy with zero restarts/errors, response failures,
disconnects, memory warnings, learning pauses or study pauses. Six posts were
actual development tests. Source stores and graph counts remained unchanged.
Tracked estimated cost USD 0.03555375, runtime USD 0.006749015 and maintenance
USD 0.028804735, 180 settled attempts and zero unsettled. Existing caps remain.


### Final 2.7.3 rollout and real Discord acceptance

[PR #42](https://github.com/jdegregorio/wcb-discord-bot/pull/42) merged as
`8b64810b87e094675868904ce49d41ed216455f8`, identical tree to tested `284d44c`.
[PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37809783106),
[merged-main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37810013379)
and [both-architecture publish](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37810355045)
passed. All six candidate and merged local gates passed: 299 tests, 95.83%
branch-inclusive coverage. Immutable [v2.7.3](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.7.3)
was deployed by the existing release timer; the locked app-scoped transaction
confirmed it current on reverified pi5. Digest
`sha256:fa7a68d86797b7ae09480e4b2d10b4e0863b53184480d787163a3523a8d48c4c`,
installed version, OCI revision and four changed source hashes matched.

All six actual owner-authored questions and production gateway replies passed in
the confirmed private development general channel: baseball, unmentioned baseball
follow-up, broad year recall, exact historical quotation, exact-date honesty and
source continuity through an intervening date question. Ordinary recall had no
routine metadata or mandatory hedge. The quotation matched current eligible
authored source text; years inside that quotation describe its subject matter,
not proof of its calendar date. Latencies were 3.120-8.933 seconds. An additional
unmentioned date probe arrived after the attention window expired and stayed silent;
the accepted date case used an explicit summons. No league test chatter was posted.

The content-free validator initially merged source words across line breaks,
causing a false quotation mismatch. Correct whitespace collapsing and separation
of quoted subject-matter years from message-date assertions repaired that check.
Final six-case report was recorded at 2026-10-09 14:01:02 UTC. Real UI naturalness
review, exact source matching and local attributed-support checks are sampled
acceptance evidence, not independent semantic or human grading of general fidelity.
Private message/source references remain only in versioned app-volume smoke reports
with mode 0600, directory 0700 and documented seven-day manual retention/withdrawal
cleanup. No raw excerpts or derived answer text are stored in those reports.
All validation clients used isolated readiness paths; production readiness survived.

After-deployment local audit at 2026-10-09 09:50 UTC retained five league bot replies,
seven target messages across three channels, 20 development replies and 12 historical
human blocks. Development metadata flags were five, two apparently unsolicited;
human flags were zero. Median words were 21 versus 15.5. The development sample mixes
earlier versions, smoke tests and operator conversations and is clipped to the latest
40 messages. Increased total metadata flags include requested evidence/date answers;
these counts do not establish current-version regression or improved general style.
Historical episode independence and previous learning overlap remain unverified.
The automatic privacy review rejection of raw-output/provider audits left semantic
humor, sincerity, stances and relationships ungraded. No new persona trait was learned.

The extended 2.7.3 health window at 2026-10-09 04:21 UTC was healthy, zero restarts,
errors, response failures, memory warnings or learning pauses, with 560 learning
batches and eight posts. Four gateway disconnects recovered and two generic study
pauses occurred. A later local diagnostic counted eight disconnects, each followed
by resume logs within about 0.24-0.35 seconds, and four study pauses. Their generic
cause logging limits diagnosis and is added to the backlog. No rollback was needed;
this is bounded evidence, not a long-term error-rate guarantee.

Native 34 records, 16 archives/4,299 grouped blocks, 405 eligible target blocks,
75 eligible 2020-labeled blocks, 439 graph humans, 554 episodes, 96 images, one
qualified claim and 1,009 edges remained. No new graph claim or complete-history
coverage is attributed to this increment. Tracked estimate at the extended health
snapshot was USD 0.03920785: runtime 0.01016947, maintenance 0.02903838; 190 settled,
zero unsettled attempts, 611,839 input/358,535 cached input/7,919 output tokens.
The delta from initial USD 0.0314292 includes background and interleaved later-run
activity. Provider billing/pre-guard spending remain unknown; USD 18/2/20 caps
and the existing ledger persist, with no paid infrastructure added.

By final evidence reconciliation, the following run had merged PR #43 and deployed
2.8.0 at `41a89a8cdf8065a466000fb80c22308cc11baa01`. At 2026-10-09 15:24 UTC,
its digest `sha256:7264c60932b0c24864aeddaf63b6dac322525cf98a44f64de93cbdd5ecf28d48`
was healthy with zero restarts/errors/response failures. Its diff preserves this
run's memory and Discord fixes. The evidence-only branch starts from that fetched
main revision and preserves the other run's notes and deployment. This run did not
redeploy an older release or mutate another worktree. Primary checkout is untouched.
[Content-free release evidence](evaluations/2026-10-08-natural-recall-release.json)
records acceptance, audit, cost, health and remaining limitations separately.
The evidence branch reran all six gates on the reconciled 2.8.0 source: 312 tests,
95.90% branch-inclusive coverage, locked sync, format, lint, typing and build pass.
Its only changes are this record, the completed backlog item and content-free JSON.


## 2026-10-08 13:00 - Context-aware graph studies (candidate)

- New managed worktree `trubot-daily-20261008-1300`, feature branch of the same
  run suffix, fetched base `8b64810b87e094675868904ce49d41ed216455f8`. Primary
  checkout untouched. The 09:00 run has released 2.7.3 and is finishing smoke
  evidence; later runs are investigating native recall and legacy persona
  grounding separately. No evolution PR was open during reconciliation.
- Character audit: authenticated pinned membership and private development
  routing rechecked. Local bounded last-100/channel, 14-day scan found five
  league bot replies and seven target messages across three source channels.
  Four configured channels include the separate development channel. Twenty
  development bot replies and 12 eligible held-out unknown-date human blocks
  were scanned with adjacent context. Development median length 16.5 words,
  human 14; metadata flags five versus zero, with two development qualifications
  apparently unsolicited. Earlier-version tests are mixed in the sample;
  these counts do not prove the current version regressed or validate a trait.
- Automatic review rejected printing raw conversations, then rejected sending
  raw private excerpts to OpenAI for a bounded audit. No rejected action ran.
  Used a local content-free audit instead; semantic evaluation awaits explicit
  approval and is incomplete. Private content-free refs are on the app volume
  at `smoke-tests/2026-10-08-1300-quality-before.json`, not public Git.
- Two pre-fix regression tests failed: nearby distinct remarks could establish
  habitual style, and exported neighborhoods lost speaker/position metadata.
  Correction preserves anonymous speaker roles, context flags/positions and
  explicit missing native setup. Related packet selection now prefers separated
  contexts; obvious shared-exchange humor/style proposals fail before paid review
  or graph persistence. Separation is a sampling bound, not proven independence.
- Candidate tests: 312 passing, 95.90% branch-inclusive coverage; formatting,
  strict typing and build pass. An initial lint line-length failure was fixed
  before publication. Final release gates, CI, deployment and real smoke evidence
  follow below. No full-history backfill or new personal observation claimed.
- Production baseline 2.7.3: 439 human source nodes, one qualified claim, 554
  episodes, 96 images, 11 captured humans, 1,009 edges; two rejected automatic
  studies. No automated style/humor observations need retirement.
- Cost baseline: 190 settled attempts, zero unsettled; conservative tracked total
  USD 0.03920785, runtime 0.01016947, maintenance 0.02903838. Pre-guard October
  spend and billing remain unknown. USD 18/2/20 caps and infrastructure unchanged.

- Final candidate all six gates pass: 312 tests, 95.90% branch-inclusive coverage.
  Accounted synthetic live acceptance passes 8/8 with captured sends and isolated
  readiness. Study latency 6.1935 seconds; no nonlexical alias was proposed in
  this sample. This proves the existing connected learning flow survives the
  packet change, not independent human fidelity.
- Actual owner UI pre-release pattern question received a real gateway response
  rejecting universal behavior from two jokes. This already passed in 2.7.3;
  the reproduced defect is the future graph-learning support path, not this
  direct conversational answer. Real post-release checks remain required.


## 2026-10-09 05:00 - Specific self-report graph learning (candidate)

Fresh managed worktree `trubot-daily-20261009-0500`, feature branch of the same
suffix, fetched base `41a89a8cdf8065a466000fb80c22308cc11baa01`. Joe's checkout
stays at `0d116e9`. Earlier style-example, recent-native-context and reply-detection
runs were inspected before selection; their unfinished worktrees remain untouched.
Main contains 2.8.0. No overlapping evolution PR was open. Execution was interrupted
and resumed with updated permissions; no source change or release happened during
that interruption.

Authenticated pinned member and private development membership were reverified.
The last-100/channel, 14-day league audit covers three channels, five older bot
replies and seven target messages. The development last-40 sample contains 20 bot
replies. Twelve eligible historical self-report blocks were reviewed with nearby
speakers. Sparse samples support defect categories, not a universal personality
judgment. No new league activity or pixel-dependent interpretation was claimed.
The audit identified pessimism during human enthusiasm, a current-sports assertion
without support, and a reproduced incorrect historical stance. Related persona and
native-context work remains assigned to earlier runs.

One actual owner-authored development question received an opposite historical
stance from the verified authored source. Retrieval omitted that source; the graph
had no relevant observation. The automatic learner's universal two-source requirement
also excluded a specific, literal self-report. New support-basis metadata and local
full-quotation/first-person gates admit one narrow claim/preference after independent
review. Humor/style still need recurring evidence; source timestamps, tentative status,
30-day expiry, contradictions, edits, deletion, withdrawal and vetoes are preserved.
Packet source indexes prevent index confusion, and extraction targets one proposition.
Trusted exact-source maintenance targeting keeps the existing four-hour gate.

Disposable corpus evaluation simulated the next due cycle, without changing production
pacing or creating a ledger. Three earlier packets were rejected: combined unrelated
claims exceeded bounds, or quoted the wrong support index. The final packet retained
one correctly scoped observation after two passes. Long phrase aliases still missed
the original paraphrase; short, source-supported operator aliases need review before
that wording can recall it. Three other human variations retained two conditional
self-reports and rejected one ambiguous interpretation. Prior learning overlap is
unknown, and this is agent contextual review plus the same runtime model, not an
independent human fidelity benchmark.

All six gates pass: locked sync, format, lint, strict types, 329 tests with 95.81%
branch-inclusive coverage, and wheel/source build. Regression covers single-source
connected recall through direct/reaction/follow-up handlers, full qualifications,
peer/quoted/truncated/hypothetical rejection, pattern exclusion, review rejection,
expiry, source deletion, withdrawal, restart and maintenance pacing. Private evidence
is on the app volume; public aggregate evaluation is in
`evaluations/2026-10-09-selfreport-candidate.json`.

Budget baseline: 198 settled attempts, zero unsettled, estimated USD 0.042584475.
Existing USD 18 runtime / USD 2 maintenance / USD 20 monthly caps remain. No paid
infrastructure or schema migration. Billing and pre-guard October spend are unknown.
CI, merge, release, deployed digest, private population, actual post-release Discord
checks and final health evidence follow below.
