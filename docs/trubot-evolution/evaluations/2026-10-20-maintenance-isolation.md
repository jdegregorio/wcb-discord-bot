# H116: isolate maintenance-client readiness

Run: 2026-10-20 17:00 Pacific. Base
`8fb108149853f8b619ab1cc4e9a819504e5e50b2`. Origin/main was fetched successfully
before the new managed worktree and feature/trubot-daily-20261020-1700 branch.
Primary checkout untouched; no unfinished evolution PR. Three dependency PRs remain
separate. Existing app credentials and the existing maintenance ledger are reused.

## Prior run reconciliation

Automation memory still describes 2.38.6. Current main contains merged
[PR 177](https://github.com/jdegregorio/wcb-discord-bot/pull/177), revision
8fb108149853f8b619ab1cc4e9a819504e5e50b2. Its protected main CI 39490636692 and
image workflow 39490971397 pass, and immutable v2.38.7 is published and installed.
The prior chat ended in a system error before its completion notes were committed.
This run independently verifies the installed version and current gateway; it does
not invent missing prior acceptance results. H113 remains unqualified.

## Phase 1: audit and competing hypotheses

Pre audit: six authenticated ArchiveStore.context windows, plus 24 actual private
server posts (12 bot, 12 owner). Three latest-100 source-channel pages contain zero
seven-day Andrew posts and one bot post. Sparse bounded pages do not prove silence
or cover all direct/follow-up/reaction/ambient behavior. Model triage flags one
possible peculiar post and undercounts bot posts as 11. This is an unadjudicated
flag, not an established human mismatch. No source/pixel interpretation or new
human trait is populated. Small unmatched truncated cohorts and a single automated
reviewer cannot establish general character fidelity.

H114 emotional abstraction: a bounded gratitude/congratulation/apology search finds
eight attributed radius-one windows across four source digests. Complete text and
attribution are checked, including surrounding peer setup/reactions and contrary
contexts. Grouped blocks are not individual-message counts; archive dates remain
unknown. Context-specific greetings, jokes and acknowledgements do not by themselves
establish a recurring emotion mechanism. Proposed benefit is useful remembered
emotional context so replies respond warmly without a forced joke. Baseline live
celebration probe gives brief fitting warmth. No demonstrated deficit or qualified
new abstraction follows. Acceptance remains separated complete supports, contrary
episodes and held-out matched usefulness without invented motives or copied prose.
Insufficient recurrence, no gain or control regression disconfirms population.
Status: unresolved; no candidate is imported, no automatic native pattern gate opens.
Raw sources and derived personal observations stay outside public Git and receipts.
H105's rejected humor candidate stays retired. Historical/native/visual coverage,
seasonal variety and broader harness/model alternatives remain candidates requiring
utility evidence, not automatic reasons for adding context or infrastructure.

H116 lifecycle isolation: build_client passes configured ready_file to every client,
including maintenance evaluations. TruBotClient.close unlinks that file even when
the client never started a gateway. Four checked-in evaluator entry points use
production Settings directly. Their finally cleanup can erase the running bot's
heartbeat. A separate personality evaluator uses a fixed auxiliary path, so
concurrent runs can also clear each other's marker. Proposed mechanism: a unique
ephemeral readiness path selected before maintenance construction, so evaluation
cleanup cannot disrupt production health or confuse quality experiments.

Predeclared H116 acceptance: exact disposable live-heartbeat bytes/inode/nanosecond
mtime survive started/unstarted maintenance close and failed-study cleanup; two
simultaneous maintenance clients cannot clear one another; ordinary runtime cleanup
retains its configured semantics. Original Settings, source paths, usage ledger,
provider configuration and learning access must remain identical. No extra provider
or Discord I/O. Reproduce using the real build_client/close path with disposable
sentinels, never by deliberately removing production readiness. Installed acceptance
must then preserve the actual main heartbeat and receive a real owner/gateway reply
after all auxiliary clients close. Any live marker removal or changed runtime path
disconfirms this correction.

First test attempt has an incorrect SDK with_options mock, so its cleanup TypeError
is excluded. Corrected baseline: five failing isolation scenarios, one passing
runtime control. Candidate: all six scenarios pass; 14 focused app/health checks
pass. The installed 2.38.7 baseline independently erases only a disposable sentinel;
the actual main heartbeat remains present/ready. This is measured lifecycle behavior,
not measured character improvement.

Official [structured-output documentation](https://developers.openai.com/api/docs/guides/structured-outputs)
was fetched while assessing bounded reviews. Schema adherence cannot establish
semantic agreement with human evidence. This correction changes no API or model
configuration; prior Boolean-review contradictions remain a limitation.

## Phase 2: selected correction and roadmap

Select H116 as a supported enabling increment. Automatic builder isolation protects
all existing maintenance callers, including new callers that forget an environment
override. A fresh UUID path under the process temporary directory is chosen before
ReadinessFile and TruBotClient construction. dataclasses.replace preserves the
caller's Settings and every other configuration field. Each client removes only
its own ephemeral marker; there is no new durable store, cleanup job, service or
provider request. Normal runtime settings and heartbeat behavior are preserved.

Next independently qualify useful emotional/amplified-humor/original-view context;
then expand useful native/visual coverage and seasonal variety. H113 needs verified
full packets and causal matched gain. Keep rejected H105/broader H107/H110a retired,
H96 closed without a qualified feed and H102 secondary. Material privacy, grounding,
source-lifecycle or delivery failures change this order. Preserve generated Michigan
U.P. aurora/trail-camera themes, selective tools, four photo studies/day, existing
USD18 runtime/2 maintenance/20 total guard and six standalone local scheduled runs.

## Validation and release status

All six gates, protected PR/main CI, immutable release/image workflow, app-scoped
locked deployment and installed acceptance are required before completion. Rollback
is code-only to 2.38.7, preserving source, usage and paid-claim state. Private
content-free references and pass/fail metadata use app-volume
smoke-tests/2026-10-20-1700, 0700/0600, existing manual seven-day retention and
withdrawal cleanup. No raw excerpts, generated answers or derived personal
observations are stored in public notes or smoke receipts. Local QA scripts/logs
remain outside managed worktrees. Final completion evidence is appended below.


Feature gates pass: locked all-groups sync, formatting, lint, strict typing of45
modules,2,053tests/96.08%branch-inclusivecoverage and2.38.8sdist/wheel.
No failures or flakiness are accepted. No source or usage schema changes.
