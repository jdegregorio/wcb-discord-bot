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
- Fresh structural audit: three league channels/latest 100/14days, five older bot
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
- Post-deploy audit: three league channels/latest 100/14days, seven target posts
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
- Post-audit3 league channels/latest 100/14days:7 target,5 older bot,17 peers;20
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

Base 28f73177220b01cb7098e948f023cd2a860086b1; fresh managed worktree
trubot-daily-20261010-0500-7986, feature/trubot-daily-20261010-0900-7986.
The setup name is a leftover scheduling label; this is a separate fresh run after
the completed 05:00 task. Primary and older worktrees are untouched. No overlapping
project PR. Both planning phases and bounded authenticated character audit complete.

H18's previous exact-day miss does not repeat in the fresh actual owner sequence;
source creation day agrees. No timing prompt change selected. H19/H20 source lookup
is selected enabling work: baseline 12/16 targeted cases fail, candidate 16/16 pass;
17 additional boundaries/3 production handler modes. Authenticated native handler
stale quote 1 to 0 sources after a topic boundary. Real baseline fabricated quote
already abstains; no generated fidelity gain claimed. Existing source, withdrawal,
readiness, scope, participation and USD 18/2/20 ledger remain authoritative. First
container staging failed safely; wrong-import output discarded and correct staged
module verified. Runtime release and actual post-deployment checks remain pending.
See research.md and the candidate evaluation for full hypotheses and limitations.

Candidate all six gates pass: 521 tests, 96.56% branch coverage, 36 new regressions.
Version 2.11.3. Runtime PR/CI/release and post-release real tests follow.


### Release and actual validation outcome

Runtime [PR #60](https://github.com/jdegregorio/wcb-discord-bot/pull/60),
merged 38058d1d13ef29d8871db37e4930548c435a4157, publishes immutable
[v2.11.3](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.11.3).
Candidate 5c388deb79a6aa77b3a2330ea0243514eb054eff and merged tree
268870a79d849f3c086f822b1ce2600ff3b319b0 agree. Required PR CI 38079143742,
main CI 38079224381 and both-architecture image publish 38079298482 succeed.
All six gates rerun on merged source: 521 tests, 96.56% branch coverage,
25 mypy modules and wheel/sdist build pass.

Reverified pi5/aarch64/Ubuntu 24.04.4, manifest and helper before the authorized
locked pi-app deploy. Installed 2.11.3 revision and all 25 Python module hashes
match tested source. Running digest
sha256:d6beaca06f3387329051f4a39f6e7f1ef930f90a76c69bec7b726ffa6c2347af.
Previous healthy 2.11.2 digest
sha256:b6f33b3c98e5e1eb57dd37f793f1670b961d7bf13143bfa1e0934e751a8543c1.
No rollback needed. At 2026-10-10T19:32:20.733743+00:00, healthy readiness and main heartbeat,
zero restarts/errors/response failures/disconnects/learning or study pauses,
11 replies and 12 bounded learning batches since restart.
This bounded health window is not a measured character-quality improvement.

Eleven actual Joe-authored development questions and eleven real gateway replies;
ten acceptance checks pass, one native short exact-day follow-up declines a known
date. Explicit current-source UTC/Pacific dates, fabricated quotation, new-topic
boundary, ordinary preference, historical recall, unknown-date/evidence chain and
empty recent-window controls pass. Ordinary memory language remains natural
without routine metadata disclaimers. Agent contextual UI review and authenticated
source checks supplement keyword screens; no independent human grader. Median
latency 3.600s, range 2.622-7.693s.
No league test chatter. No new spontaneous current-release league activity.
Mechanical verification vocabulary remains in unsupported/empty-window replies.
H18 remains unresolved, not declared repaired.

Four maintenance-ledger provider probes use the same ten-turn actual history and
runtime model/settings. Short installed routing uses the correct source and dates
it while baseline abstains; full wording baseline succeeds but installed gets zero
sources and abstains. Different live verification outcomes prevent an isolated
generation comparison. Cause unmeasured; do not claim no regression or general
reply-quality gain. No timing prompt is shipped. Source routing improvement is
supported separately by matched deterministic and authenticated handler checks.

Native/archive/visual/graph counts, pinned attribution, corrections and withdrawal
remain unchanged. Content-free private references/pass-fail are stored on the
private app volume with seven-day manual retention and existing withdrawal cleanup.
Each HTTP helper uses a distinct ephemeral heartbeat before construction; closing
it leaves main readiness healthy. No source/answer text is retained in smoke reports.

Ledger at end of bounded experiments: USD 0.07757748 total (runtime 0.03666406,
maintenance 0.04091342), 353 settled, zero unsettled; observed run delta 0.003807275,
including four research requests costing 0.000708325. Monthly USD 18/2/20 guard
and four-hour study pacing remain. No added recurring call or paid infrastructure.
Earlier October spend and actual provider billing remain unknown.

Joe's new direction is preserved in plan/backlog, ROADMAP, harness/living-memory
notes, H21/H22 research hypotheses and the automation prompt. Priorities now lead
with abstract values/humor/personality and relational memory, then deliberately
amplified 2-3x creative humor including Thomas Jones cracks. No new human trait
or humor improvement is claimed from this release. Source quotes support audits
and lifecycle corrections; narrow quote/date repairs are secondary reliability.
Six standalone daily times, GPT-6.1 Sol/Extra High and notification preference
are verified unchanged. [Public evaluation](evaluations/2026-10-10-referential-recall-release.json)
records counts, costs, real pass/partial outcomes and limitations. This evidence
follow-up changes documentation only; installed runtime remains the tested release.

[Evidence PR #61](https://github.com/jdegregorio/wcb-discord-bot/pull/61) preserves
this public validation and the new abstract-memory/humor direction. Final evidence
CI, main revision and managed-worktree archive result are recorded in automation
memory. Owned host/container comparison staging is removed; private content-free
validation references remain under the documented retention/withdrawal path.


## 2026-10-10 13:00 conditional episode-memory candidate

Base 662938036b4782cc4a620e4492cce49b3e80d0c5, new managed worktree
trubot-daily-20261010-1300 and feature/trubot-daily-20261010-1300. Previous
release/evidence complete; no overlapping evolution PR. Primary and older
worktrees untouched. Both planning phases and bounded authenticated character
audit complete: 7 target/5 older bot/17 peers, two league channels/latest 100/14
days; 33 unique attributed archive blocks/seven exports/four reserved holdouts.
No new trait in public notes, independent human grader or image interpretation.

H21a selects first-class conditional episode abstractions with linked contrary
sources and authoritative invalidation. Candidate 2.12.0 preserves summary,
conditions, limitations, confidence, temporal metadata and counterexample
fingerprints. Ordinary relevant context omits pattern-only punchlines; factual
support and explicit evidence/quote/time requests remain available. No schema,
model, intake, participation, additional provider request or service change.
Source corrections/suppression/withdrawal and shared spending remain authoritative.

Baseline fails 11/14 initial cases. Candidate passes 24/24 final regressions,
including three actual handler modes and all three selected source refreshes.
All six gates pass: 545 tests, 96.67% branch coverage and wheel/sdist build.
Eight same-input offline cases per arm find a conditional pattern in two relevant
candidate contexts versus none in baseline; other six do not retrieve it.
Original punchlines omitted; relevant packet sizes 6,976/6,564 to 5,547/5,061
bytes. A broad-alias distress match is removed by narrower situations. This is
measured context behavior, not measured generated fidelity or API savings.

Actual owner development baseline produces one fitting joke through the gateway;
it does not reproduce a joke failure or prove a candidate improvement. Specific
private OpenAI study approval is pending after automatic approval review rejected
the eight-call source/pattern baseline study and its unchanged reassessment.
No refused provider call ran, no bypass, and the new pattern remains only in a
mode-0600 disposable app-volume graph. Production 2.11.3 and its graph are unchanged.
Publication/release/deployment and real changed acceptance remain open until
specific approval and the planned validation complete. H22 creative amplification
remains next, followed by context coverage, selective tools and generated scenes.

[Candidate validation](evaluations/2026-10-10-episode-memory-candidate.json) preserves
counts, method, contrary result and exact limitations. Reviewable PR, CI and final
memory follow. Preserve this worktree for continuation; do not archive unfinished
work. Private source/derived data is confined to approved app storage with existing
retention and withdrawal. Spending caps remain USD 18/2/20, no provider research
calls or paid infrastructure. Actual provider billing/pre-guard spend remain unknown.


Draft [PR #62](https://github.com/jdegregorio/wcb-discord-bot/pull/62) is attached
and labeled codex/codex-automation. Tested commit
6a0fd32ca7a09ef679b7b0777d4eb468e1d4ddcf passes required CI 38083335444.
The source increment is fully committed/pushed; preserve this managed worktree
for continuation. No merge, release or deployment while specific provider approval
and changed real acceptance remain unresolved. Production is healthy with zero
restarts and its existing 2.11.3 immutable digest. Live graph has zero abstractions;
source counts, pinned identity and withdrawal are unchanged.

At 2026-10-10T20:21:27.812807+00:00, conservative ledger total is USD 0.079147505,
runtime 0.038234085/maintenance 0.04091342, 358 settled attempts/zero unsettled.
Observed delta since the audit is USD 0.000410625, including the single actual
baseline gateway response. No provider research call or added infrastructure;
USD 18/2/20 limits remain, actual billing and pre-guard spending unknown.
Private count/ref-only evidence and disposable graph stay on the app volume with
seven-day manual retention/withdrawal. Ephemeral module staging and exact local
helpers are removed after preservation. Next run must reconcile this open PR
rather than create overlapping work. Its source/private provider prerequisite
must be resolved before production population or behavior claims.


## 2026-10-10 17:00 - current human topic for imaginative follow-ups

Base 13b09b0356d8361ac8dcf2799ce9e0c23d3352f0, new managed worktree
trubot-daily-20261010-1700 and unique feature branch. Primary and earlier worktrees
untouched. Prior #62 is now merged, but not released when this run starts; its
selected private abstraction stays offline because provider approval is pending.
This run does not send that payload or populate a new human pattern.

Both planning phases completed. Bounded authenticated character audit: two league
channels, seven target/seventeen peer/five older bot messages, ten thematic target
archive blocks/four exports with contextual source refs and four qualitative human
reference contexts. No spontaneous current-version sample or new pixel inference.
Actual owner baseline reproduces a new-topic hypothetical returning the old animal
instead of the current dessert. Explicit/same-subject choices also succeed.

48 initial synthetic humor comparisons and 16 refinement calls reject all
amplification variants. They do not demonstrate six amusement wins; overlong,
distracting and unsupported factual embellishments are observed. The original
2-3x creative goal and Thomas Jones bit remain authorized roadmap work, not shipped
or measured here. H23 16-call 2x2 isolation: baseline 1/2 changed-topic choices,
focus-only 1/2, policy-only and combined 2/2; all two control cases per arm pass.
Framing alone has no isolated quality gain. Select the combined narrow correction
and typed context enabling work, with current human-topic framing and conditional
creative-choice permission. No new source/schema/model/request/participation rule.

Exact final candidate passes four synthetic provider cases. All six local gates
pass: 558 tests, 96.67% branch coverage, 27 typed modules, wheel/sdist 2.12.1.
Dependency versions are preserved. At 00:09 UTC conservative ledger total is
USD 0.087102475, maintenance 0.04694009/runtime 0.040162385; 84 research calls add
USD 0.00602667 maintenance, zero unsettled. Actual billing/pre-guard spend unknown;
USD 18/2/20 guard remains. Private synthetic reports stay on the persistent smoke
volume with seven-day manual retention and withdrawal; no real source/answer text
is retained there. No secondary readiness client was constructed.

PR, merge, release/image and real owner Discord rollout evidence follow below.
Public counts and limitations are in
[evaluation](evaluations/2026-10-10-human-focus-release.json).


### Verified release and actual gateway acceptance

[Runtime PR #63](https://github.com/jdegregorio/wcb-discord-bot/pull/63) merged
209346b0a5572ddc42abc7b9d47d93e1b1cbe52f, identical tree to tested
7a52db3e05f5575b84b966a80344f1fc47fb3e12. PR CI
[38097574312](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38097574312)
and main CI
[38097649909](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38097649909)
pass. All six merged-main local gates pass again, 558 tests/96.67% branch coverage.
Immutable [v2.12.1](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.12.1)
and both-architecture
[publish 38097698875](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38097698875)
succeed. Locked app-scoped pi-app transaction deploys on freshly verified
pi5/aarch64/Ubuntu 24.04.4 without sudo or unrelated service changes.

Running digest sha256:8fd3350b6dc93378f64f55061bbcbf95c0e8758006adb714b3bfc090e5194214.
Previous healthy 2.11.3 digest
sha256:d6beaca06f3387329051f4a39f6e7f1ef930f90a76c69bec7b726ffa6c2347af.
All 27 installed modules match tested source, package/OCI revision agree, main
readiness is healthy with zero restarts. No rollback required; no new live
abstraction is populated, so prior-image graph field compatibility is unchanged.

Real owner-authored Chrome Discord tests in the authenticated two-member private
guild/allowed general pass 10/10: nine actual gateway answers, one verified
recipient abstention. The baseline had five questions/five answers with one
failed new-topic continuation. Same changed scenario now chooses within the new
subject, and a factual follow-up explicitly separates that pick from human
preference. Invited fictional callback, sincere celebration, grief, supported
baseball preference and unsupported event controls pass. Observed answer latency
2.181 to 4.591 seconds, median 3.358; no latency improvement claimed. No user token,
league test post, development learning or second readiness client.

Post-deployment character audit covers all nine actual answers, with four private
human reference contexts. One animal joke repeats older bot wording; broader
variation/voice remains H22 work. No spontaneous current-release league sample,
independent human grader or new pixels. Narrow continuity improves one actual
scenario; no full replica, numeric humor or general human-fidelity claim.

At 2026-10-11T00:21:42Z: zero errors, response failures, disconnects, memory
warnings, learning or study pauses; nine posts, one declined follow-up and four
learning batches. Identity, withdrawal, 34 native records, 16 archive documents,
4,299 blocks/405 eligible target blocks, 115 visual episodes/96 assets and graph
439 sources/554 episodes/1,011 edges remain. Live abstractions zero; selected prior
private pattern remains offline with its approval prerequisite. Actual test
references and reviewed pass/fail/count metadata are private, no raw question or
answer text in artifacts. Synthetic research outputs are separate.

Tracked estimate USD 0.09052265 (runtime 0.04358256/maintenance 0.04694009),
457 attempts/zero unsettled. Run delta USD 0.011375145 includes 84 research calls
and actual gateway activity; research delta USD 0.00602667. No extra recurring
call or paid infrastructure. USD 18/2/20 caps remain; billing/pre-guard October
spend are unknown. Automatic approval review rejected printing an unverified
version environment file; helper-code verification and four allowlisted non-secret
metadata fields provided a safe alternative. No secret was printed or bypass used.

The evidence-only follow-up preserves the rollout without runtime changes.
Retain source/test references before archiving only this run's managed worktree;
leave the older unfinished/private-study worktree alone. Next order is H21's
conditional abstract memory work, H22 re-study, native/visual graph context,
selective skills/tools, generated outdoor scenes. Schedule/model/notifications
and all authorization/privacy/source/withdrawal/spending gates are unchanged.
## 2026-10-10 21:00 - conditional automatic-memory contract

Fetched base 8760432a50ad0570c5fb642c2f69a182047b9bec; new managed worktree
trubot-daily-20261010-2100 and unique feature branch. Primary checkout and older
worktrees untouched. Previous #63/#64 release/evidence are complete; #62's private
population payload remains pending and is never sent or populated by this run.

Both planning phases select H24 as justified H21 enabling work. Missing extraction
and writer fields prevent automatic conditional patterns. Add packet-bound schema,
bounded conditions/limitations/contrary quotes, exact attribution and duplicate,
separation and truncation checks; preserve independent review and source-authority
at atomic commit. Pattern summaries enter the existing graph abstraction reader,
with tentative status, 30-day expiry and new extraction provenance. Checkpoint
cohort remains v3 so existing studies are not forcibly replayed; four-hour pacing,
source scopes, withdrawal, model and spending limits remain unchanged.

Content-free authenticated audit: two league channels/latest 100/14 days contain
seven target, five older bot and seventeen peers; zero current spontaneous sample.
Twelve eligible archive target blocks/four exports/24 neighbors are inspected for
structural coverage, with one media gap. Semantic human and independently held-out
evaluation is unavailable: automatic review rejected raw private transcript export,
and the safer count-only alternative succeeded. No new pixels or derived human
pattern are claimed. One actual owner baseline receives a brief topical joke;
this is a control, not a reproduced reply-quality defect or amusement gain.

Baseline 4/13 synthetic contract failures; candidate 29/29 new regressions pass,
including pipeline recall, contrary-source mutations during review, retirement,
reviewer rejection, bot/peer refresh exclusions, truncation, duplicates and pacing.
Seven guarded synthetic provider calls: six-call baseline/candidate comparison
abstains on the fictional pattern in both arms and preserves a specific self-report;
one supplied-output call validates populated conditional schema compatibility.
No automatic extraction-quality or human-fidelity gain is measured. All six local
gates, CI/release, installed conformance and actual Discord rollout follow below.

Final local gates pass: locked sync, format, lint, 27-module strict typing,
587 tests/96.76% branch coverage and wheel/sdist 2.13.0. Dependency versions are
unchanged. Pre-release tracked estimate USD 0.0923674, 465 settled/zero unsettled;
seven synthetic maintenance calls add USD 0.001205875, one actual baseline adds
USD 0.000638875. Actual billing and pre-guard October spend remain unknown.
Production 2.12.1 remains healthy with zero restarts and its main heartbeat intact.
Candidate counts and limitations are in
[the evaluation](evaluations/2026-10-10-conditional-distillation-candidate.json).

Release verification: [PR #66](https://github.com/jdegregorio/wcb-discord-bot/pull/66)
merges tested f4e7e2165fc055c425c44cf298d8b41b06973106 as
2d884d02208f6e5f81db6d9bcb5b722c06a37886; trees match. All six merged-main
local gates pass again. [PR CI 38111018419](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38111018419),
[main CI 38111102443](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38111102443)
and both-architecture
[publish 38111187987](https://github.com/jdegregorio/wcb-discord-bot/actions/runs/38111187987)
succeed. Immutable [v2.13.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.13.0)
targets that exact merged commit. The freshly verified pi5/aarch64/Ubuntu 24.04.4
app-scoped locked transaction deploys without sudo or unrelated service changes.

Running digest sha256:3e4b32b1574253c3f0ba6acb412d0de070f13b2395a660ceed88d46c6c45fb5d,
OCI revision matches release, package is 2.13.0 and all 27 installed modules match
tested source. Previous healthy 2.12.1 digest
sha256:8fd3350b6dc93378f64f55061bbcbf95c0e8758006adb714b3bfc090e5194214.
Previous reader supports conditional records; no new real abstraction is populated
and no rollback is needed. Source/identity/withdrawal state and graph counts remain:
34 native records, 16 archives/4,299 blocks/405 eligible target blocks,
115 visual episodes/96 assets, 439 graph sources/554 episodes/1,011 edges,
one claim and one preference, zero human abstractions.

Actual owner-authored Discord acceptance passes 6/6 in the authenticated two-member
private development guild's allowed general. Two changed cases use the released
production on_message handler with an isolated invented graph and actual authenticated
Discord sends: playful brainstorming applies the abstract mechanism without copying
source punchlines; a serious vote receives sincere advice without jokes or memory
metadata. The graph was prepared with deterministic study outputs to test writer
conformance, not real automatic extraction. A separate readiness path was set before
client construction; closing it preserves the main heartbeat. No secondary gateway,
league test posts, production graph mutation or development learning.

Four further normal gateway cases pass: supported natural baseball recall, invited
fictional Thomas Jones callback, sincere care, and verified abstention for another
recipient. Three actual gateway answers plus one abstention are distinct from the
two handler-driven actual sends. Post-release character audit covers all five actual
answers. A joke repeats an older sentence frame and a care answer repeats older wording;
H22 variation remains unresolved. There is no current-release spontaneous league
sample, new semantic human/pixel study or independent grader. Numeric humor and
general character fidelity are unmeasured.

At 2026-10-11T04:31:10Z: healthy, zero restarts/errors/response failures/disconnects,
memory warnings, learning or study pauses; three normal gateway posts, eight learning
batches and zero study completions. Release timer active. Content-free private test
references, pass/fail metadata and the invented helper are retained under the existing
seven-day manual smoke retention/withdrawal policy; disposable invented graph and
owned host/container staging are removed. Main heartbeat remains healthy after cleanup.

Tracked October estimate USD 0.09447425 (runtime 0.045720885, maintenance 0.048753365),
471 settled/zero unsettled attempts. Total run delta USD 0.0039516; seven synthetic
research calls add USD 0.001205875. Same USD 18/2/20 caps, no additional recurring call
or infrastructure. Actual billing/pre-guard spending remain unknown. Automatic
approval review rejected raw private transcript export; the safer content-free audit
succeeded without bypass. The earlier selected private pattern's approval prerequisite
remains pending, and that payload was never sent or populated.

H24 is delivered as qualified-memory enabling work. Next: H21 actual contextual
abstraction learning/validated population, H22 variation, H25 native/visual coverage,
selective skills/tools and generated U.P. aurora/trail-camera scenes. The complete
privacy-safe [release evidence](evaluations/2026-10-10-conditional-distillation-release.json)
separates conformance, actual delivery and unresolved quality claims. The follow-up
evidence PR changes documentation only; preserve evidence before archiving this run's
managed worktree and leave older pending work untouched.

## 2026-10-11 01:00 - conditional behavioral graph domains

Fresh fetched base7c0eb6eb7a20cbbb104f5a3b3bfd114bc5c20f5f, managed worktree
trubot-daily-20261011-0100, unique feature branch. Primary checkout and older
worktrees unchanged. No overlapping evolution PR. Both planning phases and audit
are recorded in research.md; selected H26 extends H21 representation coverage.
Baseline 24/42 invented contract failures, candidate42/42; no human pattern learned.
Release, installed acceptance and actual post-deployment Discord remain pending.

Candidate conformance: 55/55 new synthetic regressions; baseline original42 cases
had24 failures. Provider matched comparison9 calls gives no spontaneous new-domain
proposal; three supplied-output calls pass schema conformance. Existing four-hour
cohort, two-pass calls, model and USD18/2/20 caps are unchanged. No private pending
payload sent and no human graph observation populated. Actual installed Discord
acceptance and release evidence follow after deployment.

### Verified 2.14.0 rollout, 2026-10-11T08:27Z

- Runtime PR [#68](https://github.com/jdegregorio/wcb-discord-bot/pull/68) merged
  `cec3dcb1cd2d341a311eb5729778f79c17e8ac67`; tested
  `64322204514a7436d9c1454dd65794fea0352a85` has the identical tree.
  Required PR CI38124052069 and merged-main CI38124175380 pass. All six local
  gates pass before and after merge:642 tests/96.77% branch-inclusive coverage,
  27 typed modules, wheel/sdist2.14.0. Dependency versions are unchanged.
- Immutable [v2.14.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.14.0)
  targets the tested merge; image publish38124257650 succeeds for ARM64/AMD64.
  Reverified pi5/aarch64/Ubuntu24.04.4, manifest, helper lock/rollback and secret
  permissions. Existing app transaction deploys without sudo or unrelated changes.
- Running digest `sha256:759c6a15419811a5c2a52e164d65fced57b6b2c1602f51a7664141d2e683cf95`;
  previous healthy2.13.0 `sha256:3e4b32b1574253c3f0ba6acb412d0de070f13b2395a660ceed88d46c6c45fb5d`.
  Package/OCI revision and all27 installed source hashes match. An early hash probe
  ran during replacement and was repeated after transaction completion; the final
  source check passes. No released behavior regression or rollback required.
- Installed writer3/3 synthetic domains; actual owner Discord8/8 scenarios, seven
  answers and one abstention. Three changed cases use isolated invented graph,
  released handler and authenticated real sends; four normal gateway answers cover
  supported recall, natural history, invited fiction and care. No second gateway,
  learning from tests, source scope expansion, raw answer artifact or league post.
  Primary heartbeat is verified after client close and fixture cleanup.
- At08:27:06UTC: healthy, zero restarts/errors/response failures/disconnects/memory,
  learning/study/generation pauses; four normal gateway replies, one decline,
  eight learning batches and zero study completions since08:19:28UTC. The three
  controlled real sends are counted separately from the gateway logs.
- Source/graph counts unchanged:34 native;16 archives/4299 blocks/405 eligible;
  115 visual episodes/96 assets;439 graph sources/554 episodes/1011 edges,
  one claim/one preference/zero abstractions. No real human observation populated.
- Tracked October estimateUSD0.099331455 (runtime0.047684835,
  maintenance0.05164662),491 settled/zero unsettled. Run delta0.004857205;
  twelve synthetic research calls0.001875455. Existing USD18/2/20 caps preserved;
  no new recurring call or paid infrastructure. Billing/pre-guard spend unknown.
- Private helpers, invented provider results and content-free real references are
  `/var/lib/trubot/smoke-tests/2026-10-11-0100`,0700/0600, existing seven-day manual
  retention/withdrawal cleanup. Disposable invented databases and host staging
  removed. Public [release evidence](evaluations/2026-10-11-behavioral-memory-release.json)
  contains no raw exchanges or personal observations. Owned local staging will be
  removed after final evidence merge; earlier private payload/worktrees untouched.
- Research/planning conclusion: H26 representation/lifecycle is delivered; provider
  spontaneous new-domain learning is not demonstrated. Post-audit seven answers
  shows reused achievement/care language and a prior joke frame. Sparse current
  league activity, structural human sample and absent independent semantic/pixel
  review prevent a fidelity/humor claim. Keep validated H21 human population first,
  then H22 variation, native/visual coverage, tools/skills and generated outdoor scenes.


## 2026-10-11 05:00 - bounded historical episode packets

Fresh fetched base `fbfd118bda9d6e4702f30c13bee75569e9c81e77`, managed worktree
`trubot-daily-20261011-0500`, unique feature branch. Primary checkout and older
worktrees untouched. No unfinished evolution PR. Both planning phases selected
H27 after reproducing missing setup/reaction and oversized request packets.
Baseline 5/5 new cases fail, candidate 5/5 pass. Five matched synthetic provider
calls produce one accepted qualified claim, zero abstract patterns; both attribution
controls abstain. Coverage conformance is supported, semantic fidelity unresolved.
Twelve-block/four-export count-only audit covers 69 neighbors with 19 old whole
neighbors and 65 candidate-size-eligible neighbors. No human semantic/pixel study
or real abstraction population. Full release/Discord evidence follows deployment.


### Verified H27 rollout, 2026-10-11T12:30:13.570119+00:00

- PR [#70](https://github.com/jdegregorio/wcb-discord-bot/pull/70), tested
  `c1802f207cdef9848b70d0573b51a229755ac8e7`, merged
  `876c16ce3c1e679252cdbcd9a6b25307cdf50eb0` with an identical tree.
  PR CI38138503764/main CI38138602610/image publish38138683510 pass.
  All six gates before/after merge:647 tests,96.76% branch-inclusive coverage,
  27 typed modules,2.15.0 wheel/sdist; dependency versions unchanged.
- Immutable [v2.15.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.15.0)
  published both architectures. Reverified pi5/aarch64/Ubuntu24.04.4, helper,
  manifest and secret permissions. Release timer deploys through the existing
  transaction before the explicit app-scoped deploy command, which confirms it.
- Digest `sha256:212d290fad5c46cf6984c9dbd6b52f6897eda2bc4b00b903c1de6dd7f0611717`;
  previous2.14.0 `sha256:759c6a15419811a5c2a52e164d65fced57b6b2c1602f51a7664141d2e683cf95`.
  Package/OCI revision and all27 installed source hashes match. Readiness healthy,
  zero restarts/errors/response failures/disconnects/memory/learning/study pauses.
  Six gateway posts,one decline,eight learning batches,zero study completions
  since12:19:58UTC. Controlled sends are counted separately.
- Installed writer preserves full synthetic episodes; two actual owner handler
  scenarios pass. Normal gateway6/7, overall8/9 actual scenarios/eight answers.
  Broad historical first reply misassigns the source subject; exact repeat passes.
  This is an unresolved H6 fidelity defect in an unchanged ordinary reply path,
  not demonstrated H27 regression. No rollback required for this context increment.
  Preserve failed acceptance; no full recall/fidelity claim. Exact-date uncertainty,
  baseball, fiction, care and recipient abstention pass. Main heartbeat remains
  healthy after every separate validation client closes.
- Production source counts unchanged:34 native,16 exports/4299 blocks/405 eligible,
  115 visual episodes/96 assets,439 graph sources/554 episodes/1011 edges,
  one claim/one preference/zero abstractions. No human pattern populated.
- Tracked OctoberUSD0.10355339(runtime0.05015061,maintenance0.05340278),505 settled,
  zero unsettled. Run delta0.004221935;five research calls0.001026135. Existing
  USD18/2/20 caps, no added service or recurring request. Provider billing and
  pre-guard October spend remain unknown.
- Private content-free references/synthetic helpers and results are under
  `/var/lib/trubot/smoke-tests/2026-10-11-0500`,0700/0600, seven-day manual retention
  and withdrawal cleanup. Invented stores are removed; owned staging is cleaned before
  archiving. Public [release evidence](evaluations/2026-10-11-context-packets-release.json)
  records actual failure and coverage limits. Primary checkout was never changed.
  A prior count-only audit helper was rerun once and overwrote its same prior
  before-count report; all other older evidence and pending private work are intact.
- Roadmap: H27 enabling correction delivered; semantic human abstraction quality,
  H6 subject qualification,H28 classification,H22 variation remain unresolved.
  Keep broader native/visual evidence,selective skills/tools and generated outdoor
  scenes. Six-run schedule,model/reasoning/notifications and privacy unchanged.

Final error audit distinguishes two optional voice-dependency startup warnings
from application errors: zero other warnings, zero response/memory/learning/study
failures, healthy readiness and zero restarts. Private final metadata preserves
8/9 actual outcomes; disposable invented stores are removed. Evidence PR
[#71](https://github.com/jdegregorio/wcb-discord-bot/pull/71) changes documentation
only, preserving the tested released source/tests/version/lock.


## 2026-10-11 09:00 - author-scoped personal recall

New managed worktree trubot-daily-20261011-0900, fetched base
ff0e31a33763cbbeb4628d791f53ebe92d443b55; unique feature branch.
Primary checkout, earlier worktrees and private pending study untouched.
Both planning phases select H31 after actual owner requester recall reproduces
cross-person memory attribution. H29 identity framing and H30 low reasoning
fail contrary controls and are rejected, with all experiments retained privately.
No runtime source from those prototypes ships.

The selected change blocks character-source/graph/voice retrieval for another
speaker's explicit own-past question, preserves live human context, and admits
Andrew's own verified identity. Scope follows reaction target author, not reactor.
Current authoritative withdrawal and guild/operator checks remain first.
No model, reasoning, token ceiling, prompt contract, study pacing, schema,
population, participation or infrastructure change. Version 2.15.1 candidate.
Thirty-two new source-routing, identity, handler, permission, quote/hypothetical
and withdrawal regressions pass. All six local gates pass: 679 tests, 96.77%
coverage, 75 formatted files, 27 typed source modules and both package artifacts.
Matched invented-source comparison: baseline 4/10, candidate 10/10; six unsupported
ownership answers corrected, live-human and bot-history controls retained.
This supports the narrow source boundary, not a human-fidelity or humor claim.
Release and actual post-deployment acceptance follow.

Shipped runtime PR[#72](https://github.com/jdegregorio/wcb-discord-bot/pull/72),
branch 8f10127b6df723f778e749f54ae3cdabf005b99a, merged/retested main
bc44670d88efbefe9e7ba1ddcac91778684ef46c. Immutable
[v2.15.1](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.15.1);
PR/main Quality and container publication all succeed. Verified amd64/arm64
manifests before the existing locked release transaction. Running index digest
sha256:d10b78616f2a4fe466f6e53280e8bd763e5c543c2e78e9ec8c7ab25c3fe3c030,
OCI revision/package match and 27 installed source hashes match. Previous 2.15.0
digest 212d290fad5c46cf6984c9dbd6b52f6897eda2bc4b00b903c1de6dd7f0611717
remains rollback target. Readiness healthy after HTTP-only clients close,
zero restarts/errors/response-learning-study failures, two optional voice warnings.

Actual owner-authored gateway smoke in authenticated two-member allowlisted
private general: 8/9 scenarios pass, 8 actual answers, one correct abstention.
Changed acceptance 3/3: original own-past question, unprefixed follow-up paraphrase
and actual human words preserved. Broad-history control still misassigns the
source person, as baseline did; its routing is unchanged. Preserve that failure,
do not claim complete historical recall or a clean overall character pass.
Baseball, exact timing, invited fiction, care and recipient silence pass.
Care repetition and familiar humor mechanism remain quality candidates; no
measured human fidelity or numeric funniness gain. No fresh spontaneous current
release league sample; counts remain 7 target/17 peer/5 older bot across 3 channels.

Production corpus unchanged: 34 native, 16 exports/4299 grouped blocks/405 eligible,
115 visuals/96 assets, 439 graph sources/554 episodes/1011 edges, one claim/one
preference/zero abstractions. No development message enters human evidence.
Final October tracked USD 0.128031055 (runtime 0.05352596, maintenance 0.074505095),
912 settled attempts/zero unsettled. Run USD 0.024477665, research USD 0.021102315.
Same USD 18/2/20 caps; provider billing and pre-guard spending remain unknown.
Private content-free message/source references and invented-source studies stay
under `/var/lib/trubot/smoke-tests/2026-10-11-0900`, 0700/0600, seven-day manual
retention and withdrawal cleanup. No raw personal excerpts/answer text persisted.
Own staging is cleaned before this run's worktree is archived; primary checkout
and earlier worktrees remain untouched. Public
[release evidence](evaluations/2026-10-11-author-scope-release.json) records
actual pass/fail and coverage. H29/H30 rejected; H31 narrow correction supported.
Next: validated H21/H28 abstract learning with subject checks, H22 variation,
native/visual coverage, selective skills/tools and generated outdoor scenes.

Evidence PR [#73](https://github.com/jdegregorio/wcb-discord-bot/pull/73) preserves
the release result and roadmap. It changes documentation only; source, tests,
version and lock match the tested immutable release.


## 2026-10-11 13:00 - complete reviewed episode workflow (candidate)

Fetched base fe4a7bd97979a26ee2c534d4dee74338c2325c61, new managed worktree
trubot-daily-20261011-1300, branch feature/trubot-daily-20261011-1300. Primary
checkout and prior worktrees untouched. Previous evolution #72/#73 is finished;
separate humor draft #74 remains independent and is not merged by this run.
Both planning phases select H32, with H33 automatic sampling exploratory and H21/H28
human population still dependent on private semantic and held-out validation.

2.16.0 adds complete trusted episode refs and a usable plain-HTTP maintenance
command. It preserves selected support and contrary cases across lexical differences,
or stops without paid extraction. Source scope, freshness, retirement, withdrawal,
request bounds, shared four-hour pacing and maintenance ledger remain enforced.
Automatic default sampling and ordinary reply/persona/participation paths are unchanged.
A per-cycle receipt prevents confusing another process's checkpoint with completion.

Candidate validation: all six gates, 721 tests, 96.76% branch-inclusive coverage,
28 typed modules; dependency versions unchanged. Forty-two new regressions cover
source selection/lifecycle and operator execution. Direct baseline lexical control
omits a nonlexical exception; supplied-output two-pass writer stores two supports
and one contrary link and deletion removes recall. This is enabling conformance.
Same-model comparison, three invented cases/two repetitions/two arms: 17 requests,
USD 0.002570545. Baseline accepts a pattern in 1/2, complete arm abstains in 2/2;
quoted-peer negatives abstain and specific self-report controls pass in both arms.
No private human extraction or broad quality improvement claimed; all trials retained.

Audit: authenticated two-member private guild verified. Three league channels,
latest 100/14 days: seven target, seventeen peers, five older bot, zero replies from
current release. Structural archive sample: twelve target blocks/one export,
twenty-three neighbors/one media gap, no new semantic human or pixel review.
Actual development UI exposes flat invited-banter wording and historical ownership
variability; separate active humor work owns that correction. Raw semantic study
output was rejected by automatic approval review for private exchanges entering
command logs. Safe count-only audit completed; older pending payload remains unused.
Initial tracked October USD 0.130031605, zero unsettled; caps USD 18/2/20 unchanged.
Provider billing and pre-guard October spend remain unknown.

Release, immutable digest, installed command/handler acceptance, actual owner gateway
responses, final health/cost and CI identifiers remain pending at this candidate record.


### 13:00 installed acceptance correction

v2.16.0 was built by container workflow 38172062179 for merged commit
9019bd61db1eff2c3e5bff88ea544a61f7aeeddb and deployed at 20:27 UTC. The installed
plain-HTTP command then failed before selection: the existing reply allowlist
contains the private development channel in addition to league source channels.
The command incorrectly rejected that unrelated channel. This was reproduced
through the installed console entrypoint; fixtures missed the actual arrangement.
The complete two-pass synthetic writer and actual controlled Discord send passed,
but those checks did not establish command acceptance.

The app transaction rolled back to healthy 2.15.1, digest
sha256:d10b78616f2a4fe466f6e53280e8bd763e5c543c2e78e9ec8c7ab25c3fe3c030,
zero restarts. v2.16.0 is excluded from stable discovery as a prerelease; its tag,
commit and image are retained. 2.16.1 skips unrelated/non-text configured channels
without caching them as source context. Denied HTTP reads still fail closed.
Three regressions cover the development-guild channel, a non-text channel, and a
denied source read. All six gates pass: 724 tests, 96.81% coverage, 28 typed modules.
Corrected release and installed/real Discord acceptance remain pending.


### 13:00 final release result - 2.16.1

Runtime PR [#75](https://github.com/jdegregorio/wcb-discord-bot/pull/75) merged
9019bd61db1eff2c3e5bff88ea544a61f7aeeddb. Correction PR
[#76](https://github.com/jdegregorio/wcb-discord-bot/pull/76) merged
eecefb4ef0cd13ef81c68c21a0b210d2ddc2de3e, identical tested runtime tree 4f0bd7f.
Required CI 38171771447/38171908551 for the first release and
38172872640/38172957602 for the correction pass. Image workflows
38172062179/38173072737 pass with linux/amd64 and arm64. All six local gates
pass before/after each runtime merge; final 724 tests, 45 new regressions,
96.81% branch-inclusive coverage and 28 typed modules. Dependency versions unchanged.

New immutable [v2.16.1](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.16.1)
runs on reverified pi5/aarch64/Ubuntu 24.04.4 through the locked app transaction,
digest sha256:ebc387f4e733d728a74b218d2f24202ddab4b6deee1c5edfd24a40218f717532,
started 2026-10-11T20:41:31Z. OCI revision/package/all 28 source hashes match.
Readiness remains healthy after every HTTP/validation client closes. Zero restarts,
response errors, learning/study pauses or other warnings; two existing optional
voice warnings. Previous healthy 2.15.1 remains the transaction rollback target.
The failed 2.16.0 tag/image and installed failure evidence remain intact; prerelease
status keeps it out of stable discovery. No tag reused or branch protection bypassed.

Installed command: invalid/paced selection stops without a provider charge;
authenticated plain-HTTP completion with three invented source episodes finishes
and reports rejection honestly. Cost USD 0.00030125 on the existing maintenance
ledger. No gateway/send/heartbeat ownership or production learning mutation.
Installed deterministic writer preserves two supports/one nonlexical sincere
exception across both passes. Lifecycle/deletion controls pass in regression tests.

Actual owner private Discord, final release: 8/10 trials, eight answers.
Three controlled handler trials: playful and clear sincere invitation pass; an
initial sincere follow-up abstains and remains a negative trial. The clearer
invitation verifiably receives abstract memory plus its limitation; the answer
reuses the supplied invented sincere wording. Seven normal gateway controls: 6/7,
six answers and intended recipient silence. Baseball, requester history, exact
timing, invited fiction and care pass. Broad historical memory still assigns the
character's source to the owner, matching baseline. Humor and care repeat earlier
mechanisms/phrasing. Do not claim full historical recall, better humor, independent
naturalness or populated human abstractions. No league test chatter or bot/test
learning evidence, and no separate validation gateway. Primary heartbeat preserved.

Post-audit stays sparse: three league channels/latest 100/14 days contain seven
target, seventeen peers, five older bot and zero spontaneous current-release
replies. Twelve historical target blocks/one export/twenty-three neighbors/one
media gap are structural only. Semantic human/pixel study remains unvalidated
after the automatic approval rejection of private exchanges entering command logs.
No new trait is promoted; older private pending payload stays unused.

Production state unchanged: 34 native messages; 16 exports/4299 blocks/412 target/
405 eligible; 115 visual episodes/96 assets; 439 graph sources/554 episodes/1011
edges, one claim/one preference/zero abstract patterns. Private content-free refs,
all synthetic trials and failed-release metadata remain app-owned in this run's
private smoke directory, 0700/0600, seven-day manual retention and withdrawal cleanup.
Disposable synthetic/CLI stores removed. No raw human/source/answer artifacts.

Final tracked October USD 0.13635065: runtime 0.058021535, maintenance 0.078329115;
945 settled/zero unsettled. Run USD 0.006319045 across 29 ledger attempts,
including 17-request research USD 0.002570545. Existing caps USD 18/2/20 preserved;
no added paid service or automatic request cadence. Billing/pre-guard spend unknown.
Public [release evidence](evaluations/2026-10-11-episode-selection-release.json)
records methods, failures, costs and scope. H32 enabling hypothesis supported;
H33 automatic diversity exploratory; H21/H28 human quality unresolved. Next:
validated abstract population with ownership/sincere and independent held-out
controls, separate H22 humor work, native/visual coverage, selective skills/tools
and generated outdoor scenes. Schedule/model/reasoning/notifications unchanged.

## 2026-10-11 17:00 - release the reconciled comic repair

Initial base 8769e75; network-reverified base 867896a includes already-merged #74.
Fresh managed worktree and feature/trubot-daily-20261011-1700, primary unchanged.
Both planning phases select H34 completion instead of overlapping #74 or adding
unmeasured schema. Five attributed archive windows/five exports/20 neighbors are
privately inspected with current source refs; five older league bot windows are
reviewed, no fresh spontaneous current-release replies. Three league channels,
latest 100/14 days: seven target, 17 peers, five older bot. No new human abstraction.
Private provider holdout rejected before execution; no retry or quality claim.

Fresh 48-request synthetic comparison uses the existing maintenance ledger, same
model/handler/settings and every retained sample. Comic turns improve 7/12 to
11/12 by agent rubric review; all clear controls pass 10/10 per arm. An ambiguous
literal-language case fails expected idiom 2/2 baseline and 1/2 candidate; its
clarified follow-up passes both 2/2. Preserve failures, repeated metaphor and
subjective-grading limits. This does not measure two-to-three-fold humor or overall
human fidelity. Real baseline owner gateway reproduces declined follow-up,
uncertain direct answer and flat TJ acknowledgment. Source attribution remains
an explicit release control. Results: evaluations/2026-10-11-humor-release-study.md
and 2026-10-11-humor-release/. Maintenance delta USD 0.003033155, no unsettled
attempts; ledger limits 18/2/20 and participation unchanged. Earlier #74 local
research cost USD 0.01433521 was outside this app ledger; total provider billing
and pre-guard spending remain unverified.

Version 2.17.0 publishes the reconciled runtime change; all six local gates pass,
724 tests and 96.81% branch-inclusive coverage. PR/main CI, immutable images,
installed source hashes, actual candidate Discord and deployment remain pending.
Next: validated H35 abstract population, humor variation, native/visual episodes,
selective tools/skills and guarded generated outdoor scenes.


## 2026-10-11 21:00 - bounded stale reply recovery, release pending

Base 597bfccd88136bd4993b07686fef9ad85c3cf5f2; new managed worktree
trubot-daily-20261011-2100 and feature/trubot-daily-20261011-2100.
Primary checkout/earlier worktrees untouched. Previous failed 2.17.0 remains
prerelease, production is healthy 2.16.1. Unfinished H38 repair reconciled here;
prior uncommitted draft is preserved. No role relabeling, new trait or schema.
Both phases, human/bot audit coverage, preregistered criteria and limits are in
[evaluations/2026-10-11-repetition-study.md](evaluations/2026-10-11-repetition-study.md).

All six local gates: 752 tests, 96.84% coverage, 28 typed modules, 2.17.1 packages.
Four pre-fix synthetic failures become 28 passing conformance cases. Eight
forced-old-draft candidate provider trials pass semantic review; four matched
recipient/literal handler controls pass in each arm. Sixteen total paid research
calls use the existing maintenance ledger. No human-provider export or general
humor/fidelity claim. Actual baseline two replies reproduce flat comic behavior;
changed installed/real Discord candidate checks remain pending release.

Public release identifiers, digest, health, costs, all actual acceptance outcomes
and limitations will be recorded after rollout. No completion is claimed here.

## Source-lifecycle correction before deployment

The first correction release, 2.17.1, was published but excluded from stable
discovery before deployment. Review found that an optional refresh could resend
an attached private memory packet after its sources changed. Four new adapter
regressions fail on that candidate. Version 2.17.2 adds handler revalidation using
the original conversation, preserving exact source scope and packet equality.
An unchecked, changed, deleted, withdrawn or unavailable packet receives no extra
reservation or request. The already generated draft is retained; cancellation
propagates. Synthetic actual-store handler tests cover edit/deletion/withdrawal
between first generation and recovery, unchanged-source allowance and denied
source refresh. No real withdrawal or production source mutation is invoked.
Prior eight recovery/provider trials remain conditional recovery evidence; the
new private-source gate is validated separately with deterministic lifecycle tests.
Production stayed on healthy2.16.1 throughout; immutable2.17.0/2.17.1 tags remain
prereleases, not overwritten. Final six gates and installed/actual acceptance follow.

## Final release and actual acceptance, 2026-10-12 UTC

PR #79 merged ccf8bcd; PR/main CI 38202644136/38202772735 pass. Its 2.17.1
candidate was excluded before deployment for the source-check defect. PR #80
merged e404c2019b5abf323b056adc6a8681c284ebb837, identical to tested 50023ad
and tree 9426b33c652872fc355b996dbd6c8edbb1fc7ae8. Required CI
38203365997/38203475839 and final images 38203597857 pass. All six gates pass
before/after merge: 762 tests, 96.83% branch-inclusive coverage, 28 typed modules,
2.17.2 wheel/sdist; dependency versions unchanged. New regressions total 38.

Immutable [v2.17.2](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.17.2)
runs through pi-app on reverified pi5/aarch64/Ubuntu 24.04.4, digest
sha256:a78b82141d17bf07d43d828297ce02fde267e80a1aabf84d35ef84bd7356c7d2.
Previous healthy 2.16.1 digest ebc387f4e733d728a74b218d2f24202ddab4b6deee1c5edfd24a40218f717532
is retained. Both architectures, package/OCI revision and 28 source hashes match.
At 04:38:40 UTC, 707 seconds after start: healthy readiness, zero restarts/errors,
response failures/disconnects/learning/study/memory/optional-refresh warnings;
two optional voice startup warnings only, eight gateway posts and one decline.
No final rollback. An early health read caught the old container during deployment;
its version assertion failed and was rerun after transaction completion.

Actual private owner tests: one controlled released-handler recovery passes with
one paid call and a real post; nine normal gateway scenarios yield seven passes,
eight answers and one intentional recipient abstention. Combined 8/10. Supported
preference, sincere care, explicit timing uncertainty, operator-history boundary,
comic setup and fresh fictional league premise pass. The TJ follow-up is distinct
but merely a weak acknowledgment, so the strict comic-turn criterion remains
failed. Broad historical recall still misassigns Andrew's source words to the
operator, matching the documented previous defect. No routine date disclaimer
on ordinary recall; familiar care wording remains a variation gap. Retain both
negatives, do not claim clean full acceptance or a general humor multiplier.
The selected exact-repeat recovery/source-lifecycle safeguard is operational;
its broader quality hypothesis is only partially supported. No newly demonstrated
material regression requires final rollback. Future work must satisfy open criteria.

After deployment, an additional attributed central block/four neighbors in an
already studied export verifies supported historical content locally. This is
post-hoc source verification, not a held-out quality comparison. Total local
review: six central blocks, five exports, 24 neighbors plus one separately noted
target-authored neighbor. No source date inferred, pixel-dependent interpretation,
private human provider payload, new trait or abstraction. Bounded before/after
league counts remain sparse: three channels, latest 100/14 days, seven target,
17 peer, five older bot, zero fresh spontaneous current-release activity.

Continuity unchanged: 34 native records; 16 exports/4,299 grouped blocks/405
eligible blocks; 115 visual episodes/96 assets; 439 graph sources, 554 episodes,
1,011 edges, one claim/one preference/zero abstract patterns. No real withdrawal,
second gateway, user-token extraction, league test post or development learning.
Separate readiness is set before validation-client construction and the primary
heartbeat is healthy after closure. Private app-volume artifacts retain content-free
actual test references and flags, synthetic studies and public-code helpers only,
0700/0600, existing seven-day manual retention/withdrawal. Actual answer text and
raw human renderings are not retained; local private PNGs were deleted after review.

Final October ledger estimate USD 0.1508092: runtime 0.06570523, maintenance
0.08510397, 1,060 settled/zero unsettled. Run USD 0.00577221 over 28 attempts:
runtime 0.00380216 and maintenance 0.00197005. Sixteen paid research calls plus
one controlled maintenance recovery; real gateway baseline/acceptance uses runtime.
No fresh ledger, paid service or cap change. USD 18/2/20 remains enforced; provider
billing and pre-guard spend are unknown. Six daily standalone times, Sol/xhigh,
notification setting and source/privacy/participation rules remain unchanged.

[Release evidence](evaluations/2026-10-11-repetition-release.json) preserves method,
counts, negative cases, timing, hashes and identifiers. Next: validated human
abstractions with person/care controls, creative variation/weak follow-ups, broader
native/visual context, selective skills/tools and generated outdoor scenes. No
further unmeasured schema categories or repeated literal/date-only patch priority.

## 2026-10-12 01:00 Pacific - atomic reviewed episode rollout

Fresh managed worktree `trubot-daily-20261012-0100`, base
`1dd71dbe617be35c452af0ab84364e65f5528872`. Primary checkout/earlier drafts
untouched, prior repair reconciled; no overlapping evolution PR. Both planning
phases select H40/H41: one atomic reviewed import plus abstraction-first ordinary
presentation, preserving internal dates and explicit source requests. Actual CLI
reproduction: rejected two-item batch leaves one observation before, zero after.
Current private source checks and disposable clone acceptance pass; one tentative
abstraction remains proposed until real release/Discord validation. No raw/derived
personal content in Git; source reviewer and reply reviewer are Codex, not an
independent human. Thirteen central archive windows, nine distinct exports, 51
neighbors (five windows revisit prior studies); five older actual league bot windows
reviewed separately. Eight deterministic windows are new to this run's review, not
proven unseen across all past studies. Missing media/dates remain explicit internally.
No new historical pixels, source scope, model, study pacing/cohort, budget or service.

All six local gates pass: 781 tests, 96.84% branch-inclusive coverage, 28 typed modules,
2.18.0 wheel/sdist, no dependency version changes. Nineteen new regressions cover
atomic replacements/conflicts/backups/withdrawal and conditional/timing versus explicit
quotation paths. The first clone failure identified an ordinary-question raw-punchline
path and was corrected before population. Current production remains healthy 2.17.2,
immutable digest a78b82141d17bf07d43d828297ce02fde267e80a1aabf84d35ef84bd7356c7d2.
Initial October estimate USD0.1508092, zero unsettled; all research so far is offline,
actual gateway baselines use the existing runtime ledger. Release and actual candidate
acceptance are pending; do not treat proposed population as deployed.


### Verified release outcome, 2026-10-12 01:00 Pacific

Runtime PR #82 merged `c86ec65ab12c2dd3b68bbc70ec6c22e56017e6a8`, tree `d65e78fc63c557a464acbc4cb5c8e1fe32540a4a`,
identical to tested bdcf45b. PR CI 38223156007 and merged-main CI 38223490205 pass;
38223111670 is the superseded cancelled PR run. All six merged local gates pass:
781 tests/96.84% coverage, 28 typed modules, 2.18.0 wheel/sdist. Immutable
[v2.18.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.18.0) images
38223665070 succeed for AMD64/ARM64 before the locked pi-app transaction. Reverified
pi5/aarch64/Ubuntu24.04; running digest `sha256:f7f8612ae2ed84de7730d050e35f23c9b050c75fad86c80ad977d67d81cf38bb`, previous
healthy 2.17.2 `sha256:a78b82141d17bf07d43d828297ce02fde267e80a1aabf84d35ef84bd7356c7d2` retained. Package, OCI revision
and all 28 installed source hashes match. Readiness healthy, zero restarts and no
new errors/reply failures/disconnects/memory/learning/study pauses; two optional voice
startup warnings. Primary readiness verified after all plain HTTP validation clients;
no second app gateway/client, token extraction, league test post or development learning.

Installed actual CLI rejection/commit/synthetic withdrawal acceptance is 3/3. One
private local-Codex reviewed conditional abstraction was imported atomically (three
supports, two applicability controls, five exports, unknown dates, 30-day expiry).
It is RETIRED after actual prototype acceptance is 1/3: novel fictional banter passes,
source-example reuse and mechanical qualification fail. Both ephemeral manifests are
erased. Curated retirement does not add automatic extraction vetoes; zero automatic
vetoes remain. No active human abstraction, independent human validation or general
fidelity/humor improvement is claimed. Source/ledger stores are never replaced.

Actual normal gateway controls after retirement: 8/9, eight answers and recipient
silence. Care, supported enthusiasm/preference, exact-date honesty, operator own-history
boundary and clarified fictional TJ direct/unmentioned follow-up pass. Broad historical
source-person confusion fails as before; it remains an explicit grounding prerequisite.
Combined candidate 9/12 (11 answers/one silence), baseline 1/2. The old unclarified
TJ weakness remains unresolved despite this clarified trial's comic turn. Data rollback
is retirement of the failed prototype; no new material runtime/source regression calls
for image rollback. Do not claim clean full recall, natural-memory or comic acceptance.

Human contextual review totals 16 central blocks/12 exports/63 neighbors, including
three held-out non-support windows (one compatible mechanism/two practical controls),
five targeted revisits and eight new deterministic windows. No independent human judge
or original historical image interpretation. Before/after league audit: three channels,
latest100/14days, seven target/17peer/five oldbot/zero fresh spontaneous. Five older
bot windows reveal a contextual enthusiasm mismatch with a peer reaction; current
enthusiasm passes, so a new mood policy is not justified by that old evidence alone.

Private continuity returns to 34 native/16 documents/4,299 grouped blocks/405 eligible,
115 visual episodes/96 assets, 439 graph sources/554 episodes/1,011 edges, one claim/
one preference/zero abstractions. Real withdrawal untouched. Content-free test refs,
source refs/count summaries and public-code helpers are retained privately (0700/0600,
seven-day manual retention/withdrawal cleanup). No actual answer/source text artifacts.

Tracked October estimate USD 0.156075430 (runtime 0.070971460,
maintenance 0.085103970), 1074 settled/zero unsettled. Run delta
USD 0.005266230 over 14 runtime
attempts; zero provider research calls and maintenance spend unchanged. Existing18/2/20
caps, no new paid service/request schedule. Provider billing and pre-guard spend remain
unknown. Evidence JSON preserves all pass/fail categories and identifiers. Next H44
natural selective abstraction use before more H21/H28 traits, then variation and
native/visual/tools/generated scenes. Evidence PR/final main and owned cleanup follow.

## 2026-10-12 05:00 - selective source examples (pre-release)

Base dd77ec2260b34211d8604ef5666439e16419078d, new managed worktree and branch.
H45 corrects unconditional and answer-only raw voice admission. Both planning
phases and locked acceptance are in evaluations/2026-10-12-selective-voice-study.md.
Nine baseline failures become passes; full handler/source controls are required.
Matched 16-request invented-source comparison: semantic 7/8 baseline, 8/8 candidate,
no off-topic source reuse in six candidate negatives versus one in six baseline.
Actual isolated owner-message baseline admits irrelevant voice data; candidate and
normal gateway acceptance remain pending. No new human trait or general quality claim.
Research USD0.000734410 through existing maintenance allowance; no added recurring
request, model, service, study pacing, source intake or participation change.

### 05:00 final runtime rollout and measured outcome

Runtime [PR #84](https://github.com/jdegregorio/wcb-discord-bot/pull/84) merged as
ff33a75217b84fdbbee596528ea208d699ccc2d4, identical to tested 7fdd1f7 tree.
PR CI 38248021258 and main CI 38248261704 pass. All six merged local gates pass:
794 tests, 96.84% coverage, 28 typed modules, 13 new regressions. Dependency versions
unchanged. Immutable [v2.18.1](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.18.1)
and both architectures in publish 38248458292 pass before the locked deployment.

Reverified pi5/aarch64/Ubuntu 24.04.4. Running immutable digest
sha256:d7b4eb32644826dd49dd5e23a3295fb0a5c1e478516f11154bc51a162abbca9d,
OCI/package and 28 source hashes match. Previous 2.18.0/f7f8612a digest is retained
in the existing transaction. At 12:40:38Z: healthy, zero restarts/errors/response
failures/disconnects/memory/learning/study pauses, two optional voice warnings and
zero other warnings, ten gateway posts/one decline/16 learning batches. No rollback.

Actual changed admission 2/2; both disposable correction/withdrawal controls pass,
zero test intake and live heartbeat verified after client close. Controlled behavioral
1/2: eligible example copied verbatim. Normal gateway 9/11: historical source-person
confusion persists, appropriate enthusiasm exceeds two sentences. Combined 10/13;
negative results retained. Clarified TJ pair passes narrowly, familiar mechanism not
novelty; unclarified prior failure remains unvalidated. Eleven ordinary refs and three
controlled refs are authenticated privately. Source/graph counts unchanged, zero
human abstractions, prior failed pattern remains retired. No general fidelity gain.

Research study eight attributed central blocks/eight exports/32 neighbors/two missing
media windows, none truncated, five older bot windows and zero spontaneous current
league activity. Same Codex evaluator, no independent human review or original pixels.
Matched invented comparison 7/8 to 8/8, one off-topic source reuse removed in the tiny
sample. Full methods and limits are in selective-voice-study.md and release.json.

Tracked October USD0.161571360 (runtime0.075279115/maintenance0.086292245), 1,106
settled/zero unsettled. Run USD0.005495930 across 32 attempts; maintenance delta
USD0.001188275, 16 research calls USD0.000734410. Existing USD18/2/20 caps, no added
recurring request/service. Provider billing and pre-guard spending remain unknown.

Private evidence on existing app volume, 0700/0600, manual seven-day retention and
withdrawal cleanup. Only content-free refs/counts/metrics, invented fixtures and
public helpers persist. Raw human/reply renderings erased. The UI optimistic-ID and
old log-label helper issues were corrected without product mutation. An unsafe env-file
read was rejected; safer metadata completed rollout, no blocker. Joe's checkout and
older worktrees untouched. Evidence [PR #85](https://github.com/jdegregorio/wcb-discord-bot/pull/85) carries
these final measured results. Runtime source/tests/version/lock are unchanged from
ff33a752. Final main CI and owned-worktree archive status are preserved in automation
memory after this evidence merge.

## 2026-10-12 09:00 - abstract memory projection

Base 0241bf7da03a610adf72dc404b2f0dba5a6f2a9b; new managed worktree and unique
feature branch. Prior run complete; primary/older drafts untouched. Both planning
phases, locked hypotheses, private source counts and negatives are in
[evaluation study](evaluations/2026-10-12-abstract-projection-study.md). H47 is a
purpose-specific typed renderer and handler admission correction. H48 human
population remains unvalidated; zero active abstractions and retired prototype.

Actual baseline packet exposes competing voice and reproduces source reuse.
Matched synthetic semantic results 6/12 to 10/12; exact ordinary/timing source-line
reuse 4/8 to 0/8. Evidence source-person and brevity negatives remain. All six local
gates pass, 799 tests, 96.85% coverage. Release/deployment/actual acceptance pending.

### 09:00 completed rollout and actual acceptance

Runtime [PR #86](https://github.com/jdegregorio/wcb-discord-bot/pull/86) merged
c396a04c527131f5c95a11a29554481d773bac98, identical tested tree. PR CI 38275962652
and main CI 38276152620 passed. Immutable [v2.19.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.19.0)
built both architectures in 38276302195. Reverified pi5/aarch64/Ubuntu 24.04.4;
locked pi-app transaction deployed digest sha256:541d19cea9d3f41a3828dfecfdf90388ff9f372e45d1364a0eb9e0815627a0a6. Package/OCI/28 source
hashes match and readiness is healthy. Prior healthy 2.18.1/d7b4eb32 retained.
At 2026-10-12T16:29:51.035183+00:00: zero errors, failures, disconnects, restarts or source/study
pauses; two optional voice warnings, zero other warnings, ten gateway posts, one
decline and eight learning batches. No rollback. An early installed check ran
before the transaction finished, saw the old version, and failed; the completed
installed verification passes. Merge SHA and emoji UI locator mistakes were
corrected through verified references without bypass or duplicate messages.

Installed changed packet/lifecycle acceptance 3/3; controlled behavior 2/3 due
evidence brevity. Normal actual gateway 9/11, combined 11/14: existing source-person
confusion and enthusiasm brevity remain failed. Supported preference, exact-date restraint, owner scope, care, novel banter, clarified TJ
pair and other-recipient abstention otherwise pass. Every normal owner/bot reference
reauthenticated privately; isolated source fixture clients verify membership,
owner, allowlist and sends. Zero development intake, no second gateway; separate
readiness set before construction and primary heartbeat healthy after close.
No raw source, answer text or derived human observations in public artifacts.

Audit: three channels / latest 100 messages / 14 days, seven target, 15 peers, five older bot
windows, zero current spontaneous replies. Eight target central grouped blocks,
eight exports, 32 neighbors and no marked media gaps. Actual text renderings read;
original image pixels not interpreted. Same Codex evaluator, no genuine human
population held-out benchmark or independent review. No new human trait, active
abstraction or general fidelity/humor gain. Native 34, archive 16 / 4,299 blocks, visual
115 episodes / 96 assets unchanged. Automatic pre-rollout studies added one claim since prior
run: graph 439 sources / 554 episodes / 1,015 edges, two claims/one preference/zero patterns.
The old failed pattern remains retired. Human abstractions remain the next priority.

Tracked October estimate USD0.168895595, runtime0.079035765
and maintenance0.089859830; 1149 settled/zero unsettled.
Run delta USD0.007324235 over 43 attempts: runtime
0.003756650/maintenance0.003567585. Includes
24 research requests (USD0.002187370), five controlled maintenance probes, two
existing autonomous study calls and 12 gateway attempts including one optional
repeat recovery. Existing USD18/2/20 caps; no fresh ledger, added recurring call
or paid service. Provider billing and pre-guard spend remain unknown.

Public [release evidence](evaluations/2026-10-12-abstract-projection-release.json)
preserves all negatives, methods and identifiers. Private app-volume refs/counts/
metrics and public helpers/invented fixtures use 0700/0600, existing manual seven-day
retention/withdrawal. Raw human/reply renderings and candidate overrides erased.
Final evidence PR, main CI and owned-worktree archive recorded in automation memory
after merge. Primary and earlier worktrees remain untouched.

### H47 completion patch selected

Evidence PR #87 merged 31f2409fd350a2f4d40591eb68542e87753ab9b2; required CI38278547201 and final-main CI38278806014 pass. Final review then finds an ordinary response wording bypass in the legacy classifier. Actual 2.19.0 probe admits audit/raw voice/source quotation, despite already delivering a relevant novel answer. Six new regressions fail baseline; three literal controls pass. Same run/worktree and increment: bounded modal/current-response routing closes this gap, preserving explicit source lookup. All six local gates pass, 808 tests and 96.86% coverage. New immutable patch 2.19.1 and installed actual acceptance pending; earlier 11/14 behavioral negatives remain authoritative.

### H47b final immutable rollout

[PR #88](https://github.com/jdegregorio/wcb-discord-bot/pull/88) merged
ddad4233a3a0b0ee293bb8f25c178fca959033f5, identical tested tree. Required PR
CI 38279728710/main CI 38279889685 and all merged gates pass: 808 tests,
96.86% coverage. Immutable [v2.19.1](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.19.1)
built both architectures in 38280069441. Reverified pi5/aarch64/Ubuntu 24.04.4,
deployed through locked pi-app; running sha256:053c84521d67a3b34e9f658612f2c6b6bfd54ca3021ae61da6d97672c048b696, matching OCI/package/28
source hashes and readiness. Previous 2.19.0/541d19ce retained. At 2026-10-12T17:04:20.484274+00:00:
zero restarts, errors, failures, disconnects or source/study pauses; two optional
voice warnings, zero others, four gateway posts, one decline, 12 learning batches.
No rollback.

Actual ordinary/past-word packet and lifecycle checks pass 2/2, behavioral 2/2;
five fresh gateway controls pass 5/5, completion 7/7. Cumulative installed packets
5/5 and behavior 18/21 across versions. Initial attribution and two brevity failures
remain open. Same Codex evaluator; no genuine human population hold-out benchmark,
active human pattern or broad fidelity gain. Additional baseline already supplied
a relevant novel turn despite its packet bypass. Actual fixture sends and five
normal refs authenticated privately, zero intake, no second gateway, heartbeat
healthy after close. Raw source/reply renderings erased. Fresh league audit:
three channels/latest 100/14 days, seven target/15 peer/five older bot/zero current.
Native 34/archive 16/graph 439 sources, 554 episodes, 1,015 edges unchanged;
two claims, one preference, zero patterns. Failed prototype stays retired.

Final tracked October USD 0.171527435, runtime 0.081063620,
maintenance 0.090463815; 1158 settled/zero unsettled.
Full run USD 0.009956075 across 52 attempts:
runtime 0.005784505, maintenance 0.004171570.
Includes 24 research calls, eight controlled maintenance probes, two existing
autonomous studies and 18 runtime attempts including optional repeat recovery.
Same USD18/2/20 caps, no fresh ledger/service/recurring request; billing/pre-guard
spend unknown.

[Completion evidence](evaluations/2026-10-12-abstract-projection-completion.json)
preserves final identifiers and all limits alongside the initial release record.
Evidence PR/final main CI and owned cleanup/archive are recorded in automation
memory after merge. One coherent increment completed under two immutable releases;
no restored human trait or unrelated runtime change.

Final operator privacy audit found local staging inherited mode 0755. Raw PNGs
and transfer archives were already erased; their transfer-file permissions were
not independently verified before deletion. Staging is now 0700, and persistent
app-volume evidence permissions pass 0700/0600. No raw artifacts remain. Do not
claim historical transfer privacy was fully verified or infer unauthorized access.
Future collection must create 0700 staging and 0600 transfer files before writing
human material. This operator gap does not change the healthy runtime or require
a version rollback; it is retained as a validation limitation.

## 2026-10-12 17:00 - memory author binding completion

Base 666adf2d018bfb8feb3d9fbd6678a230c47de858; main fetched successfully before a new
managed worktree and feature/trubot-daily-20261012-1700. Reconciles failed 13:00
uncommitted H49 prototype, no prior PR/release. Primary and original draft untouched.
Both planning phases and locked criteria are in [completion study](evaluations/2026-10-12-memory-author-completion-study.md), with inherited experiments explicitly separated.
Fresh actual baseline reproduces wrong source-person attribution. Typed source/focus
scope corrects five invented attribution cases (baseline 2/5); care and recipient
controls pass both. No human abstraction added. Local text audit covers four grouped
blocks/four exports/16 neighbors, zero marked media gaps; no pixels interpreted.
Three-channel latest-100/14-day scan has seven target/15 peer/five older bot windows,
zero current spontaneous replies. No provider human audit, no broad fidelity claim.
All six local gates pass, 838 tests/96.84%, 29 modules. PR/release/installed acceptance
are pending. Existing monthly allowance and app storage remain unchanged.

### 17:00 release, installed acceptance and limits

Runtime [PR #90](https://github.com/jdegregorio/wcb-discord-bot/pull/90) merged
734e381dc73ec41ed7d1331559dc3092ee6639ee, identical to tested feature tree. Required
PR CI38325341793, merged-main CI38325501523 and images38325633646 pass. Immutable
[v2.19.2](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.19.2)
builds both amd64/arm64. Reverified pi5/aarch64/Ubuntu24.04.4; scoped locked pi-app
transaction deploys sha256:e4ff71375b47226f2a8f617973d3ccd5d944fee6f30273725ec70c2946f155b1.
OCI/package/29 source hashes match. Prior healthy2.19.1/053c845 remains rollback
boundary. No schema migration or rollback. Main was rechecked through all six gates,
838 tests/96.84%,29 modules. Existing primary and original failed draft stay untouched.

Real installed controls3/3 for packets/lifecycle and behavior, using disposable
invented source stores. Distinct readiness before construction, no second gateway,
zero development intake, withdrawal and primary heartbeat after each close. Normal
actual owner gateway source grounding5/5; full review8/11, combined11/14. Retain
three-sentence broad recall, three-sentence care and initial creative cue miss;
unmentioned clarification recovers. Exact-date restraint, supported preference,
owner scope, actual owner reaction, novel banter and recipient abstention pass.
All owner/bot messages and the actual reaction were reauthenticated. References and
pass/fail categories are private; no raw source or answer text in public notes.

Post-release local audit: six central grouped human blocks across six exports,
24 neighbors, four additional authored support passages screened, zero marked media
gaps in the six windows. Original pixels unstudied. Latest100/14days in three league
channels: target7/7, peers15/12, older bot5/5 before/after, current spontaneous0/0.
No human provider audit, new human pattern, independent evaluator or genuine human
population hold-out benchmark. H49 is a supported grounding correction; it does not
establish general fidelity or amplified humor. H51 contextual cue reliability is
exploratory beside H22/H39; qualified human abstractions remain next.

At 2026-10-13T00:20:42.480781+00:00: healthy immutable2.19.2, zero errors/reply failures,
disconnects/source or study pauses/restarts; two optional Discord voice dependency
warnings, zero other warnings; ten gateway posts, one abstention and12 learning batches.
Persistent counts unchanged: native34, archive16/4299 grouped blocks/412 target/405
eligible; visual115/96 assets; graph439 sources/554 episodes/1015 edges/two claims/
one preference/zero patterns. No candidate override remained during installed tests.

October ledger estimate USD0.183547290, runtime0.085950445/maintenance0.097596845;
1245 settled/zero unsettled. Run delta USD0.007216365 over29 attempts, runtime0.004255825/
maintenance0.002960540:14 research requests, three real controlled maintenance probes,
12 runtime attempts including baseline and abstention. Existing USD18/2/20 caps;
no fresh ledger, paid service or added recurring request. Billing/pre-guard cost unknown.

Private app-volume smoke-tests/2026-10-12-1700 stores only content-free references,
counts, metrics, public helpers and invented fixtures,0700/0600 verified. Local staging
was0700 before collection; no raw human source/answer file persisted. Existing manual
seven-day retention and withdrawal cleanup apply. Temporary transfer archive/owned
browser cleanup, final evidence CI and archive completion are recorded in automation
memory. Source qualifiers remain private; failed older abstraction stays retired.
[Full release evidence](evaluations/2026-10-12-memory-author-release.json).


## 2026-10-12 21:00 H52 selection

2026-10-12 21:00 selection: H52 complete live conversational setup. Native and
historical neighbors are silently clipped at350 characters, losing qualifications.
Preserve complete rows up to600UTF-8 bytes and mark oversized rows as gaps so that
contextual memory does not misstate a human stance. Existing scope, attribution,
source lifecycle, participation and USD18/2/20 remain authoritative. No new model,
service, provider request or human abstraction. Both planning phases and acceptance:
docs/trubot-evolution/evaluations/2026-10-12-complete-context-study.md.

Next: H48/H21/H28 qualified human abstractions with genuine held-outs and H43/H6
controls; H22/H39 variation/brevity and exploratoryH51; H50 native peers/replies/
threads/pixels; bounded selective skills/tools and generated U.P. aurora/trail-camera
sharing. Targeted raw historical output was automatically rejected for private-log
risk; no workaround attempted or new trait populated. H52 is a concrete grounding
prerequisite, not a general fidelity claim. Six daily standalone runs unchanged.


### 21:00 candidate and actual reproduction

H52 changes complete native neighbor/same-channel-parent and historical adjacency
text, with600UTF-8 byte ceilings and explicit oversized gaps. Historical bot context
is separately labeled. All source lifecycle, scope, retention, budgets and existing
source-text ceilings remain authoritative; no new requests, service or human trait.
Thirteen invented regressions: baseline11fail/2pass, candidate13/13. Required six
gates pass,851tests/96.85%,29 modules and2.19.3 package build.

Actual owner/private Discord handler baseline packet silently clips the qualification;
matched candidate packet retains it. Both sends use disposable invented evidence,
existing maintenance ledger, distinct readiness before client construction, zero
fixture intake and successful withdrawal/primary heartbeat checks after close. Two
actual answers do not show a clear interpretation improvement; candidate has a novel
relevant joke. No general fidelity gain or new human pattern is claimed. The current
league audit has zero spontaneous current-release messages; wider quality stays open.
PR, immutable images, deployment and installed actual acceptance remain pending.


### 21:00 immutable release and actual acceptance

[PR #92](https://github.com/jdegregorio/wcb-discord-bot/pull/92) merged
31e07bb252a5c99aa90d7d5ac3d0263064013023. Required PR CI 38345600065, main
CI 38345714591 and image 38345838462 pass. All six gates were repeated on merged main,
851 tests/96.85%, 29 modules and package build. Immutable [2.19.3](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.19.3) has inspected amd64/arm64 manifests.
Reverified pi5/aarch64/Ubuntu 24.04.4; the release timer deploys through the locked
transaction and the scoped helper confirms current digest
sha256:c0e1921222f44c084af15903ce21cd17b158b7986dd50fa12c9c959f50db0e0a.
OCI/package/all 29 hashes and primary readiness pass. Prior healthy 2.19.2/e4ff713
is the recorded compatible rollback. No rollback or schema migration.

Installed actual owner/Discord source fixtures: packet/lifecycle 4/4, behavior 4/4.
Native, parent and archive qualifications are natural; oversized text is not invented.
An initial harness withdrawal assertion incorrectly expected empty recent context;
it is preserved as a harness failure, corrected and repeated successfully. Eight
normal gateway checks have grounding 4/4, full review 7/8 and combined 11/12. Preserve
stock care wording as a naturalness concern, with tone and two-sentence brevity passing.
No general fidelity/interpretation gain, humor multiplier, genuine human held-out
population benchmark or independent evaluator. Actual refs are privately authenticated;
no raw source/answer text is retained. Distinct readiness before construction, no
second gateway, zero development learning, withdrawal and main heartbeat pass.

At 04:39 UTC: zero errors/reply failures/disconnects/source or study pauses/restarts;
two optional voice dependency warnings, zero others; seven gateway posts, one decline,
one optional accounted repeat refresh. Native 34, archives 16/4299 grouped blocks/412
target/405 eligible, visuals 115/96 assets; graph 439 sources/554 episodes/1015 edges/two
claims/one preference/zero patterns, unchanged. Post counts-only audit has target 7/7,
peers 12/12, older bot 4/4 and current spontaneous 0/0 in three latest 100/14-day channels.
The raw-output audit was automatically rejected, then replaced by a safe counts-only
helper. No new human source renderings in the post-audit. Targeted transcript reading
remains blocked; six private short humor refs in one export await a safe approved
inspection, not source support. Zero provider human studies or new human traits.

October ledger estimate USD 0.188154895, runtime 0.089505790/maintenance 0.098649105;
1261 settled/zero unsettled. Run USD 0.004607605 over 16 attempts: runtime 0.003555345
(nine attempts including eight cases/one repeat refresh), maintenance 0.001052260
(seven invented controlled requests including the failed initial harness). Existing
USD18/2/20 caps, no fresh ledger/service/recurring request; billing/pre-guard unknown.
Private app-volume smoke-tests/2026-10-12-2100 uses 0700/0600, content-free refs/counts/
metrics, public helpers and invented fixtures only, existing seven-day manual retention
and withdrawal cleanup. Candidate override and obsolete raw-output helper are removed.
Primary checkout and earlier failed draft stay untouched. Final evidence CI/archive
completion will be recorded in automation memory.
[Full release evidence](evaluations/2026-10-12-complete-context-release.json).


## 2026-10-13 01:00 - H53 selection

Both planning phases and locked criteria: [study](evaluations/2026-10-13-passage-repetition-study.md). Select substantial stale passage recovery underH22/H39 after8baseline failures/9negative controls. Fresh actual care is a contrary non-repeating case with3sentences; no new human trait or broad gain. Mechanical private source coverage405eligible blocks/15exports/zero cross-export12-word overlaps is not semantic/independent-episode proof. Current spontaneous league output0. H48 human population remains unresolved with approved semantic inspection prerequisite; nextH54 native contextual dependencies, remaining variation/brevity/cues, wider native/visual, selective tools/skills and generated outdoor scenes. Priority documents consolidated; prior evidence remains in progress/research/evaluations/Git. Runtime verification pending.


### 01:00 H53 immutable rollout and actual limits

[PR94](https://github.com/jdegregorio/wcb-discord-bot/pull/94) merged
7b5661f636b8b4174f07b72b8305e37a90c3d605; PR 38368883700 / main 38369046594 / image
38369227636 pass. All six gates repeated on merged main:868 tests/96.86%,29 modules
and2.20.0 build. Immutable [2.20.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.20.0),
both architectures inspected. Reverified pi5/aarch64/Ubuntu24.04.4, scoped locked
pi-app transaction deployed sha256:b83f3de51d1acbe9ea9b70d6d36735cc2107923102141917331320195bd806fb.
OCI/package/29 hashes/readiness match,0 restarts. Compatible2.19.3 / c0e1921 rollback
retained; no rollback/schema/intake/state/model/service change.

Actual identical invented handler pair: baseline keeps seeded stale passage/no
provider call; candidate and installed release each make one real maintenance
refresh and deliver fresh warm wording. These are seeded recovery checks, not
spontaneous generation improvement. Both refreshed replies have3 short sentences.
Fresh normal gateway11 cases/10 posts/1 recipient decline; final full review8/11:
care and enthusiasm remain3 sentences, and additional broad-recall claims are
unvalidated. Initial manual9/11 is narrowed when that source-support gap is made
explicit. Narrow memory controls3 pass/1 partial; quotation equality, contextual
follow-up, novel banter and TJ pass. No new human trait, general fidelity/humor
multiplier or independent human benchmark. Exact dates are not invented and ordinary
recall stays natural. First baseline harness stopped before sending because the
normal gateway answered in its active window; corrected harness records each path
separately. No fake provider usage for the synthetic draft.

Automatic approval review rejected an OPTIONAL helper that would send four private
source packets and actual recall replies to OpenAI for grounding review, requiring
explicit authorization for that payload/destination. No helper execution/provider
request or workaround. Specific approval requested; source-support questions remain
unvalidated. Unaffected delivery/deployment/audits complete. No private raw/derived
text enters public notes, logs or actual smoke artifacts. An unexecuted public-code
helper is preserved privately for review, not automatically dispatched next run.

Pre/post league3 channels/latest100/14days:7 target/12 peers/4 older bot/0 current
spontaneous. Mechanical human405 eligible grouped blocks/15 exports/0 cross-export
12-word overlaps is not semantic review/independence/habit proof; no pixels interpreted.
Learning34, archives 16/4,299 grouped/412 target/405 eligible, visuals115 / 96 assets,
graph439 sources/554 episodes/1,015 edges/2 claims/1 preference/0 patterns unchanged.
At08:44 UTC zero errors/reply failures/disconnects/study pauses/restarts;2 optional voice
dependency warnings/zero others,10 normal gateway posts/1 decline/zero normal refreshes.

October ledger estimate USD 0.1944345, runtime0.09511546/maintenance0.09931904,
1,279 settled/zero unsettled. Run USD 0.005992355:15 runtime attempts/USD 0.00560967 and
2 maintenance refreshes/USD 0.000382685. No fresh ledger/paid service/cap change;
USD18/2/20, billing/pre-guard unknown. Private app-volume smoke-tests/2026-10-13-0100
retains content-free authenticated refs/counts/flags, public helpers and invented
fixtures,0700 / 0600, seven-day manual retention/withdrawal. Distinct readiness BEFORE
construction/no second gateway/zero development learning; primary healthy after closure.
Candidate override cleanup and final evidence CI/archive recorded in automation memory.

Next: qualified human abstracts with approved semantic inspection/genuine held-outs;
native study context dependency invalidation; remaining brevity/short-stock/cues;
wider native/reply/thread/pixels, selective skills/tools and generated U.P. aurora/
trail-camera scenes. Six standalone hours, Sol/xhigh and notification setting unchanged.
[Release evidence](evaluations/2026-10-13-passage-repetition-release.json).


## 2026-10-13 05:00 Pacific - H54a native pattern evidence gate, candidate

Base077de5fa4a73d72d68f8e56f84d654fa216f19c7, new managed worktree/unique branch,
primary untouched/no overlapping evolution PR. Phase1 found native target-only
packets could establish recurring patterns without durable setup; Phase2 advances
context provenance and qualified population as coupled prerequisites. Candidate
2.20.1 gates all five automatic pattern domains at schema/validator/storage/restored
recall, including counterevidence. Normal sweep erases incompatible derivations and
graph backups. Native literal recall, operator review, contextual Slack patterns,
source lifecycle/pacing/withdrawal remain. No schema/model/provider-payload/extra-call
change, no forced historical replay and no new human trait. Source and package
versions agree. Data-compatible2.20.0 rollback restores the prior permissive gate.

Same-case final baseline31fail/2negativepass; candidate33/33. Corrected a synthetic
full-cycle source-date mismatch before final baseline and moved automatic pattern
positive fixtures to genuine disposable contextual archive storage. All six gates:
901tests/96.92% coverage/29 typed modules/package2.20.1. Actual matched owner private
fixtures: baseline stores/retrieves invented automatic pattern; candidate blocks
storage/restored recall and excludes the abstract packet. Both deliver relevant
brief actual handler replies, one real maintenance request each. Normal gateway
attention-window replies are separate; synthetic stubs are never billed as requests.
Distinct ready paths BEFORE construction, no second gateway/development learning;
primary heartbeat survives close. Production learning and pacing are untouched.

Audit3leaguechannels/latest100/14days:7target/12peers/4olderbot/0current spontaneous.
Historical405eligible grouped blocks/15exports mechanical coverage only; semantic
human and original-pixel review unavailable here. No new Andrew trait or reply-quality
multiplier is claimed. Prior optional private model-audit payload approval remains
pending; no rejected operation is retried. Native34; archives16/4,299 grouped/412target;
visual115/96assets; graph439sources/554episodes/1,015edges/2claims/1preference/0patterns.
Actual release/deployment IDs, post-audit and spending to follow after rollout.
[Study and acceptance](evaluations/2026-10-13-native-pattern-study.md).


### 05:00 H54a deployed and verified

[PR96](https://github.com/jdegregorio/wcb-discord-bot/pull/96), feature
c1d710dd0e145a3f579c354dc5b70726080a3cd9, merged a33778ad643cf0c5611404323c7afc58c24d4558.
Required PR38396271206/main38396459351/image38396690373 CI pass. Merged-main all6gates
901tests/96.92%/29modules/build2.20.1. Immutable
[release2.20.1](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.20.1)
both architectures inspected; pi5 scoped locked transaction deployed
sha256:8ed7cf72ff9e54623ee41f59a6b49d853c230facb74b8a9740a6aefb4a92937d.
OCI/package/module/29hashes match, healthy/Discordready/0restarts. Previous2.20.0/
b83f3de recovery retained. No migration/rollback. Automatic review rejected printing
version envfile before execution; safe status/image inspection completed verification
without exposing env contents or requesting unnecessary approval.

Installed actual controlled fixture also blocks automatic native pattern storage and
restored recall/abstract input. Three actual controlled sends total, each real
maintenance request, relevant2sentences, invented disposable sources only. All refs
reauthenticated. Distinctready BEFOREconstruction/no secondgateway/no development
learning; primaryready survives close. Normal installed5cases/4posts/1recipient decline;
manual full4/5. Care/TJ/author/recipient pass. Baseball is natural but strict local source
binding unmatched, so grounding remains unvalidated. A specific query finds an
existing3source reviewedclaim, not a preference; incomplete topic binding does not
prove a wrong answer or new regression. No rejected private model audit retried,
new trait or general fidelity gain. Full human semantic/pixel review remains open.

Postaudit unchanged3channels/latest100/14days:7target/12peers/4olderbot/0spontaneous;
405eligible grouped blocks/15exports mechanical only. Private source/graph counts and
zero activepatterns unchanged. At12:30UTC0errors/replyfailures/disconnects/studypauses/
restarts;2Discordclient warnings/0memoryverification warnings. Monthly ledger estimate
USD0.198290225(runtime0.098401445/maintenance0.09988878),1290settled/0unsettled. Run
USD0.003855725/11attempts(8runtime includingabstention,3maintenance). USD18/2/20caps,
no newservice/ledger/call policy, billing/preguardunknown. Candidate override removed
by container replacement; disposable DBs deleted. Contentfree private refs/helpercode
0700/0600 at smoke-tests/2026-10-13-0500 retain existing7daymanual policy/withdrawal.
Final evidence CI and owned-worktree archive recorded in automation memory.
[Release evidence](evaluations/2026-10-13-native-pattern-release.json).


## 2026-10-13 09:00 Pacific: H55a bounded native setup links

New managed worktree trubot-daily-20261013-0900; base
dcb55f31fb98424bed68b6fb892c40137e4ac095, unique feature/trubot-daily-20261013-0900.
Fetched origin/main before branch/source mutation. Primary checkout never edited,
stashed or reset. Prior run96/97 and archive completed; only dependency PRs remain.
Used gh-axi and Raspberry Pi deployment skills; existing app key/maintenance ledger.

Both planning phases: [locked hypothesis/experiment](evaluations/2026-10-13-native-context-links-study.md).
Selected enabling native context links so future abstraction can track setup evidence.
Split H54b into H55a capture and H55b fresh dependency verification/study integration;
qualified H48 population remains coupled next. Retain broader native/pixels, varied
brief humor/cues, selective skills/tools and generated U.P. aurora/trail-camera scenes.
No unvalidated behavioral assumption or new human pattern is shipped.

Candidate2.21.0: optional existing live native collector records metadata-only links
under the source lock.100 captures/five human dependencies/30-day capture expiry/
native retention; source times, reply links, text hashes, gaps and provenance. Known
peer/source invalidation, restored corrected target neighbors, retention and withdrawal
erase captures/orphans/backups. No peer/source text copied, no schema/checkpoint/model/
source replay/service/additional provider or Discord request. Native automatic pattern
gate remains closed. Metadata does not prove current visibility or complete context.

Final same-case baseline29fail/candidate29pass. Full six gates:930tests/97.00% branch
coverage/29typed modules/build2.21.0. The cap test exposed an eviction tie-break fixed
before final validation. These are invented engineering cases, not human-quality gains.
Actual H55A/B private owner probes, identical invented sources/setup/history/model:
baseline0captures/dependencies; candidate1/1, restart/deletion/raw-text absence/gate
controls pass. Each made one genuine maintenance reply through real memory/respond
handlers, relevant/natural without metadata disclaimer. Distinct readiness before
construction/no second gateway/no development learning/disposable source databases
removed. Fixture helper ownership error from docker cp was corrected by writing as
app UID; no production source/credential/readiness mutation. Candidate package override
is isolated to the validation process and will be removed after installed verification.

Authenticated preaudit3source channels/latest100/14days:7target/12peers/4older bot/
0current spontaneous. UI semantic review7target messages/four dated groups/five older
bot posts, with peer setup/reactions and linked reply; no new generalized human trait.
No original-pixel study or private provider audit. Current graph439sources/554episodes/
1015edges/two claims/one preference/zero active patterns; native34,archives16/4299grouped/
412target/405eligible,visual115/96assets. Mechanical source coverage is not an independent
human-pattern benchmark. Optional prior specific private provider-audit approval gap
remains unexecuted. No measured general fidelity or 2-3x humor gain.

PR/required CI/tested merge/immutable release/both images/pi5 deployment/installed
acceptance and fresh normal gateway controls remain the final release steps and will
be recorded after verification. Pre-run covered October estimateUSD0.198290225,1290
settled/zero unsettled; USD18/2/20 guard unchanged, billing and pre-guard spend unknown.
Private artifacts keep only references/flags and public fixture code in existing app
volume0700/0600; actual answer/raw source text is not retained in smoke records.

### H55a release and installed result

[PR98](https://github.com/jdegregorio/wcb-discord-bot/pull/98) runtime merge
4ab648a355f8466b9391bff5e2692d330d0b0e99. PR38429872141/main38430316576/image38430535875
all successful; full six gates repeated on merged main930tests/97.00%/29modules/build2.21.0.
[Immutable2.21.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.21.0)
AMD64/ARM64 inspected. Reverified pi5/aarch64/Ubuntu24.04.4/helpermanifest/lock/permissions,
scoped transaction deployed cfd8f29ea6c878fefffa9fdaac3c593d004332e0d5f29c2acdecffacf2070c10.
OCI/package/module version/all29source hashes match tested runtime; healthy/ready/
0restarts after separate installed client close. Previous2.20.1/8ed7cf7 retained.
No rollback/migration. Candidate override removed before installed acceptance.

Installed actual H55C repeats1capture/1dependency/reopen/delete/raw-text absence/
gateclosed/relevant reply. H55A/B/C actual private refs reauthenticated; invented
sources only,3genuine maintenance requests. Five fresh normal gateway cases yield
four posts and one recipient decline. Manual presentation/grounding controls5/5:
brief sincere care, relevant novel TJ fiction, ordinary baseball direct/natural,
recent attributed recall agrees with viewed source messages, recipient restraint.
No routine storage/date disclaimers. Existing source-topic retrieval confirms coverage;
this is not independent model grading, a new human preference or resolution of the
prior strict preference-only audit gap. No human held-out semantic pattern benchmark
or general fidelity/2-3x humor gain. UI raw answer/source text is not saved in artifacts.

Genuine native capture initially2source neighborhoods/five dependencies, final5/nine.
Known lifecycle/bounds valid; current visibility/completeness not certified. Source/
learning/claim/preference counts and zero active patterns unchanged. Authenticated
pre/post3channels/latest100/14days:7target/12peer/4older bot/0current spontaneous. No
new original-pixel or provider private audit, prior specific approval gap unexecuted.
Postrollout0errors/replyfailures/disconnects/restarts/memorywarnings;2discord.client
warnings. Sparse activity prevents a general error-rate or character-quality estimate.

October estimateUSD0.20082361(runtime0.100326035/maintenance0.100497575),1298settled/
0unsettled. RunUSD0.002533385 across8attempts:3maintenance/5runtime(one abstention).
USD18/2/20 unchanged; no added service/reads/provider requests. Estimates not billing;
pre-guard spend unknown. Private refs/flags/public fixture code in app-volume
smoke-tests/2026-10-13-0900,0700/0600, existing seven-day manual retention/withdrawal.
Disposable databases removed; primary readiness survives validation close.
[Content-free release evidence](evaluations/2026-10-13-native-context-links-release.json).

H55a validated enabling increment complete. Next H55b fresh native context checks/
study integration + qualified H48 abstract population; brevity/variation/cues, broader
native/pixels and selective skills/tools/generated outdoor scenes remain ordered.
Public rollout evidence is committed before owned worktree archive; evidence-only
PR/final main CI and archive confirmation are recorded in automation memory.

## 2026-10-13 13:00 Pacific: H56 native setup freshness, in progress

Basea611bd2, NEW managed worktree trubot-daily-20261013-1300 and unique feature branch;
primary checkout untouched. No unfinished evolution PRs; prior run archived.
Both planning phases recorded in [study](evaluations/2026-10-13-native-freshness-study.md)
and reconciled with plan/backlog/ROADMAP/harness/living-memory/storage.
Authenticated bounded audit3channels/latest100/14days:7target/12peers/4older bot/
0current spontaneous. Contextual human/peer/bot review, no new generalized trait or
original-pixel interpretation. No optional previously rejected provider-audit payload.
Actual private owner baselineH56A:1capture/1dependency, missed edit remains.
Same-source/history/model candidateH56B: missed edit erased, source/peer text absent
from metadata, relevant one-sentence delivery/no routine metadata disclaimer preserved.
36 focused synthetic lifecycle/scope/privacy/bounds/race cases pass. Invented stores
only; distinct readiness before construction/no second gateway/development learning.
All six feature gates pass:966tests/96.92%/30typed modules/build2.22.0. Release,
installed validation and cost delta pending. This is enabling
context correction, not a measured abstract-personality or humor improvement.

H56 first release2.22.0: PR100 mergedf14a6ba; PRCI38461948010/mainCI38462145135/image
CI38462398173 SUCCESS; feature+merged gates966tests/96.92%/30modules. Scoped pi5 deployed
e6fac529895723ae418c5170ab567b727e792b1ee25478e47946173d15ced8d3; installed hashes match,
healthy/ready/zero restarts. Actual installedH56C repairs missed edit, private real
owner/reply refs reauthenticated. Normal gateway6cases/5posts/1recipient abstention;
care21words/three sentences and stock preface remain H22/H39 gaps, TJ relevant novel
fiction, baseball/recent natural and source-topic available, recent quotations match
viewed human sources. Broad past answer52words/two sentences/no metadata caveat;
no independent historical semantic quality grade or calendar-date proof. No new trait.
Covered estimateUSD0.20456879/1309settled/zero unsettled, runUSD0.00374518/11attempts,
3maintenance/8runtime including abstention/one optional refresh. Guard18/2/20 unchanged.

Three live background cycles1checked/1unavailable motivated additional matched probes:
baseline and three timeout/ordering alternatives each1/2, bounded-page prototype2/2
within1.5seconds. Rejected alternatives stay process-isolated, unshipped. H56b coherent
transport correction selected for immutable2.22.1; source/parent/dependency/scope/lifecycle
checks and six-second ceiling retained, HTTP maximum reduced to six.40focused cases;
full gates/release/actual installed validation and final evidence still required.

Finalruntime2.22.1: PR101 merged29d86dd afterrequiredCI38467186010; mainCI38467547406,
imageCI38467848695 SUCCESS. Feature+merged allsixgates970tests/96.91%/30typed/build2.22.1.
Live target/both image architectures verified. Scoped helper transaction deployed
f2512b462508663f31b88126682c196bb487f6824fd516c37e025eb89371b49d; OCIcommit/package/module/
all30sourcehashes match testedmain. Healthy/Discord-ready/zero restarts. Immediate
rollback2.22.0/e6fac5 retained, original2.21.0/cfd8f29 cataloged; no rollback/migration.
SAME installed cohort2/2in0.831seconds; all alternatives rejected and overrides removed.
Captured-cohort copy erased after comparison. ActualH56D owner/installed-handler
missed-edit/reopen/privacy/gate acceptance passes, natural relevant one-sentence reply,
distinct readiness before construction and primary health after close. New actual
background cycles2checked/0unavailable. No new human abstraction/generalfidelitygain.
Finalfreshgateway/cost/refs/docs-onlyevidencePR and cleanup follow below.

Final actual private gateway6cases/5posts/one recipient abstention. Care17words/three
sentences/repeated preface and TJ15words/paraphrased prior premise keepH22/H39open;
baseball4words/direct/natural, recent9words/sourcequotes agree with viewed human
messages, past48words/two sentences/no routine metadata caveat. LOCAL source study
5selected attributed grouped blocks/15adjacent/1export supports final past paraphrase,
with peer corrections separate and no calendar-date proof or independent qualitygrade.
No new generalized human observation is inferred or populated. Private artifacts retain
refs/counts/passflags only. Prior optional specific provider-audit request not executed.

Finalaudit3channels/latest100/14days unchanged7target/12peers/4olderbot/0current
spontaneous; contextualUIreview5target/3olderbot. Native34; archives16documents/
4,299grouped/412target/405eligible and115visualepisodes/96assets. Graph439sources/
554episodes/two claims/onepreference/zero patterns,5captures/9dependencies,8checkpoints.
Four actual background cycles2checked/0unavailable; zero errors/replyfailures/memory
warnings/disconnects/restarts, two Discord startup warnings. Sparse activity limits
rate conclusions. No original-pixel interpretation or human-held-out pattern benchmark.

Covered October estimateUSD0.207282965(runtime0.10578422/maintenance0.101498745),1,316
settled/zero unsettled. RunUSD0.006459355/18attempts:4maintenance/14runtime, including
two recipient abstentions and one optional refresh. Guard18/2/20 unchanged; zero provider
calls from source experiments/feature, zero paid additions; billing/pre-guard unknown.
[Content-free release evidence](evaluations/2026-10-13-native-freshness-release.json).
All candidate packages, synthetic stores and cohort copies removed. Private app-volume
refs/flags/counts/public code/hash artifacts0700/0600, manual seven-day/withdrawal cleanup.
All source commands used the NEW owned worktree; primary remains untouched.
Final documentation evidence is in [PR102](https://github.com/jdegregorio/wcb-discord-bot/pull/102).
Its checks verify the unchanged runtime tree. Archive follows evidence merge; its
actual completion receipt is retained in automation memory and the worktree artifact.


## 2026-10-13 17:00 H57 candidate2.22.2

Baseabfe526; unique new managed worktree/feature branch; primary untouched. Both
planning phases: authenticated bounded audit7target/12peer/4older bot across3channels,
no current spontaneous output; contextual5target/3olderbot and six previous private
answers reviewed separately. No image inference or new human abstraction. H57 selected
from two reproduced obsolete-memory commits; H55b/qualified abstracts remain next.

Fresh native source reads before each maintenance attempt and reviewed commit preserve
original cohort/payload, source/withdrawal and atomic local validation, four-hour lease,
closed native pattern gate and existing ledger. Six seconds/four per read; at most
24HTTP reads/study, no extra provider request/model/schema/service.26focused cases;
all six local gates996tests/96.87%branchcoverage/30typedmodules/build2.22.2.
Actual private matched owner/handler fixture: baseline commits obsolete invented
preference, candidate commits none; both actual replies use corrected source naturally.
Actual native same-cohort preflight2reads/521ms versus4reads/947ms, zero provider/send/
gateway/real-state mutation; copies erased. Initial log-harness umask fixture failure
and stalled backup helper corrected; no evidence claimed from failures. No measured
general fidelity or humor gain. CI/release/deployment/installed acceptance pending.
[Research and acceptance](evaluations/2026-10-13-study-freshness-study.md).

## 2026-10-13 21:00 H58a candidate2.23.0

Baseccd3ec493b284275812164b150e4ccd5c93cd967; new managed worktree
trubot-daily-20261013-2100 and unique feature branch. Primary never edited/stashed/reset.
Prior PR103 merged/deployed2.22.2/536a76c, installed C/D refs reauthenticated and actual
Discord answers inspected. Prior run stopped at account usage limit before final notes;
no overlapping evolution PR. This run completes the reconciliation and fresh controls.

Both phases in [study](evaluations/2026-10-13-native-study-context-study.md).
Fresh authenticated audit3channels/latest100/14days:7target/12peer/4olderbot;
contextual UI5target/3olderbot, no current spontaneous output or original-pixel study.
No new abstract human observation or independent held-out human quality benchmark.

Selected H58a local native setup dependency lifecycle after rejected semantic-payload
expansion. Final same-case baseline17fail/7pass; candidate24/24. Actual private owner
baseline commits obsolete invented preference, candidate pauses. Both actual roleplay
replies are relevant. Invented disposable source stores only, target-only study payloads,
existing maintenance ledger, distinct readiness before construction/no second gateway.
Provider peer-transfer approval remains pending; no rejected payload path retried.
Candidate ties existing capture fingerprints to study checks/locked commit/observations,
correction/removal/replacement/expiry/withdrawal/backups and preserves unchanged recapture.
Source cohort/checkpoint version/model/native pattern gate/spending guard remain.
Full quality/release/installed acceptance and final costs pending.

Feature allsixgates pass:1,020tests/96.86%branchcoverage/30typedmodules/build2.23.0.
Final24focused cases cover privacy, native gate, correction, races, transport,
unchanged recapture, restoration, withdrawal and checkpoint/backup retirement.
Local QA log preserved0600 in this automation directory outside the worktree.

### Prior H57 reconciliation

Verified PR103 mergedccd3ec4, required PRCI38488394986/main38488564708/image38488779154
SUCCESS. Production2.22.2 immutable536a76c3dd6a9a4bb58781d6d423877f5eca2c294eb43579305ad20b24337cc6
healthy/Discordready/zero restarts. Prior C/D actual installed private receipts were
reauthenticated; both block obsolete invented memories and actual answers are direct
current-source replies. Previous run ended at account usage limit after these tests,
not at a product failure. Its missing fresh gateway controls are not retroactively
claimed; this run performs fresh controls after its own release. Covered ledger at
run startUSD0.20793597/1320settled/0unsettled; includes prior four maintenance probes.

### H58a released and verified

[PR104](https://github.com/jdegregorio/wcb-discord-bot/pull/104), feature4a4b918,
mergedb96f8f92254432e65070ee5220e26b6dc8076076. Required PR38510455595/main38510641533/
image38510812783 CI SUCCESS. Feature and merged six gates:1,020tests/96.86%/30modules,
build2.23.0. One mistyped merge-head SHA was rejected; retried with the verified
unchanged tested SHA. No protection bypass, tag reuse or agent coauthor.

[Immutable2.23.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.23.0),
both architectures verified. Reverifiedpi5/aarch64/Ubuntu24.04.4/manifest/helper/locks/
rollback/group write access; sudo unavailable and unnecessary. Scoped helper deployed
4cc40f2d0eeec0a03c9d55cd3bf329573061a06ab8862b72cb9d7c5feb662a77. OCIcommit/package/
module/all30sourcehashes match tested release. Healthy/Discordready/zero restarts.
Previous2.22.2/536a76c retained; no rollback or schema migration. Before downgrade,
retire only context-dependent observations/checkpoints/backups with current code;
source/capture/spending stores remain. Legacy readers ignore the new metadata.

Actual installed C/D probes: review-stage missed setup edit blocks observation;
post-commit setup deletion retires it. Four controlled real owner/handler replies
including baseline/candidate/installed, all refs reauthenticated. All relevant roleplay
answers, no raw answer artifact. Extraction/review stubbed on invented sources;
zero genuine provider study calls and four genuine maintenance reply attempts.
Distinct readiness before construction/no second gateway/no development learning.
Candidate override removed before installed checks; disposable stores/copies erased.

Read-only same real two-capture cohort verifies all four boundaries2/2, stage869/3714/
822/776ms under6seconds. Zero provider/send/gateway/real-state mutation. Two actual
installed worker cycles2verified/0removed/0unavailable. This is transport/lifecycle
acceptance, not a measured human abstraction or reply-quality gain.

Fresh normal gateway6cases/5posts/1correct recipient abstention. Local contextual
presentation/recipient5/6: care20words/3sentences/stockpreface remains open, humor14words/
1relevant creative sentence, baseball4words/direct/natural, recent16words/2manual
sentences/quotes match viewed human messages, past33words/2sentences/no exact-date
assertion or routine metadata caveat. Sentence-count heuristics miss quoted punctuation;
manual meaning review is authoritative. Strict preference-only and independent historical
semantic audits remain unvalidated; prior optional rejected provider audit never sent.
No new human habit or measured2-3xhumor gain.

Fresh bounded pre/post league audit unchanged7target/12peer/4olderbot in3channels,
zero current spontaneous posts; UI5target/3olderbot reviewed with setup. No new original
pixels. Coverage34native/16archives/4299grouped/412target/405eligible/115visual/96assets;
graph439sources/554episodes/2claims/1preference/0patterns/5captures/9dependencies.
Three legacy observations, two native-supported/one automated native, were not
retroactively linked or revalidated. Genuine production has0context-bound observations
so far; new-study correctness is demonstrated by invented handler acceptance only.

Observed post-release0errors/replyfailures/memorywarnings/disconnects/studypauses/
restarts;2startup Discord warnings. The early worker counter used the wrong label,
corrected before reporting two actual successful cycles. Sparse league activity limits
rate/fidelity claims. October covered estimateUSD0.210867275(runtime0.107923395/
maintenance0.10294388),1330settled/0unsettled. RunUSD0.002931305/10attempts:4maintenance
replies/6runtime including recipient abstention. Guard18/2/20 unchanged, no new service,
not provider billing; pre-guard spending unknown. Specific semantic peer-context transfer
approval remains pending after automatic review rejection; local-only correction complete.
[Content-free release evidence](evaluations/2026-10-13-native-study-context-release.json).


## 2026-10-14 01:00 - H59 bounded brief-reply repair

Base f871005e13d010a8890e93ad2b28b6677925af4c, new managed worktree and unique
feature/trubot-daily-20261014-0100 branch, primary untouched. Prior run completed,
no unfinished evolution PR. Both planning phases, authenticated bounded character
audit and fresh actual owner/gateway care reproduction completed before selection.
Three channels/latest100/14days:7target/12peer/4olderbot; UI5target/3olderbot with
context. Zero current spontaneous activity; one image turn excluded, no new human trait.

H59 prototype:9baseline failures/13controls,22/22candidate;31final safeguards.
Same-model synthetic12contexts/3samplesperarm,72finalanswers reviewed: care/celebration
brevity17/21to21/21, no new grounding/recipient/grief-control regression observed.
36baseline/42candidate accounted attempts. Gentle jokes in two low-stakes setback
answers remain contrary evidence to a general emotional-judgment claim; stock care
prefaces/humor variety remain open. No independent human-care hold-out or broad
fidelity gain. Full [research](evaluations/2026-10-14-brief-reply-study.md).

Selected repair shares one optional quality attempt with repetition, conservatively
exempts literal/detail/creative requests, rechecks private memory before reuse,
accounts same purpose, preserves failed/overlong drafts without truncation. No native
study payload/pattern gate/ledger/schema/source/schedule change. Specific approvals
and H48/H55b qualification stay open. Candidate2.24.0 awaits gates, tested merge,
immutable release/images/scoped deployment and fresh actual Discord acceptance.

Feature six gatesPASS:1,051tests/96.87%branchcoverage/31typedmodules/build2.24.0.
Line-length lint failure corrected and complete gates rerun. TrialUSD0.004066880
maintenance/78settledattempts, plus actual baseline questionUSD0.000599750;
coveredOctoberUSD0.217613030/onepreexistingunsettledreservation. Estimates, not
billing; pre-guardspendunknown. Release and installed acceptance still pending.


### H59a real acceptance failure and H59b correction

PR106merged922c260237c8b74367c4aa480c394390cba9eb70, CI38534523682/
38534769398/38535048934success. Immutable2.24.0/f5179a0 deployedhealthy/all31source
hashesmatch, but fresh actualcare remains3sentences. Logs confirm1repair/2accounted
attempts/noerrors/stilloverlongfallback. Synthetic trials omitted accumulated chat.
The release is marked prerelease/notlatest, tagbytesunchanged; scopedtransaction
rollbackrestored2.23.0/4cc40f2healthy/Discordready. No source/state/ledger restore.

H59b supplies actualfalliblebotdraft and repeats originalfocus/authorbinding in the
same optional attempt, reserving its serialized bytes. Repetition-only shape and
imagecountremain.32finalfocused cases include author/image protection; testfixture
corrected to use authoritative memory-origin binding, rather than expecting a focus
label to establish identity. Actualcandidateowner/handler H59B: firstdraft3sentences/
20words, accountedrevision1sentence/12words, actualsendreviewednatural/sincere.
Distinct readinessbeforeconstruction, nosecondgateway/developmentlearning/rawartifact;
primaryheartbeathealthyafterclose. Same-model accumulated-history matched trial and
allreleasegates remain pending. Same coherent dailyincrement, candidate2.24.1.


### H59b2.24.1 verified final runtime outcome

PR107 merged e761f965c92b311789a334f023e727f6549e41de, CI38537163276/
38537462172/image38537848820SUCCESS; feature/merged6gates1,052tests/96.87%/31typed/
build2.24.1. Stable immutable [release](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.24.1)
running c2553b4f5876c7c1db76a047771c1497a3f17ccacd02c7d62e4db9ca872c46de,
all31sourcehashes/OCIcommit/module/package match. Release timer completed scoped
transaction during manual preparation; helperconfirmedalreadycurrent. Pi5/aarch64/
Ubuntu24.04, healthy/Discordready/0restarts, previousgood2.23.0/4cc40f2retained.
2.24.0prerelease/notlatestflagreauthenticated, tagbytesunchanged; earlierrollbackverified.

Seven normalactualowner/gatewaycases,6authenticatedposts/1accountedcorrectabstention,
9providerattempts/2successfulcare repairs. Care12words1sentence, heldoutvariation14/1,
banter12/1, ordinarypreference4/2, broadpast43/2, exactday7/1naturaluncertainty. Source
claimscheckedprivately with7ArchiveStore.contextwindows/2documents/21groupedblocks/
8target13peer, plus authenticatednativeevidence. Unknowncalendar dates remaininternal;
ordinaryanswersno metadata caveat. No exactcalendar assertion, source ownership mixup,
new biography or insensitive care in these controls. Variation's thirdperson operator
wording and stockprefaces remain quality questions; no human-care holdout/generalgain.

Actualowner-to-botlatencies3.3-11.3seconds, care10.0/11.3seconds. Source-reuse refusal1
made no extra call; actual6posts vs5adaptercompletionlogs corrected before reporting.
Zeroerrors/replyfailures/disconnects/studypauses/restarts,2startupSDKwarnings; sparseleague
activitylimitsrates. Pre/post3intakes/latest100/14days7target12peer4olderbot0current
spontaneous; native34/439graphsources/554episodes/3legacyobservations/0patterns.
Existing recall nowrecords6content-freecaptures/9dependencies, no newhumantrait.

CoveredOctoberUSD0.226279000,1,506attempts/1preexistingunsettledreservation; run175
settled/USD0.013332600 (163maintenance/USD0.008018325,12runtime/USD0.005314275).
Finalgateway9/USD0.003774565. Estimatesnotbilling,pre-guardunknown,18/2/20unchanged,
noaddedpaidservice. Privatecontent-free receipts0700/0600; trialoverrides/rawdiagnostic
stagingerased, no sourcestate/withdrawal/usage restore. NewH60shortfactualrechecklatency
hypothesis remainsunvalidated; qualifiedH48/H55babstractpopulation/legacyreviewstays
nextwithspecificapprovalandheld-outs. Source/visual/tools/generatedoutdoorthemesretained.
[Complete structured evidence](evaluations/2026-10-14-brief-reply-release.json).


Completion evidence: [PR108](https://github.com/jdegregorio/wcb-discord-bot/pull/108).
It changes documentation only. Runtime, tests, version and lockfile are identical to
released commit e761f965c92b311789a334f023e727f6549e41de. The run's three PRs are
attached to its chat and labeled codex and codex-automation. Private receipt refs and
quality logs are preserved before archiving only this run's managed worktree.

## 2026-10-14 05:00 - H60a short reply continuity

Base 66de3e9a1c30eba98cbcb4585e0ff67d11d572ab; new managed worktree and unique
feature/trubot-daily-20261014-0500 branch. Prior evolution complete, no unfinished PR.
Primary checkout untouched. Fetch used authorized network after sandbox DNS failure.
Both planning phases and fresh actual gateway reproduction preceded runtime changes.
Selected bounded short continuity after two accounted calls with unchanged four-word
output; baseline 17 new failures/2 controls, candidate 100 focused checks pass.
[Locked study](evaluations/2026-10-14-short-continuity-study.md).
Full gates, matched studies, release/deployment and actual acceptance pending.

Candidate evidence: 100 focused checks, all six final feature gates, 1,071 tests,
96.87% coverage/31 typed modules/build. Corrected six causal pairs: first requests/drafts/
finals identical, requests 12 to six. General 8-context/2-sample cohort: 32 final outcomes,
28 posts/4 abstentions, no new control regression in manual review. Initial punctuation
mismatch did not exercise exact echo and is not counted as causal. Actual source-backed
same-owner-anchor handler baseline/candidate: memory checks 2 to 1, one accounted request
each, handler time 10,572/4,641ms; sequential one-pair timing is limited. Initial missing
native channel cache trial is excluded from grounding acceptance. Production heartbeat
verified after validation clients close; no second gateway/development learning/raw answer
artifact. Runtime merge/release/deployment and fresh normal gateway acceptance pending.

Delivered 2.24.2, PR109 head 5a367e9f24015597aa41006d901788b90d811c32,
merge 81f8e065e7a795a9caa77b4f0672481e4ceaeef0. PR CI38562915499/main CI38563150309/
image CI38563452233 success; all feature/merged gates1,071tests/96.87%/31typed/build.
Immutable [release](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.24.2)
index c75799ddee36c8804e96869590a1071dba5e828fbc99529692807fe26787c31b,
AMD64 0665af8508f24a0061215af5251e8286fe1103e3eaa1f7c603bede60cedfce38,
ARM64 404be40627e821ba66d094765b2232031d6d571a8b45f7a09ba25c6dcbb8308d.
Verified pi5/aarch64/Ubuntu24.04, existing locked transaction, all31sourcehashes/OCI
commit, healthy/Discordready/0restarts. Prior good2.24.1/c2553b4 retained, no rollback.

Six fresh normal gateway controls pass manual review: five posts/one recipient
abstention/eight provider requests. Short source-backed recall one call/no cosmetic
refresh, same four-word answer. Observed latency10,249ms to5,635ms is one pair with
changed history/cache, not a general benchmark. Shared care repair remains. Exact-date
uncertainty seven words retains two requests; the boundary is deliberately narrow.
Familiar comic premise/stock care wording, zero new abstract patterns and sparse current
spontaneous league activity remain limitations. No unsupported day/ordinary metadata
disclaimer, source/author/recipient regression observed. Short window has0errors/reply
failures/disconnects/study pauses,2startupSDKwarnings. Post-audit counts7target/12peer/
4olderbot/0currentspontaneous; no development learning or source expansion.

Run68settledrequests/USD0.009047595estimate (58maintenance/0.004649270,10runtime/
0.004398325); installed8requests/0.003330700. CoveredOctober0.235326595/1574attempts/
1unchangedpreexistingunsettled,18/2/20guard unchanged. Not billing; pre-guard unknown.
Six historical context windows/one export/42block occurrences with possible overlap are
mechanical source coverage, not independent semantic pattern evidence. Private exact
refs/metrics0700/0600,seven-daymanualretention/withdrawalcleanup,no raw answer artifact.
Candidateoverridesremovedbeforeinstalledtests; publicsyntheticreports/fullqualitylogs
preserved in automationstorage. EvidencePR only changes docs; runtime/test/version/
lock identical to released81f8e06. [Full result](evaluations/2026-10-14-short-continuity-release.json).


## 2026-10-14 09:00 - H62/H62a qualified abstract rollout

Both phases and locked criteria: [study](evaluations/2026-10-14-abstract-rollout-study.md).
New fetched-main managed worktree, base ad3c4e5, primary untouched; prior run complete.
Authenticated three-channel fourteen-day audit: 7 target/12 peer/4 older bot/0 current
spontaneous. Contextual private archive study: 21 windows/6 exports, 39 target/66 peer
block occurrences, current exact refs, unknown dates. Two distinct supports, a contrary
case and one independent unseen compatible episode justify a conditional tentative
candidate, not a universal human trait. Overlapping, sparse and missing-pixel windows
are excluded from independent quality evidence. Same Codex evaluator; no human review.

Selected preview validates all prospective graph writes under the source lock and
rolls back successful previews without changing beliefs or backups. Commit revalidates.
12 baseline regression failures; 13 candidate checks pass. Real-source disposable
lifecycle 9/9. Matched actual owner handlers: both arms 5/5, eight posts/two abstentions,
six maintenance requests each. Four candidate packets carry an abstraction with no
audit counts, four baseline packets do not. Baseline replies are already natural;
no broad quality/humor gain is measured. Candidate depth is longer, 44 words/two
sentences; firm/care/recipient controls pass. First temp clone exceeds16MB tmpfs;
owned private app-volume clones solve it and are erased, no production state change.

Next: qualified population and independent human held-outs/legacy review; specific
native semantic approval remains unresolved and no rejected transfer is retried;
emotional/semantic humor/cues; broader native/thread/pixels; selective skills/tools
and generated U.P. aurora/trail-camera scenes. Guard18/2/20, source/lifecycle/intake,
model/pacing/schedule/notifications remain. Candidate2.25.0 release/install acceptance
pending. Runtime change is operator preview; private population is a separately
validated deployment step, never public Git source or synthetic human evidence.


### H62/H62a final installed result

Deployed2.25.0/5f1e9cc8 after PR111/required CI/both images and merged full gates:
1,084 tests/96.88%/31modules. Actual CLI preview preserves graph bytes/status/backups;
commit adds one qualified tentative conditional value with two supports/one contrary/
30-day expiry and exact held-out provenance in protected graph state. Initial CLI parent
privacy rejection changes nothing; corrected owned 0700 parent passes. No old pattern
restoration, native gate expansion, new private retention exception or source replay.

Fresh normal gateway10/10,9posts/1abstention/11 runtime requests; seven zero-provider
actual-anchor packet checks pass, primary heartbeat survives close. Care stays stock,
semantic variation/general fidelity unmeasured; baseline already natural. Source counts
unchanged, graph1 value4 concepts1,034 edges. Post audit7 target12 peer4 older bot0 fresh across
three channels/latest100/14 days, zero observed errors/restarts/two startup warnings.
Run 28attempts/USD 0.009190225 estimate, coveredOctoberUSD 0.244516820/one unchanged
preexisting unsettled reservation. No billing/pre-guard visibility invented.

[Final study](evaluations/2026-10-14-abstract-rollout-study.md) and
[release/health/cost evidence](evaluations/2026-10-14-abstract-rollout-release.json).
Next independent qualified abstractions/legacy review, native semantic integration
when specifically approved, emotion/semantic humor/cues, broader native/pixels and
H61 selective tools/generated outdoor scenes. All standing invariants preserved.
