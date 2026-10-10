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

### Verified 2.9.0 rollout

[PR #45](https://github.com/jdegregorio/wcb-discord-bot/pull/45) passed required
[CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37953139709).
Tested candidate `85baaade277030912864116873f7b89f0fecdc2c` was rebased onto the
previous run's evidence commit `89c6302`; squash merge
`b1e55382e8e66adf641fbc65df6ca556d6a2e5c3` has the identical tested tree.
All six gates passed again on merged main, with 329 tests and 95.81% coverage;
[main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37953287294)
passed. Immutable [release v2.9.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.9.0)
targets that exact commit. Both AMD64 and ARM64
[image builds](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37953474824)
succeeded before deployment.

Reverified pi5/aarch64/Ubuntu 24.04 and the installed app helper/manifest, then used
the existing locked `pi-app deploy wcb-bot 2.9.0` transaction. Running digest is
`sha256:d5ce8498cbe3295466c8de4211df282a46a239b18a013885034c49de99294072`;
previous healthy 2.8.0 digest is
`sha256:7264c60932b0c24864aeddaf63b6dac322525cf98a44f64de93cbdd5ecf28d48`.
Installed package version, OCI revision and three changed source hashes match
merged main. No rollback was required. The container started at 15:43:34 UTC.

One candidate observation was rechecked against the live exact source fingerprint,
complete authored statement and neighboring speakers, then imported through the
existing operator graph path. This was authorized agent operator review, not a new
human review or an automatic production study. Concise conceptual aliases were
reviewed separately; they fixed the original paraphrase's retrieval gap. The
observation remains tentative with unknown message date and 30-day expiry. No
provider call, new Discord post or production pacing change accompanied import.
The original distillation checkpoint stayed byte-identical. Automatic production
study acceptance remains unobserved; clone acceptance simulated the next due cycle.

Actual owner-authored Chrome Discord questions and production gateway replies pass
6/6: the original historical stance, unmentioned follow-up, explicit exact date,
baseball, broad year recall and restraint about habitual traits. Latencies were
4.236, 4.757, 3.751, 3.832, 2.885 and 3.097 seconds. The same original question
changed from an unsupported opposite stance to supported content. Ordinary recall
has no stock metadata disclaimer; the explicit date answer stays briefly uncertain.
Baseball and year answers were compared with current attributed human sources;
the year remains a retrieval cue, not a proven calendar date. No league test posts,
user-token extraction or learning of development messages occurred.

Post-deployment character review covers these six actual replies (median 15.5 words)
against the earlier contextual human study and current supports. The follow-up
repeats the same short stance wording and acknowledges the earlier wrong answer;
these are appropriate in this exchange but do not validate a general catchphrase.
No unsolicited storage explanation, unsupported date or universal habit was found.
The repeated last-100/channel, 14-day league scan still has five older bot replies
and seven target messages across three channels, with zero new league replies
since deployment. Reaction and ambient fidelity were tested through fixtures only,
not new spontaneous league activity. Agent review and the same runtime model are
not independent human fidelity grading; historical episode independence and prior
learning overlap remain unknown. No new enduring personality trait was established.

At 15:50:10 UTC, more than six minutes after startup, Docker health and a direct
readiness probe passed, with zero restarts, errors, response failures, disconnects,
memory warnings, learning pauses or study pauses; eight learning batches and six
reply posts completed. No production graph study had run in this short window.
This is bounded health evidence, not a long-term error-rate guarantee. Learning,
archive and graph online backups passed SQLite integrity checks, and a disposable
restore matched identity and graph counts. Both private evaluation/restore copies
were removed after saving content-free reports, leaving the source, graph, marker
and ledger intact.

Coverage remains 34 native records, 16 archives/4,299 grouped blocks, 405 eligible
target blocks, 75 eligible 2020-labeled blocks, 439 graph human sources, 554 episodes,
96 images and 11 captured humans. Graph now has one qualified claim and one narrow
preference, two concepts and 1,011 edges. No all-years native or visual expansion.
Private artifacts use the existing app-volume `smoke-tests/2026-10-09-0500-*`
prefix, modes 0600/0700, seven-day manual retention and withdrawal cleanup. Only
references, counts, flags and timing are retained; no source or answer prose.

Final conservative ledger estimate at 15:50:36 UTC is USD 0.0479301, comprising
runtime 0.01367732 and maintenance 0.03425278, with 217 settled/zero unsettled
attempts, 687,994 input/374,610 cached input/10,022 output tokens. Delta from the
run baseline is USD 0.005345625, including 12 maintenance requests and seven real
Discord response requests; the ledger is shared with background activity. Existing
USD 18/2/20 caps persist, billing and pre-guard spending remain unknown, and no paid
infrastructure was added. Broader paraphrase coverage, independently held-out
contextual fidelity, native reply/thread history and unvalidated legacy persona
assumptions remain follow-up work. See the
[content-free release evidence](evaluations/2026-10-09-selfreport-release.json).

## 2026-10-09 09:00 run: diagnosable learning outcomes

New managed worktree `trubot-daily-20261009-0900`, branch
`feature/trubot-daily-20261009-0900-0155`, fetched base
`875f11808f99163875ccbc95ff42198f2fb19ab2`. Primary checkout was not edited,
stashed or reset. The initial sandbox fetch could not resolve GitHub; the authorized
network retry succeeded before branch/source mutation. Other active runs and open
PRs were inspected. 2.9.0 is already released; native/reply/persona work remains
other runs' scope. No overlapping evolution PR was open at selection.

Phase 1 reviewed the current production code, earlier failure/evaluation evidence,
a fresh authenticated bounded activity/human-source scan and documented tools/image
capabilities. The latest 100/channel, 14-day league window has five older bot replies
and seven Andrew messages across three channels. The latest 40 development messages
contain 20 bot replies. Twelve eligible unknown-date historical blocks with adjacent
references supplied a structural comparison. Development/human median length is
18/14 words; two requested development metadata references versus zero human
references. Ordinary recall shows no routine metadata disclaimers in this sample.
Semantic humor, emotional judgment and habitual traits were not independently
reviewed, and historical independence/prior-learning overlap remain unknown.

H1-H3 record falsifiable diagnosis, conceptual-recall and skills/generated-image
hypotheses with baseline, acceptance and contrary cases in [research.md](research.md).
Phase 2 chooses H1 as supported enabling work so future memory experiments can
separate missing/invalid evidence from learning failures. Held-out conceptual recall
remains next, followed by native/source-qualified persona context, selective tools
and requested northern-lights/trail-camera attachment prototypes. Reconciled
repository-owned ROADMAP.md and docs/agent-harness.md reflect current memory/vision
and distinguish documented capability from tested behavior. No vendor migration,
image generation or new persona characteristic was shipped.

Reproduced against the installed 2.9.0 package: nine injected failure paths collapsed
into one generic warning, and five completion outcomes lacked diagnostic reasons.
The same 14 isolated synthetic probes on 2.9.1 diagnose 14/14; private payload
exclusion and restart pacing pass 14/14. They open only disposable synthetic stores,
mock every transport, construct no Discord client and make zero provider calls or
Discord writes. This is not measured reply-quality improvement or proof of a
natural production study. The recent 2.9.0 restart had zero studies/pauses at baseline;
older generic events cannot be retrospectively classified.

Runtime now logs only fixed stage/cause/outcome plus source count, study-adapter
request count and elapsed milliseconds. It distinguishes valid abstention and
review rejection from unavailable sources, budget/provider/storage errors and
failed commits. Adapter errors for oversized packets and incomplete/malformed
results are typed without changing behavior or payload bounds. Normal verification,
pacing and no-candidate skips remain DEBUG only. Cancellation propagates. No raw
exception messages/bodies/classes, source/answer text, IDs, paths or source hashes
enter these events. Reservations, source checks, withdrawal, vetoes, four-hour pacing,
learning decisions and all storage schemas remain intact.

All six candidate gates pass: locked sync, format check, lint, strict typing,
345 tests with 96.21% branch-inclusive coverage, and wheel/source build. Regression
covers private failure bodies, typed API/Discord categories, pre-request source-check
stage, atomic commit failure, cancellation, restart pacing and quiet ordinary polls.
Budget baseline is USD 0.0479301, 217 settled/zero unsettled attempts; existing
USD 18 runtime / USD 2 maintenance caps remain. No new provider calls or paid service
were needed for research/diagnosis. Billing and pre-guard October spend are unknown.
See [candidate evidence](evaluations/2026-10-09-study-diagnostics-candidate.json).
CI, merged-source checks, immutable release/digest, installed probes and actual
owner-authored private Discord responses follow below.

### Verified 2.9.1 rollout

[PR #47](https://github.com/jdegregorio/wcb-discord-bot/pull/47) passed required
[CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37957000605)
and merged as `b8d3c2d5b2931f2951b1f64fb8aa2954d17ffa1b`, with the identical tree
to tested candidate `5c2cc59d983f9f777ea934d08ac08046a416a6bc`. All six local gates
passed again on merged main (345 tests, 96.21% coverage); merged
[main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37957219149)
passed. Immutable [v2.9.1](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.9.1)
targets that exact commit. Both architectures
[built successfully](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37957350780)
before deployment.

Reverified pi5/aarch64/Ubuntu 24.04 and used its installed locked app transaction.
Running digest is
`sha256:18aa210b6bb770298dfb4918e6acd5310d7b6b664ec0943b8af285f375324518`;
previous healthy 2.9.0 digest is
`sha256:d5ce8498cbe3295466c8de4211df282a46a239b18a013885034c49de99294072`.
Installed version, OCI revision and both changed module hashes match the tested
merged source. No rollback was needed. Installed isolated probes pass 14/14,
with no provider calls, Discord writes, live-state access or separate client.
The main readiness heartbeat remains healthy throughout.

Actual owner-authored Chrome Discord questions and running gateway replies pass
3/3: baseball, broad year-context quote and explicit exact-date question. Latencies
are 5.275, 4.714 and 3.809 seconds. Ordinary content recall is direct and has no
metadata disclaimers; exact-date uncertainty is concise. The quote matches current
eligible source text; year-labeled provenance is never asserted as a proven message
date. Baseball uses a source-term support check and direct agent reading, not a
full independent semantic grader. These test normal replies after isolated study
failures, not injected failures in the live background learner. No test chatter
entered league channels, no user token was extracted, and development posts were
not learned as Andrew. Private artifacts retain only references/flags/counts/timing.

Post-deployment audit repeats the bounded three-channel latest-100/14-day scan:
five older bot replies, seven Andrew messages and zero new spontaneous league
replies. The latest 40 development messages still contain 20 replies, median 16.5
words, zero unsolicited metadata; the same 12 human blocks have median 14 words
and zero metadata. Window turnover and mixed versions prevent causal character
claims. Direct agent review of the three new responses found no unnecessary
storage explanation, invented date or unsupported habitual extension. Humor,
emotional reactions, ambient timing and broad personality fidelity remain ungraded.

At 16:17:49 UTC, 194 seconds after startup, Docker health and direct readiness pass:
zero restarts/errors/response failures/disconnects/memory warnings/learning pauses/
study pauses, four learning batches and three replies. No natural production
study completed in this short window; the previous four-hour checkpoint is unchanged.
This is bounded health evidence, not a long-term error-rate claim. Identity and
source/graph coverage remain unchanged: 34 native records, 16 archives, 4,299
blocks, 405 eligible human blocks, 115 visual episodes/96 assets, 439 graph human
sources, 554 episodes, one claim, one preference and 1,011 edges. No schema change,
new personality observation or historical/visual coverage expansion.

Private online backups of learning, archive and graph pass integrity checks;
disposable restore integrity and every table count match. The first archive
restore attempt exceeded the container's 16 MiB `/tmp`; rerunning on the approved
private app volume passed and probe copies were removed. Live stores and usage
were never replaced. Documented mode-0600 backups retain seven-day operator
retention and withdrawal handling. Off-device recovery/deletion remains unverified.

Ledger at 16:17:51 UTC: estimated USD 0.04868566 (runtime 0.01443288, maintenance
0.03425278), 220 settled/zero unsettled attempts, 701,624 input/383,016 cached input/
10,059 output tokens. Run delta USD 0.00075556 corresponds to three actual Discord
reply requests; research/diagnostics made no provider call. Existing USD 18/2/20
caps and original ledger persist; billing and pre-guard October spend remain unknown.
Public [rollout evidence](evaluations/2026-10-09-study-diagnostics-release.json)
contains no raw source/answer text or private IDs. App-volume artifacts use
`smoke-tests/2026-10-09-0900-*`, modes 0600/0700, seven-day manual retention and
withdrawal cleanup. Next priority is H2 held-out conceptual recall/contextual
coverage; tools/image prototypes remain explicitly unvalidated H3 candidates.

## 2026-10-09 13:00: grammatical memory connections

Fetched base `d4a207dad1d4a796630134d370b9b1d2614beed0`; new managed worktree
`trubot-daily-20261009-1300`, branch `feature/trubot-daily-20261009-1300-014a`.
Primary checkout and older unfinished native/persona worktrees remain untouched.
No overlapping evolution PR was open. Reverified production pi5/aarch64/Ubuntu
24.04, 2.9.1 healthy with zero restarts, existing immutable digest and deployment
interface. Existing app-scoped credentials are present; no secrets exported.

Both planning phases are recorded in research.md. The authenticated structural
character audit found the same five older league bot replies and seven target
messages, no new spontaneous activity, and 20 development replies. It cannot
establish human traits or semantic/emotional fidelity. Automatic approval review
rejected exporting private raw source/derived payloads into the tool transcript;
a safer content-free app-volume audit completed. Detailed private semantic review
is still a gap, not an inferred Andrew trait. No image-dependent interpretation.

H4: six predeclared new operator-written conceptual phrasings retrieved the existing
reviewed neighborhood in 1/6 cases. A disposable plural-only prototype and final
candidate both retrieve 2/6; the other five positive-case outcomes and all three
control lookups are unchanged. Baseline and candidate use identical sources; no
new graph observation, alias, source or provider request was added. The actual
owner-authored baseline Discord answer on the plural case was already correct,
with recent supported channel context available. This increment fixes retrieval;
it does not demonstrate a generated reply-quality improvement. Four broader
paraphrases remain unresolved. Hypotheses H2/H3 and generated outdoor scenes remain
on the roadmap, with skills/tools and guarded attachment delivery still exploratory.

2.9.2 shares conservative noun-form normalization between reviewed graph phrases,
lexical scoring and existing topic expansion. An explicit 17-noun vocabulary avoids
arbitrary stemming of names and verbs. Phrase boundaries/order and source text
remain intact; exact quotations never use grammatical normalization. No context,
participation, spending, retention, storage-schema or study-pacing limit changed.

Candidate gates passed: locked sync, formatting, lint, strict typing, 376 tests,
96.25% branch-inclusive coverage, wheel/source build. New regression coverage checks
singular/plural equivalence, names/substrings/verbs/order, numeric boundaries,
source correction/deletion, exact quotation, contradictory neighborhoods, freshness,
guild isolation, restart, withdrawal and production-handler source refresh. A stale
fake-channel test clock and a stopped-word score expectation were corrected in the
test harness before passing. Existing tests show no known flakiness or failure.
Installed candidate source probe confirms 2/6 reviewed connections and unchanged
controls. No API call was needed for research/prototype/retrieval checks; the real
baseline reply uses the existing ledger. Pre-run tracked estimate USD 0.049035785,
221 settled/zero unsettled attempts; earlier October spend and billing are unknown.
Full CI/release, installed acceptance, real gateway, health and ledger evidence follow.

### Verified 2.9.2 rollout

[PR #49](https://github.com/jdegregorio/wcb-discord-bot/pull/49) passed required
[PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37985243852),
merged as `bf9196b0d1f4f9f10e45d5e93f50cd0caa852af7`, and has the identical tree
to tested `9de4c7b`. All six gates passed on that merged source again: 376 tests,
96.25% coverage. [Main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37985450282)
passed. Immutable [v2.9.2](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.9.2)
targets the exact tested merged commit. Both architectures
[published successfully](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/37985591556).
The merge succeeded; the CLI's subsequent local branch cleanup tried the primary
checkout's occupied main and failed safely. Manual fetch/detached verification used
only this managed worktree. The primary checkout was never edited or reset.

Reconfirmed pi5/aarch64/Ubuntu 24.04 immediately before the installed locked
`pi-app deploy wcb-bot v2.9.2` transaction. Running immutable digest:
`sha256:f8b3ec1f9cd1cbc4823b05ce20ef3773cc4365015d4bdb4bc01b2e302f9005fc`.
Previous healthy 2.9.1:
`sha256:18aa210b6bb770298dfb4918e6acd5310d7b6b664ec0943b8af285f375324518`.
Installed version, OCI revision and all three changed module hashes match merged
source. An early installed probe read the old container while deployment was
pending; its result was discarded and its artifact replaced only after the
transaction completed and 2.9.2 was confirmed. Final installed replay is 2/6 graph
connections, three unchanged controls. Private identity, withdrawal state, study
pacing, native count and graph coverage match before/after. No rollback was needed.

Actual owner-authored Chrome questions and running gateway answers pass 5/5 in the
authenticated two-member private development guild's existing allowed general:
plural position, baseball, broad year-context quote, exact day and unmentioned
follow-up. Latencies: 7.256, 4.023, 2.677, 3.060, 2.778 seconds. Ordinary recall
has no unsolicited metadata; timing uncertainty is brief. The quote matches current
eligible attributed source under the requested export-period cue; that cue never
proves its message date. Position/baseball checks combine limited term/source checks
and direct agent reading, not independent human grading. The repeated position
uses similar wording appropriately in the same test exchange; it is not evidence
of an Andrew catchphrase. No league posts, user-token extraction or development
learning; private artifacts hold only references, flags, counts and timing.

The changed real case is slower than its single baseline (3.304 seconds). Same-corpus
local retrieval, 20 samples each, has baseline median/max 11.844/14.413 ms versus
installed 21.728/37.827 ms, now including the recovered connection. This is a bounded
CPU/context cost of the retrieval correction, not an API-latency causal estimate
or a concurrency/load benchmark. Four broader paraphrases still miss the graph;
no general reply-quality improvement is claimed. Source text never changed.

Post-deployment structural audit still has five older league replies/seven target
messages and zero new spontaneous league replies. Latest 40 development messages
after the first four smoke replies have 20 bot replies, median 14.5 words. Window
turnover/mixed releases prevent causal voice claims; warmth, reaction/ambient timing,
relationships and broader humor fidelity remain ungraded. The fifth follow-up was
reviewed separately. Private source semantic export remains restricted; safer
aggregate checks do not substitute for independent human-source contextual grading.

At 20:22:20 UTC, 329 seconds after startup, Docker and direct readiness pass with
zero restarts/errors/reply failures/learning pauses/memory warnings/study pauses,
eight learning batches and five posts. One gateway disconnect at 20:19:25.333
resumed at 20:19:25.597 (264 ms); the subsequent real unmentioned follow-up passed.
No repeated disconnect or failed reply occurred in this bounded window. Zero new
production studies completed after deployment. Before release, 2.9.1 classified a
natural six-source, one-request study as `proposal_invalid` at commit, zero accepted.
This resolves the earlier unobserved-classification gap, not extraction success.

Coverage remains 34 native records, 439 graph human sources, 554 episodes,
96 visuals/11 captured human sources, one claim, one preference and 1,011 edges.
No migration or derived-state population. Existing source correction, expiry,
backup/recovery, withdrawal and ledger authority remain; no raw/private data in Git.
Private reports are `smoke-tests/2026-10-09-1300-*`, modes 0600/0700, seven-day
manual retention and withdrawal cleanup. Existing volume ownership/privacy passes.
Temporary candidate/baseline packages are removed after evidence preservation.

Ledger at 20:22:20 UTC: estimated USD 0.05142999 (runtime 0.016827085,
maintenance 0.034602905), 227 settled/zero unsettled attempts, 732,890 input,
394,224 cached input and 10,309 output tokens. Run delta USD 0.002394205:
one baseline plus five deployed real reply requests; research/retrieval probes
made zero provider calls. Original ledger and USD 18/2/20 caps persist, no added
paid infrastructure. Provider billing and earlier October spend remain unknown.
Public [release evidence](evaluations/2026-10-09-lexical-recall-release.json) records
retrieval, real Discord, latency, health, provenance and limitations separately.
Next: four semantic misses, independent private contextual review and valid learner
proposal diagnosis, while reconciling native/persona work. Selective skills/tools
and generated U.P. northern-lights/trail-camera scenes remain guarded experiments.


## 2026-10-09 17:00 run: bounded provider evidence contracts

- Base `282f5f01cc0b013f1f344fa56d28aff45a34c6c7`; new managed worktree
  `trubot-daily-20261009-1700`, branch `feature/trubot-daily-20261009-1700-0975`.
  Primary checkout and older native/persona branches untouched. No evolution PR
  open at selection. Production baseline 2.9.2, immutable digest
  `sha256:f8b3ec1f9cd1cbc4823b05ce20ef3773cc4365015d4bdb4bc01b2e302f9005fc`.
- Both required planning phases recorded as H5 in research.md; roadmap/harness
  priorities reconciled. Selected a contract correction, no new behavioral belief.
  Conceptual recall/native persona work and selective tools/generated scenes remain.
- Audit: three league channels, latest 100 each/14 days, five older bot/seven
  human messages; 20 development bot replies; 12 historical structural passages;
  one actual attributed image inspected. Zero new spontaneous activity. Older
  enthusiasm mismatch predates current fixes; no new style trait inferred.
- Baseline 15/15 malformed synthetic proposals are schema-valid/local-invalid;
  candidate admits 0/15. Local quote/independence/semantic/source gates retained.
  Real adapter comparison: three synthetic packets/revision, nine requests; locally
  valid 2/3 to 3/3, contextual acceptance 1/3 both, ambiguous abstention both.
  Review declined one structurally valid candidate. No generated-quality claim.
- Automatic approval review rejected the private-corpus provider replay before
  execution. Synthetic comparisons and authenticated UI/read-only audits completed
  instead. Natural rejection cause, independent human grading and broader recall
  remain explicit gaps. No private source payload exported or graph populated.
- Cost baseline USD 0.05172174, after synthetic comparison USD 0.053062615,
  delta USD 0.001340875. Existing USD 18/2/20 caps and ledger preserved; zero
  unsettled attempts, no paid infrastructure. Pre-guard spend/billing unverified.
- Version 2.9.3, development-only standards validator, meaningful contract/pipeline
  regressions. All six candidate gates pass: 401 tests, 96.28% branch-inclusive coverage.
  Release/deployment/real Discord results pending.


### 17:00 release and actual validation

- Runtime [PR #51](https://github.com/jdegregorio/wcb-discord-bot/pull/51)
  tested `ff804a9c34642e584eab48816a7049c27f378e73`, merged
  `7de1e39978bf75a7a7c7f5cb1c39400e850ea2dd`; identical tree. PR CI
  38008000100/main CI 38008123720 pass; all six merged gates pass, 401 tests.
- Immutable [v2.9.3](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.9.3)
  targets that commit; AMD64/ARM64 publish 38008204215 succeeds. Reverified
  pi5/aarch64/Ubuntu 24.04.4; locked app transaction deploys
  `sha256:ac3848aa72f1333b2a6f4ade316eeb2181af8b1c69bc5b09aacede94e4a8df24`.
  OCI revision, package/exported version and two installed module hashes match.
  Previous immutable 2.9.2 digest retained; no data migration or rollback needed.
- Installed schemas match 3/3 and review bounds 3/3; diagnostic acceptance 14/14;
  synthetic learner direct/reaction/follow-up/correction/withdrawal 8/8. No provider
  calls or live state in installed synthetic probes. Distinct readiness path is
  supplied before validation-client construction; production heartbeat survives.
- Real owner-authored private Discord: four core checks pass (baseball, eligible
  period-qualified quote, exact-day uncertainty, unmentioned scoped follow-up),
  4.993/2.741/2.091/3.878 seconds. Normal recall natural, no routine metadata.
  One additional restraint answer (3.195 seconds) gives unverified extra personal
  examples; correctly rejecting a universal trait is partial acceptance only.
  Aggregate topics and three peer-only native search results cannot verify stance.
  H6 added above wider conceptual recall; do not claim all five fully grounded.
  No independent human grading or spontaneous current-release fidelity evidence.
- Private content-free IDs, pass/fail, timings, state fingerprints and visual
  provenance are under app-volume `smoke-tests/2026-10-09-1700-*`, modes 0600/0700,
  seven-day manual retention/withdrawal cleanup. No raw answer/source artifact.
  Primary/older worktrees untouched; no league tests or development learning.
- Identity/withdrawal/four-hour pacing/graph counts unchanged: 439 human, 554
  episodes, 96 visuals, 11 captured humans, one claim/one preference/two concepts.
  Two natural rejected studies remain; no new observation or study since release.
- At 00:23:55 UTC, 389-second health window: healthy/direct heartbeat, zero
  restarts/errors/reply failures/disconnects/memory warnings/learning pauses/study
  pauses; eight batches/five replies. Bounded window, not a long-term rate claim.
- Tracked cost USD 0.05531207 (runtime 0.01907654, maintenance 0.03623553),
  run delta USD 0.00359033 for nine synthetic study and six actual reply requests.
  243 settled/zero unsettled; 770,838 input/405,432 cached/11,164 output tokens.
  Original ledger and USD 18/2/20 caps preserved; billing/pre-guard spend unknown.
- [Public release evidence](evaluations/2026-10-09-study-contract-release.json)
  distinguishes contract reliability from reply quality and the rejected private
  replay. Evidence PR/final CI and exact helper cleanup/worktree archive follow.

Post-release audit: unchanged league 5 bot/7 human, zero new spontaneous activity.
Development median 10 words in the latest 40/20 bot sample; no causal quality claim.
One authenticated recent original image was inspected, decoded and SHA-256 hashed
in memory (221,337 bytes); source/hash metadata privately retained, no pixels or
caption. No captured-archive match, so native visual coverage remains incomplete.
Evidence [PR #52](https://github.com/jdegregorio/wcb-discord-bot/pull/52) includes
these limits. Runtime source is unchanged from the tested release.

## 2026-10-09 21:00 run: source-checked contextual voice

- New managed worktree `trubot-daily-20261009-2100`, unique feature branch,
  fetched base `01485e657bd3b21f3abf815ee6650007589477df`. Primary checkout and
  older native/persona worktrees unchanged. No overlapping evolution PR; three
  unrelated dependency PRs remain. Earlier persona prototype reconciled here.
- Both planning phases recorded as H7 in research.md. Twenty catalog entries,
  16 matching answer entries, only four current authored/setup pairs. Select at
  most three with source references, unknown dates and explicit context-only roles.
  Fixed unvalidated biography/habit assertions no longer supply personal evidence.
- Six synthetic matched cases, 24 maintenance calls across baseline/three candidates:
  unsupported legacy personal details 3/3 before to 0/3 after. Supported contrary
  positions, excitement and timing retained. First candidates exposed robotic
  fallback and unsupported apology, repaired before selection. Final social-action
  answer remains less natural; no independent human or general fidelity claim.
- Fresh structural audit: three league channels/latest100/14days, five older bot
  replies/seven authenticated humans, 20 development replies and 12 reused historical
  structural blocks. Three actual human posts and peer context reviewed in UI;
  sparse spontaneous/current-release activity. No new learned observation.
- Current-corpus selector gives three examples/2,462 bytes in about 56-66 ms.
  No provider call added, no new persistence or migration. Source withdrawal,
  correction, scope, ambiguous quotes/media, bounded context and year exclusions
  have meaningful synthetic regression coverage. Actual delivery/release pending.
- Private content-free references/counts at app-volume smoke-tests with 0600/0700
  and established seven-day manual retention/withdrawal cleanup. No league probes,
  source excerpts, derived answer text or credentials in Git/log artifacts.

### 21:00 release and actual validation

- Runtime [PR #53](https://github.com/jdegregorio/wcb-discord-bot/pull/53),
  tested `e8efebb7280d78b357072a93b79e78293bcc8be4`, merged
  `7be0836cbd8e74bc07791c5776130158b789d345`; identical tree `24585735c222c519ab0661f855ad131c5f19343e`.
  PR CI 38023442151/main CI 38023523932 and both-architecture publish
  38023593146 passed. All six merged local gates: 417 tests, 96.36% coverage.
- Immutable [v2.10.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.10.0)
  targets that merged commit. Reverified pi5/aarch64/Ubuntu 24.04.4, manifest,
  helper and enabled release timer. Locked `pi-app deploy wcb-bot 2.10.0` runs
  `sha256:a14d3f4ecf725b1c1e2ae0de2a8b150dc33d7641a2829e029e074ea1beca014c`.
  Previous healthy 2.9.3 digest retained. Version, OCI revision and all 22 module
  hashes match. No schema change, migration, new source population or rollback.
- Installed source-lifecycle acceptance passes 8/8 on disposable synthetic stores,
  without provider calls, live-state access or Discord-client construction. Six
  private identity/source/withdrawal/graph continuity checks pass. Main heartbeat
  healthy after all probes. Native 34; archive 16/4,299/405 eligible; graph 439
  humans/554 episodes/96 visuals/one claim/one preference/1,011 edges unchanged.
- Real owner Chrome questions and actual production gateway replies: five fully
  verified checks of six questions (baseball, current eligible period quote,
  exact-day honesty, recent-event restraint and unmentioned connected follow-up).
  Latencies 4.410/2.157/3.011/1.810/3.084 seconds. Ordinary recall has no metadata
  disclaimer; exact timing remains unknown. Quote is a current attributed excerpt,
  not dated proof. Recent-event baseline was already cautious; no improvement claim.
- The sixth scope response (4.124 seconds) still adds personal position examples
  whose semantic qualification is unverified. Count it as partial, not fully
  grounded. This disconfirms legacy examples as the sole cause, not H7's proven
  source-lifecycle need. H6 remains next with semantic precision/qualified sources.
  Only two fresh baseline questions were sent; four earlier baseline checks reused.
  No independent human grading, league tests, user-token extraction or dev learning.
- Post-deploy audit unchanged league five older bot/seven target messages, zero
  new spontaneous league activity; latest 40 development contains 20 bot replies,
  median 9 words, no unsolicited metadata. Different questions/windows cannot
  establish causal voice improvement. Twelve historical blocks remain reused
  structural coverage; full native/pixel/held-out human studies incomplete.
- At 04:24:29 UTC over 202 seconds: healthy/directready, zero restarts/errors/replyfailures/
  disconnects/memorywarnings/learningpauses/studypauses, four batches/six replies,
  zero new studies. Predeploy one background source-refresh timeout (six sources,
  zero requests, 5,307ms) is diagnosed separately; no cost or retrospective fix claim.
- Tracked estimate USD 0.06007111 (runtime 0.022434085, maintenance 0.037637025),
  run delta 0.00475904; 24 synthetic maintenance and eight actual owner-reply calls,
  275 settled/zero unsettled, 853,167 input/456,411 cached/11,825 output tokens.
  Existing USD 18/2/20 caps preserved, no paid infrastructure. Billing/pre-guard spend
  unknown. Private content-free references/passfail/continuity remain app-volume
  smoke-tests, 0600/0700, seven-day manual retention and withdrawal cleanup.
- [Public validation](evaluations/2026-10-09-source-voice-release.json) separates
  lifecycle, synthetic restraint and actual partial semantic acceptance. Evidence
  PR/final CI, helper cleanup and archive only this run's worktree follow.


## 2026-10-10 01:00 run: H10 recent native episodes

- Base `09a8b6059ff8f7d3ddb85b774bd7a28706969b77`, fresh managed worktree
  `trubot-daily-20261010-0100`, feature branch of the same suffix. Primary checkout
  and older worktrees untouched. No overlapping evolution PR. Reconciled native
  prototype `14f8366`; H7 was already shipped, not reimplemented.
- Both planning phases are in research.md. Actual owner-authored recent/setup
  request returned an undated historical quote. Source-count and UI audit show
  seven recent target posts, five older league bot posts, twenty recent development
  responses, one inspected explicit native reply and an unstudied image gap.
  H6 semantic extras remain unresolved. H9 short-name behavior is deferred after
  the fresh quote passed and eligible historical short-name occurrences were absent.
- Identical-source authenticated baseline/candidate comparison, three predeclared
  operator-written cases: broad recent/setup sources 0 dated of 5 to 3 of 3;
  broad recent 0 of 5 to 2 of 2; recent baseball 3 of 5 to 3 of 3. Candidate supplies
  3/1/3 human context rows and 1/0/0 explicit focus reply links. No undated fallback.
  The second case safely omitted a source at the six-second refresh boundary.
  Baseline retrieval 91.52/82.30/1,563.76 ms; candidate 1,904.77/6,005.73/1,572.24 ms.
  Variable authenticated network reads limit causal latency conclusions. Zero new
  provider calls or Discord writes in these comparisons; no new source/graph claim.
- Candidate has 447 passing tests and 96.44% branch-inclusive coverage, including
  thirty new recent-routing, native-context, handler and lifecycle regressions.
  Formatting, lint, strict types, locked sync and package build pass. Old operator
  message DTOs now preserve reference/media metadata. Optional neighbors follow
  all mandatory refreshes; denial stops reference reads; absent setup/pixels and
  empty recent recall cannot reuse old bot/export text. Current grammar and graph
  contracts, withdrawal, scope, study pacing and ledger remain intact.
- Private count-only reports are under the existing app-volume smoke-tests path,
  0600/0700 with seven-day manual retention and withdrawal cleanup. No raw source
  excerpts, derived observations or generated answer text is retained. A distinct
  readiness path preceded validation-client construction; main readiness passed
  after disposal. Original stores were not cloned or replaced. Container tmpfs
  staging is bounded code only. Source revalidation updates verification metadata.
- Candidate-stage release steps were pending; the verified result follows.

### 01:00 release and actual validation

- Runtime [PR #55](https://github.com/jdegregorio/wcb-discord-bot/pull/55), tested
  `9ffc726943dc308b1584987e9128738079d24284`, merged
  `3a910509846ea4ef399650ecd4933bc31e79faba`; identical source tree. Required
  [PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38037723555),
  [main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38037791048)
  and [both-architecture publish](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38037905665)
  passed. All six local gates rechecked on merged main: 447 tests, 96.44% coverage.
- Immutable [v2.11.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.11.0)
  targets the exact merged commit. Reverified pi5/aarch64/Ubuntu 24.04.4 and app
  manifest/transaction; `pi-app deploy wcb-bot 2.11.0` adopted
  `sha256:2b4d9d2f8892bb6b968e893c0da86f7714ef7316c3679de361cc4e8a0a491865`.
  OCI revision/version/all 23 module hashes match. Previous healthy 2.10.0 digest
  `sha256:a14d3f4ecf725b1c1e2ae0de2a8b150dc33d7641a2829e029e074ea1beca014c`
  remains recorded for rollback. No schema migration, rollback or new service.
- Three installed authenticated probes contain 3/3/2 recent dated sources and
  3/1/2 human context rows; one explicit linked parent in the first case. Elapsed
  4,650/2,734.8/5,103.17 ms. Safely omitted sources/context and network variability
  preclude a latency improvement claim. Identity/withdrawal fingerprints unchanged;
  main readiness healthy after validation clients closed with distinct paths.
- Actual owner Chrome questions and production gateway responses in the confirmed
  two-member development guild: seven core checks and one supplemental explicit
  native reply-link check pass contextual review. Recent quote now matches a
  dated native source instead of the baseline undated export. Unmentioned follow-up
  does not invent a reply or unseen pixels; topical recent recall stays relevant;
  existing preference and historical quote/date controls pass. Explicit parent setup
  matches the authenticated human reply relationship. Broad recall uses dated text.
- Real latencies by case: 5.535/6.953/4.053/4.550/2.374/6.130/4.934/2.757 seconds.
  Zero routine metadata disclaimers. The historical quote matches an eligible
  current source and period hint, not calendar-date proof. Exact day is uncertain.
  Only the recent-quote case has a fresh matched baseline (4.192 seconds, wrong
  recency). Agent review is not independent human grading or general voice evidence.
- Post-deploy audit: three league channels/latest100/14days, seven target posts
  and five older bot replies; no spontaneous current-release league reply. Twenty
  recent development replies reviewed structurally; eight fresh smoke responses
  reviewed against human context overlap that window. Twelve historical blocks are reused,
  not newly held-out human evidence. No new pixels interpreted or trait derived.
- At 08:37:06 UTC, five-minute observation: healthy/direct readiness, zero restarts,
  errors, response failures, disconnects, memory warnings, learning/study pauses;
  four learning batches/eight replies/zero completed studies. Short window only.
  Native 34; archive 16 documents/4,299 blocks/405 eligible; graph 439 human sources,
  554 episodes/96 visuals/11 captured humans/one claim/one preference/two concepts/
  1,011 edges unchanged. Ephemeral neighbors are not durable graph population.
- Tracked estimate USD 0.06522696 (runtime 0.027589935, maintenance 0.037637025),
  delta 0.003559075 from this run's first observed snapshot. Eleven actual reply
  calls (three before/eight after), zero provider-assisted research requests;
  289 settled/zero unsettled, 905,932 input/472,096 cached/12,553 output tokens.
  USD 18/2/20 caps and study pacing preserved; billing/pre-guard spend unknown.
- Private content-free references, timing and pass/fail remain app-volume
  smoke-tests, 0600/0700, seven-day manual retention/withdrawal cleanup. No source
  or answer prose, league test chatter, user-token extraction or development learning.
  [Public validation](evaluations/2026-10-10-native-recall-release.json) separates
  source routing, actual response acceptance and coverage limits. H6/H2 semantic
  precision remains next, then context-qualified graph/coverage and H3 tools/scenes.
  [Evidence PR #56](https://github.com/jdegregorio/wcb-discord-bot/pull/56) holds
  this release record. Final CI/archive status is recorded in automation memory.


## 2026-10-10 05:00 run, implementation checkpoint

Fresh managed worktree trubot-daily-20261010-0500, base
327af434ea8dafa4303c8497749a79b491472adb, unique feature branch. Joe's primary
checkout and older prototypes are untouched. Both planning phases and bounded
authenticated character audit are in research.md. H14 is selected after the actual
past-week quote miss; low reasoning did not improve the six-case synthetic comparison
and concurrent-refresh figures are discarded for harness leakage. Runtime memory
window parsing is being verified; no deployment or general fidelity gain is claimed.

Candidate: 2.11.1, six gates passed, 480 tests/96.49% branch coverage. Same-corpus
source probe passes all three rolling-window cases (3/0/2 eligible selected),
compared with baseline 0/0/2 eligible of 5/4/5. Actual paired baseline returned
no past-week quote; post-release real tests remain pending. No new graph claims,
source state/schema/service or provider calls per reply. Evaluation metadata is
in evaluations/2026-10-10-rolling-recall-candidate.json.


05:00 completion correction: 2.11.1 [PR #57](https://github.com/jdegregorio/wcb-discord-bot/pull/57)
merged and deployed healthy, but actual broad quotes still falsely abstained.
H16's full-context matched replay supports moving fresh evidence near focus.
2.11.2 completes the same rolling-recall increment; final verification follows.
Do not infer all real smoke checks passed from the intermediate release.


### 05:00 final release and actual validation

- Runtime [PR #57](https://github.com/jdegregorio/wcb-discord-bot/pull/57) delivers
  rolling windows; [PR #58](https://github.com/jdegregorio/wcb-discord-bot/pull/58)
  completes fresh-evidence placement after contrary actual replies. Second tested
  head 75bdfc45d30b485d5be765fcce48b0052e856fa3 merged as
  b95e70d78d57c858d0268a0e21fc07432d172ab8; identical tree
  248b409297c5984e06f418bb97d0236836ed15da. All six gates on candidate/merged
  revision: 485 tests, 96.49% coverage. Required [PR CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38052548390),
  [main CI](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38052640290)
  and [image build](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38052710092) pass.
- Immutable [v2.11.2](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.11.2)
  targets that merged commit. Reverified pi5/aarch64/Ubuntu24.04.4 and app manifest;
  locked pi-app transaction runs sha256:b6f33b3c98e5e1eb57dd37f793f1670b961d7bf13143bfa1e0934e751a8543c1.
  Version/OCI revision/all24 module hashes match. Previous healthy 2.11.1 digest
  607e9d8ecaee02111dbd64e41538b6dc95ae7f5ac73084fe371aca617e000bd3 remains
  recorded for rollback; original 2.11.0 was 2b4d9d2f8892bb6b968e893c0da86f7714ef7316c3679de361cc4e8a0a491865.
  No rollback, schema migration, model change or added service.
- Installed selection 3/0/2, all inside week/48hour/topical-week windows, versus
  baseline eligible 0/0/2 of5/4/5. Actual memory-handler probes supply3/2 dated
  sources with3/3 human context rows, 2.396/1.496 seconds. No provider calls in probes.
- Final actual owner Chrome/private confirmed two-member guild/general: eight
  gateway responses, seven fully verified plus one partial. Exact broad question
  now returns an eligible current native quote, versus repeated baseline denial.
  Empty48hour window abstains; topical week quote, supported preference, eligible
  historical period quote, exact historical uncertainty and authenticated linked
  human setup pass. Historical period hints never prove a calendar date.
- Real latencies 4.879/2.864/3.659/4.179/2.311/2.595/3.123/2.497 seconds. No general
  speed or human-fidelity gain claim. One empty reply uses verification vocabulary;
  zero ordinary storage/date metadata caveats. Agent contextual/source review is
  limited and not independent human grading. No current spontaneous league reply.
- H18 new timing defect: the unmentioned native-date follow-up responds but declines
  a known day. A fresh production memory-handler probe supplies one dated native
  source/two context rows and timing guidance in956ms; it is not a missing-date
  archive case. Cause is unresolved. Do not report8/8 full recall or invent a day.
  Source-qualified timing now precedes H6/H2 semantic scope/precision, followed by
  durable native/visual graph context and H3 skills/tools/generated scenes.
- Post-audit3 league channels/latest100/14days:7 target,5 older bot,17 peers;20
  recent development bot replies, overlapping final smoke tests. Twelve reused
  historical structural blocks, no new pixels/traits or held-out human voice grading.
- At12:47:10UTC,348-second observation: healthy/direct readiness, zero restarts,
  errors, response failures, disconnects, memory warnings, learning pauses and study
  pauses;8 learning batches/8 replies/zero completed studies. Short window only.
  Identity/withdrawal/native34/archive16docs4299blocks405eligible and graph439
  human sources/554episodes/96visuals/1011edges unchanged; no development learning.
- Tracked estimate USD0.073770205 (runtime0.03356511, maintenance0.040205095);
  observed run delta0.008543245.24 maintenance research calls cost0.00256807,
  plus21 actual replies (3before/10intermediate/8final).334 settled/zero unsettled;
  1037674input/546483cached/13813output tokens. Existing18/2/20caps and pacing
  preserved; provider billing and pre-guard October spend remain unknown.
- Private content-free IDs/timing/passfail/counts only on app-volume smoke-tests,
  0600/0700, seven-day manual retention and withdrawal cleanup. Validation paths are
  distinct before construction; HTTP-only helpers do not own the main heartbeat.
  No raw source/answer artifacts, new source copies, league chatter or user tokens.
  [Public validation](evaluations/2026-10-10-rolling-recall-release.json) separates
  routing, matched harness experiment, actual replies and the remaining timing miss.

[Evidence PR #59](https://github.com/jdegregorio/wcb-discord-bot/pull/59) preserves
this release record. Final main CI and worktree archive outcome are in automation memory.


## 2026-10-10 09:00 source-qualified referential recall

Base28f73177220b01cb7098e948f023cd2a860086b1; fresh managed worktree
trubot-daily-20261010-0500-7986, feature/trubot-daily-20261010-0900-7986.
The setup name is a leftover scheduling label; this is a separate fresh run after
the completed05:00 task. Primary and older worktrees are untouched. No overlapping
project PR. Both planning phases and bounded authenticated character audit complete.

H18's previous exact-day miss does not repeat in the fresh actual owner sequence;
source creation day agrees. No timing prompt change selected. H19/H20 source lookup
is selected enabling work: baseline12/16 targeted cases fail, candidate16/16 pass;
17 additional boundaries/3 production handler modes. Authenticated native handler
stale quote1 to0 sources after a topic boundary. Real baseline fabricated quote
already abstains; no generated fidelity gain claimed. Existing source, withdrawal,
readiness, scope, participation and USD18/2/20 ledger remain authoritative. First
container staging failed safely; wrong-import output discarded and correct staged
module verified. Runtime release and actual post-deployment checks remain pending.
See research.md and the candidate evaluation for full hypotheses and limitations.

Candidate all six gates pass:521 tests,96.56% branch coverage,36 new regressions.
Version2.11.3. Runtime PR/CI/release and post-release real tests follow.
