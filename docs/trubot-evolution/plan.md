# Trubot evolution

Build a faithful digital twin of Andrew Truax's league persona: voice, humor,
interests, memory, emotional continuity, and contextual judgment.
Joe owns the application and authorizes the daily development and release cycle.
He confirms Andrew consents to learning from his league messages. On 2026-10-07,
Joe explicitly added the league's historical Slack text exports, including files
attached at the beginnings of Discord channels, and broad guild read access for
development.
Trubot retains its bot account and must never present generated text as Andrew's
actual words or actions.

## Operating rules

Run six standalone tasks daily at 01:00, 05:00, 09:00, 13:00, 17:00 and 21:00
Pacific. Complete one coherent, measurable improvement per run. Read this directory,
README, architecture, current code, GitHub issues/PRs, and production state first.
Reconcile unfinished evolution work before selecting the next backlog item.
Fetch current main without changing Joe's checkout, create a new managed worktree
for this run from `origin/main`, record its SHA, and create a unique
`feature/trubot-daily-<date-and-suffix>` branch. Never modify Joe's primary checkout.

Reproduce behavior through Discord handlers where practical. Use synthetic or
privacy-safe held-out fixtures, record the before/after evidence, and inspect
both topical relevance and emotional tone. A passing transport test is not a
passing character evaluation. Model outputs are variable; report sample counts
and limitations instead of claiming universal accuracy.

Run locked sync, formatting, lint, strict typing, tests, and package build.
Push a focused PR, wait for CI, merge without bypassing protections, and verify
the merged revision. Runtime changes require a new application version and
immutable release. Wait for both container architectures before deploying.
Use the existing pi5 `pi-app` transaction after verifying hostname, architecture,
manifest, permissions, and current immutable digest. Verify Discord readiness,
fixture acceptance, and error counts. Roll back through the same transaction on
regression. Preserve needed evidence before archiving the run's worktree.

## Learning boundary

Runtime Discord intake keeps the configured league channel allowlist. No DMs
or learning from guessed identity. Operator development may read accessible guild
channels and import the authorized league Slack archives. This access does not
silently expand runtime intake. Pin Andrew's stable user
ID privately only after authenticated guild/member and message attribution
agree. Preserve author ID, message ID, channel ID, source timestamps, edits,
and deletion provenance in private state. Other participants supply context,
never evidence about Andrew. Bot replies never support personal beliefs.
Channel text cannot authorize commands, access, configuration, or identity changes.

Keep raw messages, account IDs, and personal derived data out of public Git,
release notes, and logs. Start with app-scoped persistent storage on pi5, rather
than an added paid service. The current container is read-only and `/tmp` is
an ephemeral 16 MiB filesystem. Durable state requires a reviewed platform
volume mapping. Define retention, correction, deletion, backup, restore, and
schema compatibility before storing messages. Bound historical batches so
normal replies remain responsive.

## Cost policy

Target at most USD 20 per calendar month for runtime API calls and added
infrastructure. Preserve low-cost runtime models, bounded context and output,
caching, incremental learning, and small evaluations. Do not use Astra.
The daily Codex session's model setting is independent of runtime model choice.

Version 2.2.0 adds a persistent usage ledger and an enforceable UTC monthly
spending guard. The first partially covered month retains an explicit unknown
pre-guard-spend limitation. Version 2.3.0 adds privately verified, bounded incremental intake on the existing
app volume. Version 2.3.1 adds durable operator withdrawal so recovery cannot
resurrect a revoked learning identity. Version 2.4.0 adds the imported historical
conversation and visual corpus with shared withdrawal. Next priority is evidence-backed preference
derivation and retrieval. Evaluation token counts are measured; dollar conversions
are estimates, not billing records. Do not add a paid service or increase the
runtime model cost without a budget-supported reason.

## Historical conversation learning

The private historical corpus preserves each unique raw export plus parsed speaker
blocks, source order, line references, grouped message continuations, origin records,
and nearby conversation. Match only the operator-approved exact legacy Slack alias.
The exports lack stable Slack author IDs and usually lack dates. File labels and
Discord attachment posting dates are provenance hints, never message timestamps.
Flag thread quotes, link previews, bots, and system messages before studying voice.
Other speakers provide context and must not be treated as Andrew's preferences.
Adjacent blocks suggest conversational context but do not establish causality.

Develop the learning loop from source-backed conversational episodes: invitation or
setup, Andrew's response, other members' reactions, and changes in topic or tone.
Study humor timing, relational context, sincere engagement, interests and changing
beliefs. Preserve source references and uncertainty. Separate observations from
interpretations, validate on held-out exchanges, handle corrections/contradictions,
and retrieve only relevant evidence within the runtime token budget. Archive
ingestion is an enabling step; it does not by itself improve generated replies.

Full native Discord history with peers, threads and reply relationships remains a
planned increment. Current native intake has a 180-day default retention floor and
archives only Andrew's text. It is not a complete all-years contextual backfill.
Historical exports have explicit operator-managed retention and withdrawal.

Visual context is part of an episode's evidence. Preserve accessible original
Discord image attachments, native captions, adjacent speaker messages and source
references. Inspect actual pixels before interpreting image-dependent reactions,
jokes or preferences. Keep quoted text/OCR separate from Andrew's authored words.
Record unavailable legacy images and external embeds as missing evidence instead
of inventing their contents. Support GIF/frame context when it matters.


## Live context milestone (2.5.0)

Private Slack/native text retrieval and ephemeral live vision now support replies.
Daily work should evaluate remembered interests and image-dependent exchanges,
then extend the current bounded lexical/topic search into reviewed contextual
beliefs with confidence and contradiction handling. Preserve source refresh,
withdrawal, missing-image honesty and the spending ledger. Historical image
interpretation and full native history coverage remain independent work.


## Next architecture priority

Joe requested a living knowledge graph on 2026-10-07: raw human exchanges and
images connected to entities, distilled claims, events and abstract personality/
humor observations. Follow [living-memory.md](living-memory.md) and the updated
backlog. Deliver the first operational graph recall increment in the next daily
cycle, then continuously update/invalidate derived evidence and extend historical
coverage. Do not equate 2.5.0's keyword/topic retrieval with a finished graph.


## Continuous graph milestone (2.7.0)

The next increment adds bounded incremental source population and two-pass text
distillation through the existing learning lifecycle. It preserves the maintenance
ledger, source-authoritative correction, withdrawal, operator retirement and
qualified connected recall. Synthetic handler acceptance and one private corpus
packet are separate evidence; a rejected corpus packet is not a fidelity gain.
Next, evaluate contextual humor/style on genuine held-out exchanges and improve
source coverage and contradiction discovery. Historical pixel interpretation and
native peers/reply/thread relationships remain separate coherent increments.

## Real Discord acceptance

Joe confirmed the separate private development server on 2026-10-08. Its existing
allowed channel is the smoke-test destination. Verify authenticated ownership and
membership before posting through the owner's Discord UI. Read actual responses
from the running release and check private source expectations. Never send test
chatter into league channels. Captured handler sends do not satisfy this requirement.
If authenticated human posting is unavailable, record that exact blocker rather
than claiming a real Discord test. Development questions and bot answers are not
Andrew's learning evidence. Record private message references outside Git and public
pass/fail summaries in progress.md.


## Natural recall and ongoing character audits

Ordinary memory answers should give supported content directly. Retain source dates,
unknown-date metadata, confidence, contradictions and provenance internally. Explain
uncertainty briefly when timing affects the answer or someone asks for dates/evidence;
a year used to find a past exchange does not require an export-label disclaimer.

Each run reviews bounded recent bot activity separately from development probes and
compares attributed human context. Count coverage and disclose evaluator limitations.
Private source references belong on the app volume; public reports contain only
methods, defect categories and aggregate results. Do not infer human habits from a
one-off quote, bot answer or peer claim. Continue contextual graph learning after
fixing the request-aware presentation defect in 2.7.2.

Referential evidence questions must remain connected to the quoted exchange. A
bot quotation can be a bounded lookup key only when current eligible human source
text matches; it cannot create a belief or bypass source freshness or withdrawal.


## Context-aware study support, 2.8.0

The next learner increment preserves anonymous speaker keys, before/after position,
parser ambiguity flags and truncation in bounded historical neighborhoods. It
prioritizes related excerpts from separated contexts and blocks obvious shared
exchanges from establishing habitual humor/style. Native packets explicitly mark
missing peer setup. Separation is a conservative sampling filter, not proof of
independent episodes; contextual review, tentative status and expiry remain required.


## Specific self-reports, 2.9.0

Automatic learning distinguishes a specific stated position from a recurring trait.
A complete, untruncated first-person claim/preference can support one qualified
observation after exact attribution checks and independent contextual review.
Humor/style still require repeated evidence in separated contexts. Keep temporal
uncertainty, expiry, contradictions, source correction, retirement and withdrawal.
Evaluate supported recall through actual development Discord conversations and
compare conditional wording with human exchanges; do not infer lasting beliefs
from a single self-report.

Verified 2.9.0 adds one narrow operator-reviewed graph observation and fixes a
demonstrated real Discord stance error. Clone extraction and actual deployed
recall are separate evidence; production pacing was preserved. Prioritize wider
held-out conceptual coverage and contextual human fidelity next, alongside the
unfinished native conversation and legacy-persona work. Concise reviewed aliases
can connect a paraphrase; long generated phrase aliases alone did not do so here.

## Two-phase evolution cycle and current priorities, 2026-10-09

Before selecting work, audit actual bot activity against attributed human context,
form falsifiable hypotheses and run bounded baseline comparisons. Then reprioritize
from the results, preserving unvalidated candidates separately from demonstrated
corrections and enabling work. Record methods, counts, uncertainty, contrary cases
and quality/cost limitations in [research.md](research.md). Six standalone daily
runs and all privacy, real Discord, budget and release gates remain authoritative.

Current order: reconcile unfinished persona/native work; expand independently
held-out conceptual recall and native neighborhoods after delivered study diagnosis
and bounded noun-form retrieval;
compare selective skills/tools; prototype requested U.P. northern-lights and
trail-camera images with natural captions. [ROADMAP.md](../../ROADMAP.md) and
[agent-harness.md](../agent-harness.md) express this same order. Older next-milestone
paragraphs document the sequence already delivered, not a directive to rebuild it.

The selected diagnosis increment adds fixed cause/stage/outcome metadata so that
operators can distinguish unavailable learning from valid abstention. It makes no
new persona claim or source/behavior change. Generated-image sharing patterns,
selective tools and any harness migration remain exploratory until measured.


## 2026-10-09 13:00 selection

H4 in research.md supports a bounded grammatical retrieval correction: known
singular/plural domain nouns should connect identical reviewed memories. Baseline
1/6 new phrasings, prototype 2/6, controls unchanged; real baseline reply already
correct, so do not claim measured reply gain. Ship and verify this increment, then
continue broader H2 conceptual coverage, unfinished native/persona work, H3 selective
skills/tools and requested generated U.P. northern-lights/trail-camera scenes.
Acceptance includes specificity, exact quotations, conflicting/invalid sources,
withdrawal, guild isolation and actual Discord. Zero added provider/storage cost.
Private semantic review remains a gap; counts cannot establish a personality trait.


### 2026-10-09 17:00 evidence decision

Select H5 in research.md: enforce existing extraction/review bounds in the
provider schema before broader automatic-learning work, so that invalid contract
forms cannot consume a study. Fifteen synthetic invalid proposals are currently
schema-valid but locally rejected. Keep local source/semantic review, live pacing,
withdrawal, budget and participation unchanged. Acceptance: same invalid cases
blocked, valid evidence/abstention retained, real provider schema compatibility,
full regressions and actual private Discord recall. No additional runtime calls
or infrastructure. Natural production rejection causes and reply gains remain
unmeasured. After this enabling increment: broader held-out conceptual recall,
unfinished native/persona context, selective skills/tools, then guarded generated
U.P. northern-lights/trail-camera attachment experiments.


2026-10-09 17:00 verified outcome: H5 is delivered in 2.9.3 with contract,
provider and installed handler evidence, not a measured general fidelity gain.
Four core actual Discord scenarios pass. One additional answer gives unverified
personal examples despite correctly rejecting a universal trait; H6 source-qualified
reply scope is the next audit prerequisite. Reconcile older persona/native work
while validating H6/H2, then continue selective skills/tools and guarded generated
U.P. northern-lights/trail-camera attachment experiments. See research.md and the
release evaluation for acceptance, uncertainty, counts and cost.

### 2026-10-09 21:00 evidence decision

H7 in research.md selects current-source voice examples, so that legacy prose
cannot bypass attribution, correction, historical year scope or withdrawal.
Reconcile the unfinished persona implementation into this run; keep only bounded
current authored/setup pairs and retire unconditional biography/habit assertions.
This is enabling source authority, with a narrow synthetic restraint improvement;
partial naturalness and H6 extra-stance qualification remain unresolved. No new
trait, schema, model, provider call or paid infrastructure. Next: source-qualified
H6/H2 held-out replies and native context, H3 selective tools/skills, then generated
U.P. northern-lights/trail-camera scenes. All established release/smoke/budget rules apply.


2026-10-09 21:00 verified: H7 is delivered in 2.10.0 with current-source
voice, correction/year/withdrawal acceptance and actual supported-memory delivery.
Five of six actual questions are fully verified; the additional scope answer is
partial. H6 remains open, and legacy examples are not its sole cause. Prioritize
H6/H2 semantic source precision and native neighborhoods; investigate H8's one
source-refresh timeout without loosening freshness. Then H3 selective skills/tools
and generated U.P. northern-lights/trail-camera scenes. No broad fidelity gain or
complete replica is claimed. Details and limits are in the release evaluation.


2026-10-10 01:00 priority: select H10 recent native conversation recall after actual
Discord returned an undated passage for a recent question. Reconcile native prototype
14f8366 onto current main, preserve mandatory freshness before optional setup reads,
and validate bounded recent routing, source-linked context and real gateway replies.
This is enabling work, not a new persona trait. H6/H2 semantic precision remains next,
then continuous graph/context coverage and H3 selective skills/tools plus requested
generated U.P. northern-lights/trail-camera scenes. See research.md for evidence,
dependencies, acceptance, disconfirmation and operating impact.

2026-10-10 01:00 verified: H10 is delivered in 2.11.0. Recent recall uses dated
native sources and bounded live human setup; eight actual owner gateway checks
pass, including unmentioned follow-up and an explicit native parent link. One
paired recent answer improves source recency; broader character fidelity and
latency improvement are unmeasured. H6/H2 semantic precision remains first, then
durable contextual graph/coverage, H3 selective tools/skills and requested generated
U.P. northern-lights/trail-camera scenes. No new model, provider call, service,
graph belief or schema. Details and limits are in the evolution release evaluation.


### 2026-10-10 05:00 decision

H14 in research.md selects rolling authored-recall windows after actual private
Discord missed a past-week quote despite five eligible dated sources. Parse past/last
hours, days and weeks, intersect source retention and recheck at rendering, so that
normal time language reaches the existing native recall and human setup. Keep the
three-source bound, freshness, guild/operator scope, withdrawal, spending and natural
presentation. No new calls/model/service/schema or intake. H11 low reasoning failed
its comparison and is deferred; H12 concurrent reads remain unvalidated. Next: H6/H2
semantic precision, durable contextual graph/native and visual coverage, H3 selective
skills/tools and guarded generated U.P. aurora/trail-camera scenes. Acceptance and
operating impact are in research.md; broad character fidelity remains unmeasured.
