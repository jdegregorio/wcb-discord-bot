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
