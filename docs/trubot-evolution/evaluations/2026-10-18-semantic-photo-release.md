# Semantic source-photo delivery, 2026-10-18 13:00 Pacific

## Isolation and reconciliation

Fresh fetched base: cb982e9f02ff6c9e7c3331c84bf0186dacd21cef.
New managed worktree: trubot-20261018-1300/wcb-discord-bot.
Branch: feature/trubot-daily-20261018-1300-reconcile. Primary checkout untouched.
The prior H98d/PR156 stopped before release, with one uncommitted recipient
correction. Copy its reviewed implementation and correction into this worktree;
this run completes H98d rather than starting overlapping behavior. H99/PR157 is
separate enabling coverage work and remains a draft pending this release.

## Phase 1: research and acceptance before the final experiment

Production 2.34.0 is healthy on verified pi5/aarch64/Ubuntu24.04.4. A fresh actual
owner/gateway catch-up request and its indirect show-photo follow-up reproduce
text-only delivery: the bot claims to show a picture but sends zero attachments.
Earlier actual owner conversation independently demonstrates the same defect.
The deployed responder has no source-photo delivery action; first-person visual
recall and source-reference generation already exist and are not reimplemented.

Fresh authenticated census: latest100 messages in each of3existing source-guild
channels, zero pinned-human or bot messages within7days. Controlled development
conversation is separate:16posts,9bot posts. Four separated attributed human
archive windows are supplied using ArchiveStore.context with digest/ordinal/line
references retained privately. One maintenance model triage flags3peculiar and
4possible overreach posts,0third-person or mechanical-gap posts; it explicitly
finds the cohorts insufficient for a general human character comparison. These
counts are screening signals, not verified semantic scores. Small unmatched,
truncated cohorts, operator selection, single model and no blinded human evaluator
limit inference. No new persona trait or memory observation is inferred.

- H98d1: make an original-photo action available to the existing model so that
  indirect conversational requests can produce the actual image rather than a
  description. Baseline: actual zero-attachment follow-up and absent action.
  Mechanism: model chooses a bounded descriptive query; fresh private retrieval
  supplies source pixels before caption continuation; handler publishes bytes.
  Accept3different requests selecting the correct image, actual installed follow-up
  attachment with inspected source pixels, brief first-person caption, and date,
  refusal, care and reasoning controls without an image. Disconfirm on missing or
  unrelated attachments, fabricated ownership/date, phrase-dependent routing or
  ungrounded caption. Existing source/date/withdrawal checks stay authoritative.
- H98d2: prioritize the current recipient before action selection so that an older
  invitation cannot cause an image response to another person's request. Earlier
  contrary probe failed this control before the recovered correction; two final
  contrary probes passed after it. Accept no tool and no reply for the held-out
  explicit-other-recipient case; reject if an actual gateway case responds.
  This is a correction to model guidance, not an inferred human trait.
- H98d3: freeze attachment signatures and preserve deletion tombstones before an
  asynchronous capture so that corrected or deleted source photos cannot survive
  a download/import race. Earlier2regressions fail on2.34.0. Accept both fixed
  races and existing edit/delete/withdrawal/access regression suite. No behavior
  gain is inferred from ingestion alone.

Alternative H99 older-photo recovery has concrete omitted-source evidence but
cannot fix the reproduced delivery defect. H92 abstract/emotional/amplified-humor
utility remains a higher-level research need with insufficient independent held-out
qualification. H96 local confirmation remains inaccessible/unvalidated; no automatic
event publishing. Do not ship another unsupported persona or date prompt patch.

Current official documentation confirms function-call outputs and continuation;
this implementation keeps store=False, one action and one continuation on Luna.
The project separately tests actual pixels and actual attachments; documentation
alone is not proof of quality. [Function calling](https://developers.openai.com/api/docs/guides/function-calling#handling-function-calls).

## Phase 2: decision and next increments

Finish H98d now because the actual user-facing failure and mechanism are reproduced.
It is a supported capability correction, not a claim of improved general character.
Dependency: original source retrieval, approved owner-only development scope and
existing18runtime/2maintenance/20total ledger. Confidence in diagnosis high;
general semantic intent reliability and naturalness remain limited by small samples.
At most one extra provider continuation per chosen action; no new service/model,
spending pool, intake scope or gateway test learner.

Then integrate H99/PR157: resumable operator-only older original-photo recovery,
so omitted shared views can inform future qualified composition. Its21local tests
and two privately inspected omitted sources support enabling work, not reply gain.
Rebase after2.35.0, rerun all gates, validate installed bounded recovery and real
Discord use; retain actual oversized/media/denied gaps. Operating impact: bounded
operator reads, existing capture/maintenance caps; no automatic bulk backfill.

Next H92/H93: independently qualify abstract/emotional/amplified-humor and original
view composition, so source-backed concepts guide varied natural engagement.
Require separate attributed support/contrary episodes, held-out contexts and actual
private gateway controls. Confidence unresolved; same bounded maintenance ledger.
Then seasonal timing/caption variety needs longitudinal natural opportunities and
sensitive-context restraint; no general engagement gain yet. H96 requires a fresh
accessible location/time-bound positive/negative observation source before opening
aurora publishing. H97 remains unresolved until actual context can reproduce its
clarification failure. Material privacy/grounding/ordinary-reply regressions reorder
these priorities. Preserve generated U.P./trail-camera direction, bot identity,
six standalone runs and configured model, schedule and notification preferences.

## Validation

Focused52photo/action/lifecycle cases pass. The focused invocation alone misses the
repository-wide90%coverage threshold; full required suite supplies release coverage.
A test harness membership-count assertion and development-channel census assertion
failed before provider I/O and were corrected. One settled positive provider case
lost its receipt because the new directory was missing; the directory was then
initialized and the final experiment rerun. No ledger reset or duplicate Discord
request. Final provider comparison, full six gates, CI, immutable release/image,
installed source hashes, real owner/gateway acceptance and post audit follow below.


### Contrary experiment and correction

First final8case comparison:7/8pass. Three visual requests queue originals; date,
refusal, care and other-recipient controls avoid photos, and recipient returns no
reply. The text-only reasoning case incorrectly queues a photo. Do not count this
as passing. Correct action guidance to honor the current requested response format
and distinguish understanding a point from viewing its photograph. No phrase
classifier or new persona assumption. Repeat the same8cases plus separately worded
modality/recipient controls before release; any failure remains visible.

Final same8intent cases:8/8pass after modality correction, using one freshly loaded
canonical source packet returned by the action and fresh canonical source checks.
This deliberately isolates model intent from dynamic query/ranking changes; it is
not a full arbitrary-query retrieval score.3visual positives queue the original,
5negative controls do not, and other-recipient returns no reply. Captions12-14words
in these positives. An earlier fully integrated retake posts one successful result
then stops safely on a changed/unavailable broad source packet before provider
continuation; this unresolved availability limitation is not hidden. Only its
single proven zero-provider-call reservation is settled to zero from the captured
traceback/time window; the2old uncertain reservations remain intact.

All six final feature gates pass: locked sync,format,lint,41typed modules,
1,830tests/96.10%branch-inclusivecoverage and2.35.0source/wheel build. Broad semantic
and naturalness reliability remain unmeasured; real installed acceptance pending.


### Release and initial installed acceptance

Four additional new-wording controls pass4/4with the same isolated intent protocol:
2visual requests queue originals, text-only evidence and other-recipient controls
queue none; the latter returns no reply. This supports bounded intent capability,
not arbitrary-query retrieval reliability or independently measured human fidelity.

PR158head9529080eac4c348be5058713570bee5151012be3 passes Quality39161832322.
Ordinary squash merge041d529990fc5d9be6ae3d919b9089fab08876bf exactly equals the
tested tree. All six merged gates pass again:1,830tests/96.10%,41typed modules,
locked sync/format/lint/build. MainQuality39162007529 passes. New immutable
[v2.35.0](https://github.com/jdegregorio/wcb-discord-bot/releases/tag/v2.35.0)
and multiarchitecture ImageCI39162276560 pass for the same commit.

Scoped pi-app deployment succeeds on freshly reverified pi5/aarch64/Ubuntu24.04.4,
index71579343cde118f3f3714cf18414bc1d7385331507897acdad3cb044bbf5aa44.
All41installed Python hashes match, revision041d529, read-only root, healthy Discord
readiness,0restarts. Previous2.34.0/index48a89f3a13623dc54374b469fd6be20012a03f62a852b9f8b63f5ee2f5346de3
is retained by the existing locked transaction. No state restore,new service,
permission bypass,sudo or unrelated-app mutation. The release timer remains active/
enabled. An early hash read occurred while the transaction still ran2.34.0;
repeating after transaction completion matches the correct release, not a rollback.

Actual authenticated owner/gateway same catch-up request:1source JPEG/17.222s.
Exact unmentioned show-photo follow-up:1source JPEG/19.844s versus baseline zero
attachments/7.930s. Both257,703byte delivered images match the privately inspected
normalized source frame exactly. This is actual source delivery, not a generated
substitute, and pixels were inspected. Hashes/message references remain private.
Two corresponding baseline text requests had zero attachments,6.137s/7.930s.
The live captions are brief and first-person; wording repeats a previous closing
phrase, so do not claim varied character voice. Latency increases in these two
observations; no population latency estimate is inferred.

Initial installed negatives pass: text-only reasoning3.627s/no attachment,
explicit-other-recipient no reply confirmed in UI and handler decline, exact date
briefly unknown with no invented date/photo, explicit refusal describes visible
content without attaching, and care stays considerate with no photo. Ordinary
baseball recall stays direct and supported without stock source/date boilerplate.
Further controls, final post audit, ledger and client-close sanity follow.


### Final installed controls, audit and cost

13actual controlled owner/gateway scenarios pass their functional checks:
3source-photo deliveries,9text replies and1recipient abstention. All3attachments
match the inspected normalized source pixels. Third-photo latency19.662s.
The final current-conditions request succeeds4.140s after every secondary client
closes, without a photo; no later Discord client is constructed. Its content-free
references/timestamps come from authenticated browser DOM. Heartbeat remains healthy,
read-only,0restarts. Source hash verification itself imports no Discord client.

Semantic quality remains qualified: one photo caption assigns an unverified
function to a visible object and narrates more than requested. Record visual
grounding/response-format quality as partial, not a perfect-caption result.
Broad historical recall is natural and avoids stock date boilerplate, but its
specific2020relevance is unproven. Invited fictional humor remains brief and care
is considerate; neither establishes a humor multiplier or human character gain.
H98d1supports source delivery and limited intent discrimination; full caption-quality
acceptance remains unresolved. H98d2's tested recipient abstention and H98d3's
reproduced lifecycle regressions are supported within their stated coverage.

Post audit repeats4attributed human windows with16recent development posts/9bot
posts:0peculiar/1possible-overreach flag,0third-person/metadata-gap flags. Both pre
and post model triages explicitly find the human comparison insufficient. Cohorts
differ, source windows are truncated and one unblinded model screens both; the
count change is not causal character improvement. Manual actual-pixel/caption review
finds the unverified-detail partial above. Three source channels/latest100 each
again contain0seven-day target/bot posts. No recent spontaneous direct, follow-up,
reaction or ambient comparison is available. Development prose never becomes human
learning evidence. No new human trait or graph observation is introduced.

Final observed covered-run ledger:58settled records,estimated USD0.028396320,
runtime USD0.011972360 andmaintenance USD0.016423960. One record is the proven
zero-provider source check. Covered October2,562records/USD1.030795415estimate;
2unchanged old unsettled,0new. Same18/2/20guard, no new pool/service,not billing;
pre-guard spend remains unknown. No image generation charge in this run.

Content-free private receipts remain in the existing app-scoped smoke-tests
directory for this run under0700/0600 and its existing manual7day retention/
withdrawal cleanup. Local preserved receipts/logs are outside the worktree.
No raw source excerpts or derived answer text enters those receipts or public Git.
Temporary normalized source/delivered-pixel copies are removed after hash comparison;
canonical authorized source storage remains governed by existing lifecycle controls.

Five-minute baseline and post snapshots each show0errors/discards/unhandled
failures, with unequal activity exposure; this is no formal error-rate comparison.
The final whole-installed window and closeout evidence are recorded with this run.
No rollback is required. PR156is superseded/closed; H99/PR157remains a separate draft
requiring rebase,all gates and installed recovery/real Discord qualification.
Prioritize independent source/pixel caption calibration with abstract/emotional/
amplified-humor utility after that enabling recovery; no unsupported trait promotion.
If source-refresh availability repeats under normal traffic, investigate it before
expanding memory scope. Keep H96confirmation closed and H97clarification unresolved.
