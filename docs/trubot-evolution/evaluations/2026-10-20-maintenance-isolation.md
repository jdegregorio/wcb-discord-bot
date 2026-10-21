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


## Installed completion

[Runtime PR178](https://github.com/jdegregorio/wcb-discord-bot/pull/178) is merged
through protection as `cb9dbba6635a2af851da5986f3506d1ed2d45b4d`.
Feature CI39519893797, main CI39520185050 and image CI39520404371 all pass.
All six gates also pass on merged runtime:2,053tests,96.08%branch-inclusivecoverage,
45typedmodules and2.38.8sdist/wheel.
[Immutable release](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.38.8).

Verified pi5/aarch64/Ubuntu24.04 and current app manifest before the existing
non-sudo locked pi-app transaction. Running immutable index
`sha256:bf7c4adf8fae4949d2c7bcb67d35aa0124eccdb1eb26947bc8b35de84a10a80e`; ARM64 `sha256:4708aa106431ce616ad0583bedb5abad0a35452dac486d6270f88c0652d4bfde`;
AMD64 `sha256:8f7f22b64cd19a4c4ea170c2573ffd07498f0c08642e30c3a994b53d6a7e29d1`. All45installed source hashes and version
match the tested merge. Previous2.38.7/index
`sha256:1ed6c21b9de20af5511b956bc49c644337681e2d6242fd71bfce26174139c16a`
is retained for rollback. No source, usage or paid-claim restoration.

Installed lifecycle acceptance passes: a disposable heartbeat survives maintenance
construction/close, original settings stay identical, two maintenance clients have
distinct paths, closing one preserves the other, both own markers are removed,
and the real main heartbeat remains ready after all closures. Zero provider calls,
Discord writes or additional gateway sessions in that lifecycle acceptance.

Actual owner/gateway cohort in the reverified two-member development server:
12requests,11answers and one correct other-recipient abstention. Fictional humor,
requested new comic idea, hypothetical care, celebration, supported particular
preference, natural broad-memory wording and exact-date honesty pass. Five fresh
authenticated human sources support the particular preference; no new belief or
strength is inferred. Broad-year full content/calendar grounding remains unresolved:
that control tests wording only. Current public context, initial location
clarification and bare-location completed-night read pass. The returned regional
content agrees with fresh reports and does not invent a sighting. Twelve explicit
semantic review flags pass; single-model review remains fallible.

The final actual main-gateway probe is sent after all auxiliary clients close and
answers in2.353seconds. No Discord client is constructed afterwards. Later evidence
uses only stateless Bot REST, health/files and ledger reads. Installed reply
latencies2.345-12.045seconds,median4.595; no performance gain is claimed. The one
pre-release celebration probe also received fitting brief warmth. These controls
are not spontaneous league engagement or Andrew learning evidence.

Post audit repeats six human windows and24development posts (12bot/12owner), with
the same sparse three-page league census. Triage flags two possible peculiar posts
and three third-person references, versus one possible peculiar flag before. Those
aggregate labels do not identify a self-narration defect; requested fictional
subjects also use third person. Direct inspection of the smoke replies and their
case review does not establish a new meaningful character mismatch. Keep the
unassigned triage discrepancy unresolved rather than selecting another persona
change or claiming a gain. Both cohorts are small, unmatched, partly truncated and
reviewed by one model; pre audit also undercounts bot posts. The separate review of
the one actual league post flags zero peculiar/mechanical/unsupported-personal or
timing issues, still insufficient for a general character comparison.

Two authenticated human held-outs are separated from the audit, eight new study
anchors and static examples. Four generated answers pass natural brevity,
contextual fit and factual restraint. Each pair has identical initial provider
request hashes across baseline/release. The correction changes readiness only;
these stochastic no-op controls show no causal character benefit. They are captured
responses, not actual gateway tests, and do not qualify a human abstraction.

Graph unchanged:553episodes,438human-source nodes,24native contexts,28dependencies,
1,071edges,one value,one preference,two claims;one accepted/three rejected studies.
No new human trait, graph population or native automatic-pattern permission.
H116 is supported enabling reliability work. H114 usefulness and the unassigned
triage discrepancy remain research; full native/visual history stays incomplete.

Final observed health at2026-10-21T00:24:42.577724+00:00:healthy,Discord-ready,read-only,zero
restarts/OOM/errors/reply failures/unhandled exceptions/source-continuity warnings
or private-source discards. One normal quality repair and one declined follow-up
are recorded. Timer remains active/enabled. No rollback was required.

Covered run window:27settled attempts (10maintenance/USD0.002078505,
17runtime/USD0.009981815),totalUSD0.012060320. CoveredOctoberUSD1.318135295,
estimates rather than provider billing; pre-guard spending remains unknown.
Six old unresolved reservations (one pending/five uncertain),zero new. Existing
18runtime/2maintenance/20total guard, four photo studies/day and no paid infrastructure.

Fourteen private content-free JSON receipts pass0700directory/0600file and forbidden
raw-key checks; a fifteenth receipt records that verification. Existing manual
seven-day retention and withdrawal cleanup apply. No source excerpts, generated
answers, personal derivations or screenshots are persisted in smoke artifacts.
A local receipt collector initially used the preceding run's QA directory; current
receipts are moved to the correct run and11prior app-volume receipts restore the
prior copies. No production source/state changed. Local QA evidence stays in
/private/tmp/trubot-20261020-1700 outside the managed worktree, with private modes.
Final documentation PR/CI and managed-worktree cleanup are recorded in automation
memory. Primary checkout untouched.
