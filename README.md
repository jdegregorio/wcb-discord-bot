## Case-level character audits, 2.38.9

Private operator audits assign fixed triage flags to every sampled bot turn and
derive counts locally. Missing cases, extra fields, non-Boolean flags, changed
sources and oversized complete context stop the review. Authenticated channel
reads retain runtime allowlists and the two-member development-server boundary.
This enables inspectable character research; model triage does not establish
human fidelity or alter normal replies.
[Method and validation](docs/trubot-evolution/evaluations/2026-10-20-case-audits.md).

## Isolated maintenance readiness, 2.38.8

Maintenance clients automatically receive a unique ephemeral heartbeat before
construction, so closing an evaluation cannot clear the live bot's readiness or
another study's marker. Existing source, generation and spending settings remain
identical. Runtime heartbeat behavior is unchanged. This is a reliability correction
for safe character research, with no measured reply-quality gain.
[Evidence](docs/trubot-evolution/evaluations/2026-10-20-maintenance-isolation.md).

## Reply-context diagnostics,2.38.7

Runtime emits fixed states and aggregate counts for memory verification/assembly,
selected context routes and photo-action availability. It retains no private text,
source IDs, tool arguments or pixels and changes no model request or behavior.
Existing rotated app logs only; no provider call, schema or service is added.
These events enable valid character-quality research; they do not prove reply
quality or publication. [Evidence](docs/trubot-evolution/evaluations/2026-10-20-context-diagnostics.md).

## Complete a location clarification (2.38.6)

After Trubot asks where for an unlocated last-night sky or northern-lights question,
answer `Marquette.`, `Munising.` or `The Keweenaw.`. The same requester can complete
that immediate question using the existing fresh NOAA/NWS read. Unrelated,
interrupted and already located questions keep their existing behavior.
[Qualification and limitations](docs/trubot-evolution/evaluations/2026-10-20-location-clarification.md).

## Requested fresh jokes (2.38.5)

An explicit request such as `Give me a different joke about that same scene` can
refresh an unchanged substantial punchline from the immediately preceding bot turn.
This uses the existing maximum one accounted repair and source freshness checks.
Requested quotations, reference wording, short factual continuity and ambiguous
requests retain their previous treatment. No semantic-novelty or funniness guarantee;
failed repairs keep the initial draft. Model, learning and participation are unchanged.
[Study](docs/trubot-evolution/evaluations/2026-10-20-requested-novelty.md).

## Fresh public context in follow-ups (2.38.4)

During an active conversation, a complete follow-up such as `And check current
Munising sky conditions now?` can use the same NOAA/NWS tools as a summoned question.
Complete last-night questions and location clarification also retain their routes.
A fresh read supplies the answer; an older bot answer is not current evidence.
Short ambiguous follow-ups still lack contextual tool selection.
[Validation](docs/trubot-evolution/evaluations/2026-10-20-explicit-context-followups.md).

## Direct conversational replies (2.38.3)

Ordinary replies shed an accidental outer dialogue quotation, so humor and care
appear as direct speech. Quoted framing also cannot hide a long answer or an old
bot echo from the existing bounded quality check. Requested quotations, original
captions and embedded quoted excerpts retain their wording and punctuation.
There is still at most one optional quality repair, with the same source and
spending checks. No new human trait or general humor improvement is claimed.
[Study](docs/trubot-evolution/evaluations/2026-10-19-abstract-banter-study.md) and
[installed validation](docs/trubot-evolution/evaluations/2026-10-19-dialogue-release.md).

## Text follow-ups to shown source photos (2.38.2)

After Trubot shows an indexed original, ask about its original caption, visible
scene or timing. A separate read-only action inspects that same verified source
without attaching it again. Discord Reply selects a particular shown photo;
otherwise the latest original shown to you in the channel is selected.

Current-focus capability context prevents an earlier missing-caption answer from
hiding an available source. Requests about another speaker's own history do not
receive character-photo inspection.

Links last six hours and survive bot restart. Missing, corrected, deleted or
inaccessible sources stay unavailable. Bot captions never become human evidence,
and a posting date never establishes when the camera took the picture. Existing
allowlists, owner-only development access and the USD20 guard still apply.
Older sends and the legacy native-text photo fallback have no new source link.
[Validation](docs/trubot-evolution/evaluations/2026-10-19-photo-continuity.md).

## Conversational source photos (2.35.0)

Ask to see a recalled photo, including a short follow-up such as `Can I see?`.
The model can retrieve the original, inspect its pixels and attach it with a short
caption. Current source, requester, channel access and withdrawal checks apply.
Missing photos remain unavailable. This does not create another source photograph
or infer an exact capture date. [Validation](docs/trubot-evolution/evaluations/2026-10-18-semantic-photo-release.md).

# Last-night U.P. context (2.32.0)

Ask directly, for example: `🤖 Were Marquette conditions favorable for northern
lights last night?` Trubot can read bounded NOAA/NWS observations for Marquette,
Munising and the Keweenaw at any hour after the local night ends. Questions without
a location receive a brief clarification. These sampled observations can support a
possible viewing window, never establish a witnessed sighting. Missing data remains
unknown. Current conditions retain their existing route, and no picture is generated.
See [the study](docs/trubot-evolution/evaluations/2026-10-17-completed-night-study.md).

# Trubot

## Quiet outdoor check-ins (2.33.0)

Trubot can wake privately, read the public NOAA aurora forecast, and choose when to
check again without posting. A bounded planning turn chooses 20 minutes to 8 hours;
rapid checks require fresh promising nighttime activity. Restarts preserve the plan,
missed wakes do not replay, and most checks produce no Discord message.

Occasional generated U.P. scenes cover trail-camera deer, autumn wood preparation,
small-lake freeze and spring thaw. Seasonal attempts are limited to one per rolling
seven days, after an initial quiet week, between 09:00 and 21:00 America/Detroit. Quiet
time, existing shared cooldown/caps, sensitive conversation, current permissions
and withdrawal still gate images. Generated origin stays visible. No actual Andrew
activity, wildlife sighting or current ice condition is implied.

Initialize `trubot-outdoors init` once on the private app volume. The existing
`TRUBOT_AURORA_CHANNEL_ID` opt-in/destination is retained; its store directory now
also holds `outdoors.sqlite3`. `trubot-outdoors status` reports the next wake and
content-free outcome counts. Missing state fails closed. The same USD 20 monthly guard applies.

Automatic aurora pictures now require confirmed local visibility and remain closed
until a fresh accessible observation source passes validation. The local camera
endpoint returned403. Forecasts only change private wake timing; they never confirm
a sighting. This supersedes the older opportunity-only morning feature below.
Explicit requested aurora scenes still work. New complete requests also work, such
as `🤖 Generate a woodpile picture in the UP.` or `🤖 Generate a trail-camera image
in the Upper Peninsula.` The existing requested-image transaction/caps apply.

[Evidence and limitations](docs/trubot-evolution/evaluations/2026-10-18-outdoor-checkins-release.md).

## Requested U.P. aurora scenes (2.31.0)

Ask directly, for example: `🤖 Generate an original northern-lights picture over
Lake Superior near Marquette.` Trubot can create one generated scene near Marquette,
Munising or the Keweenaw, with a short caption and clear generated-origin label.
This is an imagined illustration. It does not establish a sighting or photo ownership.
The first skill accepts simple complete scene requests; edits, reference photos,
extra subjects and unsupported modifiers continue through ordinary conversation.

Initialize private operational state once with `trubot-scenes init`. It lives beside
learning state as `requested-scenes.sqlite3`. Missing/unsafe state prevents image calls.
Requests share a ten-minute global cooldown, three requested attempts per UTC day and
the existing monthly spending guard. Duplicate, failed or ambiguous requests never
regenerate automatically. Existing scheduled mornings retain their own timing rules.
See [the study](docs/trubot-evolution/evaluations/2026-10-17-requested-scenes-study.md)
and [operations](docs/trubot-evolution/storage.md).

## Selective current U.P. context (2.30.0)

Ask Trubot directly to check current sky conditions or northern-lights activity near
Marquette, Munising or the Keweenaw. A small read-only skill can gather fresh NOAA/NWS
observations before answering. Missing or stale reports stay unknown; these are
observations, not guaranteed sightings or forecasts. Ordinary conversation loads no
extra tool context. No new service, credential or spending allowance is needed.
See the [study](docs/trubot-evolution/evaluations/2026-10-17-context-tools-study.md).

## Historical U.P. aurora mornings (2.29.1, superseded)

In2.33.0 the quiet outdoor planner above replaces automatic opportunity-only
publishing. The following describes the earlier capability for release history.

An opt-in scheduled visual skill checks the previous night's observed NOAA activity
and NWS local sky conditions. After a suitable night it can share one original
generated Lake Superior aurora scene between 08:00 and 11:00 America/Detroit. It checks
conversation timing, quiet time and shared post caps/cooldowns, and preserves a
restart-safe one-attempt claim. Generated scenes are clearly labeled; conditions
indicate a viewing opportunity, not a confirmed sighting or a real photograph.

Initialize private state with `trubot-aurora init`, then set
`TRUBOT_AURORA_CHANNEL_ID` to an already allowed source-guild text channel.
Default 0 disables the feature. `TRUBOT_AURORA_STORE_PATH` defaults to
`/var/lib/trubot/aurora.sqlite3`. NOAA/NWS reads use no paid service. Fixed GPT Image2
medium 1536x1024 generation shares the existing monthly spending ledger; the first
actual preview cost USD 0.04172. See the [study](docs/trubot-evolution/evaluations/2026-10-17-aurora-feature-study.md)
and [storage/operations](docs/trubot-evolution/storage.md).

## Fresh source media continuity (2.28.1)

Mandatory fresh native source reads preserve media-presence warnings even when an
optional neighborhood read times out. Supported drafts no longer depend on that
metadata arriving through a second read. Changed media presence and substantive
human setup still stop publication. Source-only metadata remains ephemeral and
cannot become a captured learning episode. No extra Discord/provider request.
See the [study](docs/trubot-evolution/evaluations/2026-10-17-source-media-stability-study.md).

## Fresh native learning context (2.28.0)

Native memory studies now supply existing freshly checked human setup to both
extraction and independent review. Anonymous speakers, retained reply links and
honest coverage gaps help distinguish literal statements from quoted or fictional
speech. Peer context never becomes authored support; raw peer text stays ephemeral.
Automatic native personality-pattern learning remains closed.
See the [study](docs/trubot-evolution/evaluations/2026-10-17-native-study-setup.md).

## Explicit reply memory continuity (2.27.6)

A topic-free question sent with Discord Reply now uses the selected human message
as its memory search subject. An unrelated newer exchange cannot replace that
subject. Complete bounded text is required; bot, unavailable and image-dependent
references cannot supply it. This supplies context to existing verified retrieval,
without learning a new preference or adding a provider call.
See the [study](docs/trubot-evolution/evaluations/2026-10-16-reference-memory-study.md).

Trubot is the Will Carter Bowl League of Champions' dry, deadpan, oddly sincere,
Thomas-Jones-obsessed Discord character. Attributed league conversations,
contextual voice examples and bounded source-backed memory enrich that voice.

Version 2 is a ground-up rewrite. It has one job—make Trubot feel like Trubot—
and deliberately has no commands, Trello integration, or `!insultjim` feature.

## Channel behavior

Trubot only operates in configured channels.

- **Direct:** Mention Trubot, include 🤖, or reply to one of his messages and he
  posts immediately in the channel using the latest channel context.
- **Follow-up:** For ten minutes after an explicit summon, Trubot pays attention
  to that channel. He answers an unmentioned message only when the conversation
  makes it clear that it is meant for him.
- **Reaction:** Add the custom `ThomasJones` reaction or 🍆 to a message and he
  posts his take on that message in context.
- **Ambient:** After at least two people talk within one hour, Trubot may join
  after ten quiet minutes. Ambient replies are limited to one every two hours
  and three per UTC day, per channel.
- **Restraint:** A direct or reaction reply cancels pending ambient chatter and
  starts its cooldown, but never consumes the ambient daily quota.

All timing, limits, channel IDs, and reaction names are configurable. Participation
state is in memory: a restart resets ambient counters, attention windows,
and pending timers, while Discord remains the source of recent conversation
context. Responses are normal channel posts rather than Discord reply references.

## OpenAI integration

The bot uses the [OpenAI Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
through the async Python SDK. The production defaults are explicit:

- model: [`gpt-6-luna`](https://developers.openai.com/api/docs/models/gpt-6-luna)
- processing tier: `default` (standard)
- reasoning effort: `none` for explicit/ambient replies, `low` for inferred follow-ups
- text verbosity: `low`
- response storage: disabled
- token ceiling: 180 for explicit/ambient replies; 512 for inferred follow-ups, including reasoning

The prompt combines emotional and contextual judgment with curated, authentic
league exchanges. Channel messages are a rolling context window, not durable
OpenAI conversation state. See [personality.py](src/trubot/personality.py) for
the voice contract and [ARCHITECTURE.md](ARCHITECTURE.md) for the design.

Trubot shares supported excitement, keeps jokes relevant, and responds to difficult
news with care. It remains a fictional bot and does not invent Andrew's actions
or current sports facts. The evolving roadmap and release evidence live in
[docs/trubot-evolution](docs/trubot-evolution/plan.md).

The fictional character is available even when memory retrieval returns nothing.
Jokes, playful opinions, innuendo and comic exaggeration do not require historical
evidence. Claims about Andrew's real actions, preferences or past words do.
Read the conversational intent: accept an offered joke, answer a genuine factual
question accurately, and meet grief with care. Bot identity does not mean robot jokes.

## Local development

Requirements:

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- a Discord bot with the **Message Content Intent** enabled
- a private, persistent directory for the API usage ledger

```sh
uv sync --locked --all-groups
cp .env.example .env
export TRUBOT_USAGE_LEDGER_PATH="$PWD/.trubot-state/usage.sqlite3"
uv run trubot-budget init --path "$TRUBOT_USAGE_LEDGER_PATH"  # once only
uv run trubot
```

Fill in `DISCORD_TOKEN` and `OPENAI_API_KEY` in the local `.env`. Production
credentials should remain in the deployment environment; no secret belongs in
this repository.

Run the complete local quality gate with:

```sh
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
uv build
```

## Configuration

Only two variables are required.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DISCORD_TOKEN` | required | Discord bot token |
| `OPENAI_API_KEY` | required | OpenAI API key |
| `TRUBOT_OPENAI_MODEL` | `gpt-6-luna` | Only this model has approved pricing; other models stop generation |
| `OPENAI_TIMEOUT_SECONDS` | `45` | End-to-end SDK request timeout |
| `OPENAI_MAX_RETRIES` | `2` | Accounted adapter retries for transient failures, from 0 to 4 |
| `TRUBOT_USAGE_LEDGER_PATH` | `/var/lib/trubot/usage.sqlite3` | Pre-initialized persistent API usage ledger |
| `OPENAI_MAX_OUTPUT_TOKENS` | `512` | Hard total token ceiling; explicit/ambient replies are also capped at 180 |
| `TRUBOT_ALLOWED_CHANNEL_IDS` | existing league and development channels | Comma-separated Discord channel IDs |
| `TRUBOT_DEVELOPMENT_GUILD_ID` | existing private development guild | Its owner can test league recall in an allowed channel; `0` disables access |
| `TRUBOT_REACTION_EMOJIS` | `ThomasJones,🍆` | Comma-separated reaction names |
| `TRUBOT_LEARNING_STORE_PATH` | `/var/lib/trubot/learning.sqlite3` | Explicitly initialized private evidence store; unavailable state pauses learning |
| `TRUBOT_LEARNING_RETENTION_DAYS` | `180` | Text retention and maximum catch-up age, from 1 to 365 days |
| `TRUBOT_LEARNING_BATCH_SIZE` | `50` | Oldest messages scanned per channel per cycle, from 1 to 100 |
| `TRUBOT_LEARNING_POLL_SECONDS` | `300` | Background cycle interval, at least 60 seconds |
| `TRUBOT_HISTORY_LIMIT` | `30` | Maximum recent Discord messages sent as context |
| `TRUBOT_HISTORY_WINDOW_MINUTES` | `360` | Maximum age of channel context |
| `TRUBOT_FOLLOWUP_WINDOW_MINUTES` | `10` | Attention window for inferred follow-ups; `0` disables it |
| `TRUBOT_AUTO_DELAY_MINUTES` | `10` | Required quiet time before an ambient reply |
| `TRUBOT_AUTO_ACTIVITY_WINDOW_MINUTES` | `60` | Window used to count active people |
| `TRUBOT_AUTO_MIN_INTERVAL_HOURS` | `2` | Minimum time between any reply and ambient chatter |
| `TRUBOT_AUTO_DAILY_LIMIT` | `3` | Ambient replies per channel per UTC day; `0` disables them |
| `TRUBOT_AUTO_MIN_PARTICIPANTS` | `2` | Distinct people required for ambient chatter |
| `HEALTH_READY_FILE` | `/tmp/wcb-bot-ready` | Container readiness heartbeat |
| `HEALTH_REFRESH_SECONDS` | `60` | Heartbeat refresh interval |
| `HEALTH_MAX_AGE_SECONDS` | `180` | Maximum healthy heartbeat age |
| `LOG_LEVEL` | `INFO` | Python log level |

The same contract is machine-readable in [env.schema.json](env.schema.json).
`TRUBOT_OPENAI_MODEL` intentionally replaces the v1 `OPENAI_MODEL` variable so
a stale deployment override cannot silently keep the bot on `gpt-4.1-mini`.

## Container and releases

```sh
docker build --tag wcb-trubot:local .
docker run --rm --env-file .env \
  --mount type=bind,src="$PWD/.trubot-state",dst=/var/lib/trubot wcb-trubot:local
```

Prepare the mounted directory for container UID/GID 10001 and initialize the
ledger using that image before starting the bot. The image runs as an unprivileged user and reports healthy only while the
Discord connection heartbeat is fresh. GitHub pull requests run formatting,
linting, strict type checks, tests with branch coverage, and a package build.
Publishing a GitHub release produces signed-metadata, SBOM-enabled AMD64 and
ARM64 images at `ghcr.io/jdegregorio/wcb-discord-bot`, tagged by semantic
version and commit SHA.

## Character evaluation

With existing app-scoped credentials available, run the opt-in live evaluation:

```sh
uv run python scripts/evaluate_personality.py \
  --fixtures tests/fixtures/emotional_judgment.json --samples 2
uv run python scripts/evaluate_personality.py \
  --fixtures tests/fixtures/banter_judgment.json --samples 2
```

Use only synthetic fixtures. The harness runs the real Discord event handlers
and OpenAI adapter while capturing all posts in a mock channel. It never logs
into Discord, sends a Discord message, or changes production learning state.
Runs are limited to 12 cases and three samples each, with reasoning and output capped at 512 tokens and SDK retries disabled.
It reports actual API token usage and requires separate rubric review for
enthusiasm, relevance, tone, and factual restraint. A zero exit code confirms
transport checks only. CI tests the harness without making API calls.

`emotional_judgment_holdout.json` provides two additional variation checks;
`core_voice.json` checks the established Thomas Jones answer and recovery from
an irrelevant earlier bot reply.

`banter_judgment.json` checks figurative setups, TJ hero worship, affectionate
silliness, innuendo and understated rivalry. It also checks genuine grief,
missing real memories, literal definitions and questions for other recipients.
Review whether a reply actually adds a comic turn, rather than merely acknowledging
the setup. Brevity and successful delivery alone do not establish humor quality.

## Stable empty native setup (2.27.4)

Supported recall keeps the same conservative packet when optional native setup is
empty or absent. This prevents empty coverage metadata from discarding a verified
answer. Fresh source/author/withdrawal checks and exact final packet comparison
remain. Nonempty setup, media/coverage gaps and oversized omissions still retain
their meaning and can stop publication when changed. No extra provider call or storage.

## Recent personal activity (2.27.3)

Explicit factual questions about recent travel, activities, reading or play use
the existing bounded dated-source route. Undated history and optional voice examples
cannot establish recency. First-person activity questions also use authenticated
requester ownership, so another person's history cannot become the asker's biography.
Hypothetical choices, advice, current news and broad past recall retain their routes.
This is a conservative lexical boundary, not a general intent classifier or new
personal observation. Source correction, withdrawal and final checks still apply;
there is no new provider pass, service or spending allowance.

## Complete authored reply evidence (2.26.1)

Reply context preserves complete stored authored passages up to6,000UTF-8bytes.
Larger passages and their adjacent context are omitted together with an internal
gap, so a closing qualification cannot silently disappear behind a partial quote.
This changes reply rendering only; native intake bounds remain unchanged. It does
not resolve the separate historical speaker-attribution synthesis issue.

## Conversational abstract-memory continuity (2.27.1)

Recognized short follow-ups such as "How would you handle that?" use the immediate
human setup to find relevant source-backed memory. The original question still
governs the reply. Only one complete setup of at most600characters is eligible;
new topics, intervening humans and bot/memory/reference rows cannot supply it.
Own-history questions also retain only conversation text from the authenticated
focus author; prior bot replies, peers and detached references cannot establish
that person's history. Author IDs are ephemeral metadata and never provider text.
Requester ownership and fresh source checks still apply. This enables natural
abstract-memory use without a new provider call or new human observation.

## Shared concept lookup aliases (2.26.8)

Adding a reviewed memory to a shared concept preserves earlier lookup aliases.
Each new alias belongs to its reviewed relationship; current supporting evidence
must validate before that alias can retrieve shared neighbors. Replacement,
retirement, correction and expiry can remove a route without erasing other routes.
Legacy node aliases remain a read fallback. Already overwritten legacy aliases
need source-reviewed reimport. The existing result/source/freshness bounds remain.

## Bounded connected recall (2.26.0)

Relevant memory growth retains up to four complete observations and five unique
support/contrary sources rather than losing every result on a crowded topic.
Reviewed whole-word aliases rank by specificity; valid transitive disagreements
stay together or are omitted as a group. Source freshness checks remain bounded,
with attribution, expiry, correction and withdrawal preserved. This enables larger
qualified abstract libraries, without establishing a new trait or measured humor gain.

## Topic-bearing requester recall (2.26.4)

Questions such as "What team have I said I support?" and "Which side did I support?"
reach the authenticated author guard before historical retrieval. Another speaker's
own recall cannot borrow Andrew's source text, abstractions or voice examples.
The focused human message and prior human statements remain available, including
explicit fictional premises within their scene. Quoted peers cannot supply the
requester's answer. Andrew retains his own retrieval.
Quoted questions and hypothetical advice preserve their existing routing.

## Final private-source check (2.26.6)

A generated reply with retrieved private memory is revalidated immediately before
posting, using the existing source and author-scope checks. If a correction,
withdrawal, changed access or unavailable check invalidates the packet, the draft
is discarded without another generation attempt. Replies without private memory
and recipient abstentions retain their existing behavior. This protects source
lifecycle during generation; it adds bounded source reads, no provider call.
The final check and Discord send cannot form an atomic cross-service transaction.

## Historical authored recall (2.26.5)

Ordinary questions about remembered words or positions use complete Andrew-authored
Slack passages without adjacent speakers' text or competing optional voice examples.
Explicit context, joke, explanation, quote and evidence requests retain separately
attributed surroundings. Native setup and reviewed abstractions keep their existing
behavior. Source dates, provenance, conflicts, correction and withdrawal remain
internal and authoritative. This narrows a measured peer-stance failure; it does
not establish general semantic accuracy or a new personal trait.

## Memory author binding (2.19.2)

Reviewed graph rollouts can be previewed with `trubot-graph import --manifest
<private-manifest> --dry-run`. Preview runs full source/provenance/conflict validation
without changing beliefs or backups; the later import revalidates everything.
Qualified abstract memories require independent contextual support, limitations,
contrary evidence and actual reply checks. Private population is not packaged in Git.
See the [storage runbook](docs/trubot-evolution/storage.md) for rollout and retirement.

Historical evidence and abstract episode memories remain attributed to Andrew.
An authenticated source/focus-author comparison distinguishes his own questions from
another person's questions, including reactions and misleading display names.
Ordinary persona recall uses natural first-person or named-source language without
assigning Andrew's history to the person asking. Unknown authors receive conservative
attribution. Scope is rechecked alongside private source state before reuse.

## Repeated reply recovery (2.20.0)

When an addressed answer exactly copies a long older bot reply or a 12-word passage
inside a changed answer, Trubot can make one separately budgeted attempt at fresh wording.
Case, punctuation and apostrophe differences do not hide copied passages. The immediate bot turn, short
reactions, requested quotes/repetitions and explicit references retain deliberate
reuse. The extra attempt uses the same source context and model, with no transport
retries or third quality attempt. An unavailable, empty or incomplete refresh
keeps the existing accounted draft; a refreshed follow-up may still abstain.
Private memory is revalidated through the handler before refresh; a changed,
withdrawn or unchecked packet is not sent again. This targets exact stale
repetition, not a general humor or factual quality score. Short common wording and
approximate semantic similarity do not trigger another attempt.

## API spending guard

Every provider attempt reserves a conservative cost in a private SQLite ledger
before network I/O. The UTC calendar-month allowance is USD 20: USD 18 for
normal replies and USD 2 shared by evaluations and future learning. The adapter
accounts for each retry separately; empty outputs and abstentions still count.
Only GPT-6 Luna at the standard global endpoint has approved pricing.

Actual token counts and a conservative dollar estimate are recorded without
message text, user IDs, channel IDs, or credentials. Uncached input is estimated
at the higher cache-write rate because the installed SDK does not report cache
writes separately. These estimates are not provider billing records. Prices were
verified on 2026-10-06 against [OpenAI's model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna).

Missing, corrupt, unwritable, or unsupported state stops generation. Exhaustion
pauses explicit replies with a brief message and keeps inferred/ambient attempts
silent. State is never recreated automatically. Uncertain requests retain their
full reservation across restarts and subsequent months. Settled metadata is
retained for 13 months. Spending before initial deployment is unknown and cannot
be included retroactively; the first covered month reports that limitation.

Use `uv run trubot-budget status --path "$TRUBOT_USAGE_LEDGER_PATH"` to inspect
usage. Production storage, backup, correction, deletion, and recovery are covered
in [the storage runbook](docs/trubot-evolution/storage.md). There is no added paid
infrastructure. Keep all app-key API use, including evaluation, on this ledger.

## Private learning intake

An authorized operator can withdraw private learning with `trubot-learning forget`.
It erases the archive, pinned identity, adjacent audit, and documented local learning
backups, and writes a private durable marker. An old database restore cannot resume
intake while that marker exists. The usage ledger and normal replies remain available.
See [the storage runbook](docs/trubot-evolution/storage.md) for recovery boundaries.

Version 2.3.0 starts a reliable evidence intake loop. A trusted operator must
first corroborate Andrew's unique stable account with authenticated author and
guild-member metadata, then initialize `learning.sqlite3` from that private audit.
Runtime never guesses an identity, changes it from channel text, or creates lost
state. An unavailable learning store pauses learning while normal replies continue.

The existing client ingests only that pinned human's text in the intersection of
the configured allowlist and the channels approved by the audit. A five-minute
background cycle revalidates membership and scans one bounded page per channel,
committing attribution, source timestamps, and checkpoints together. It also
rechecks two stored messages per channel to repair edits or deletions missed
while offline. Gateway edit/delete events remove stale text immediately.

Text is capped at 4,000 characters, 10,000 records and 180 days by default.
No attachment files or other participants' messages are archived. Deleted text
is erased, with content-free markers preventing scan races from restoring it.
The evidence remains private and does not enter prompts in this increment;
preference derivation and relevant retrieval are the next roadmap step. Intake
makes no OpenAI calls and adds no paid infrastructure. See the storage runbook
for initialization, correction, retention, deletion and recovery.

Run `uv run python scripts/evaluate_ingestion.py` for a synthetic acceptance
check through the real handlers, using disposable storage and captured posts.
It makes no external calls. Production content-free status is available through
`docker exec wcb-bot trubot-learning status` on pi5.

## Historical league archives

Operator-imported Slack text exports extend Trubot's private learning corpus with
other speakers' conversational context. `trubot-archives` preserves raw sources,
deduplicates files, labels speaker blocks and flags missing dates or ambiguous
quotes/previews. Accessible native image attachments are retained with nearby
conversation, while missing or external-only media is marked explicitly. Version 2.5.0 retrieves bounded Andrew-attributed text evidence for live replies.
The retained historical images support ongoing contextual studies. See the [evolution plan](docs/trubot-evolution/plan.md)
and [private storage contract](docs/trubot-evolution/storage.md) for scope, import,
correction, withdrawal and recovery.


## Live memory and image context

Version 2.5.0 connects private source memory to responses. Relevant Andrew-authored
native messages are refreshed before use; legacy Slack passages include source
lines, date uncertainty and separately labeled adjacent context. Supported
preferences can now inform the persona. Other people's claims and prior bot
replies cannot establish Andrew's beliefs. Retrieval currently uses bounded
keywords and topic expansion; full contextual interpretation remains ongoing.

Live replies can read pixels in the current message, the same-channel message it
references, and recent conversation. The two-image limit prioritizes focus and
reference images. Discord attachments and proxied previews are fetched without
credentials, decoded and sent as structured vision inputs. Unavailable images
are marked; animations provide only their first frame. Live pixels are ephemeral.

The operator acceptance script uses authenticated read access and the existing
maintenance ledger while capturing every Discord send:

```bash
uv run python scripts/evaluate_live_context.py --expected-team-file /private/team.txt
```

It requires an operator-reviewed mode-0600 expectation file in a private directory
and the verified private learning store. It checks grounded baseball
memory, direct/follow-up behavior, image content/OCR, reactions and bot-memory
exclusion. See the storage runbook for source freshness, withdrawal and bounds.


## Connected private memory

Version 2.14.0 extends conditional graph memory to observed values, expressed
emotional responses and ways of interacting. New domains require recurring
attributed support, applicability, limitations and separate review. They cannot
be flat claims or singleton habits. This enables future evidence-backed learning;
it does not establish a new Andrew trait or a measured fidelity improvement.


Version 2.13.0 connects automatic humor/style studies to conditional graph memory.
Each accepted pattern retains separate applicability, limitations and attributed
counterexamples, with tentative status, expiry and source-driven invalidation.
Ordinary relevant replies receive summaries rather than pattern-only source jokes.
This enables future evidence-backed learning; synthetic conformance does not
establish a new human trait or a measured fidelity improvement. Study pacing and
the existing maintenance budget remain unchanged.

Version 2.6.0 adds a private SQLite evidence graph. Reviewed concepts can retrieve
supporting exchanges through different wording, with confidence, source dates,
contradictions and expiry preserved. Native sources are refreshed before use;
edits, deletion and withdrawal invalidate derived memory. Initial coverage and
limitations are recorded in the [living memory plan](docs/trubot-evolution/living-memory.md).
Images are connected to captured episodes but historical visual interpretation
and continuous distillation remain future work. Operator commands and recovery
are in the [storage runbook](docs/trubot-evolution/storage.md).

The bounded acceptance script reads private expectations, uses the existing
maintenance ledger and captures all Discord sends:

```sh
uv run python scripts/evaluate_graph.py --expectations /private/expectations.json --phase installed
```

Answer-term checks verify recall; separate contextual review evaluates scope,
natural engagement and unsupported claims. Private responses and expectations
must remain outside Git and application logs.


## Continuous private graph learning (2.7.0)

The existing background learning cycle adds new eligible native/Slack sources to
an explicitly initialized graph. Every four hours it studies at most six related
human excerpts, with separately labeled Slack adjacency. New claims/preferences
and contextual humor/style observations need 2-3 distinct exact support quotes
and a separate model review. Accepted observations are tentative, expire after
30 days, and carry source references, uncertainty and extraction provenance.
They enter bounded connected recall after the existing source verification.

The learner uses GPT-6 Luna, strict [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs),
no tools, no retries and `store=false`. Both attempts use the existing maintenance
ledger. Restart, failure or reconnect cannot reset its four-hour pacing. Missing
or withdrawn graph/source state pauses studies while ordinary replies continue.
It never posts a Discord message itself. See the storage runbook for operator
retirement, correction and recovery, and progress.md for measured coverage.

## Private development recall (2.7.1)

The owner of the configured development guild can query the same verified league
memory from an existing allowed channel. Other guilds and development users do
not gain that access. Development messages never become Andrew's source evidence.
Native support refresh, corrections, withdrawal and the persistent spending guard
remain required. Set `TRUBOT_DEVELOPMENT_GUILD_ID=0` to disable this access.

Year questions retrieve dated native sources or passages from matching historical
export labels. A label such as 2020 is provenance, not a message timestamp. Trubot
can give a supported quote from that labeled export while acknowledging its unknown
exact date. Full all-years native Discord history remains incomplete.

Release smoke tests must post actual human questions to the private development
server and read the running bot's actual responses. Use the authenticated Discord
UI for the owner account; never use a user token or pretend a bot probe is human.
Check grounded baseball recall, a year-labeled historical quote with date uncertainty,
and the changed acceptance scenario. Captured sends remain regression coverage.

## Grammatical recall coverage (2.9.2)

Reviewed graph aliases and lexical source scoring treat an explicit, bounded set
of common sports/league noun plurals as equivalent to their singular forms.
This preserves connections such as a singular alias queried with a plural noun.
Names, verbs, semantic synonyms and exact source quotations keep their existing
meaning. Sources, conflicts, freshness and withdrawal remain authoritative.
This improves a demonstrated retrieval miss; wider conceptual recall is still
incomplete and no general reply-quality gain has been measured.


## Bounded memory extraction (2.9.3)

The learner supplies a packet-specific structured schema: bounded observation
text and aliases, distinct self-report/corroborated alternatives, source indexes
restricted to supplied passages, and reviewer references restricted to supplied
observations. A singleton must quote the complete eligible anchor. Local exact
quote, independence, context, freshness and semantic review remain authoritative.
No new learning source or provider request is added; pacing and monthly spending
reservations are preserved. This strengthens contract reliability; broad reply
quality and natural production extraction gains remain unmeasured.


## Source-checked contextual voice (2.10.0)

Legacy examples are lookup keys rather than unconditional personal evidence.
Replies can receive at most three current attributed archive passages whose
preceding peer setup also matches. Quoted/ambiguous/media-dependent context is
excluded. Source correction, removal, historical year scope and learning withdrawal
apply to these examples, including owner-only development recall. They illustrate
one context rather than establishing a habit or biography. Fixed unvalidated
biography/style assertions are removed; missing evidence gets brief uncertainty.
No new model call, source, storage schema or paid infrastructure is introduced.


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


## Rolling conversation recall (2.11.1)

Authored recall such as "quote something from the past week" or "what did you say
in the last 48 hours" uses verified native timestamps. Numeric and ordinary spelled
hours/days/weeks define rolling durations, intersected with current retention.
Selection and rendering both recheck the window; at most three native sources and
two human neighborhoods are supplied. Empty, zero or unknown quantities cannot
fall back to undated archives or voice examples. Named calendar months/days remain
outside this parser; explicit year recall keeps its existing provenance rules.
No new state, retention, provider call, model, participation or spending policy.


Freshly checked memory follows previous conversation and precedes the current
question, including its image pixels. Earlier bot replies remain conversation
context and cannot override authenticated human memory evidence.


## Focused quotation recall (2.11.3)

Timing and evidence requests prioritize one explicit quotation in the current
question. Implicit quotation lookup follows only an uninterrupted timing/evidence
chain, stops at a new subject, and rejects ambiguous quotations. Every key still
requires current attributed source support; bot/peer wording never establishes a
human statement. Named topics retain topical search. Qualified day/month/year
questions use timing presentation, while ordinary recall keeps natural language.
Unrelated voice examples are omitted from quotation lookup. No new provider call,
source scope, storage schema, model, participation rule or spending allowance.


## Conditional episode memory candidate

Candidate 2.12.0 represents reviewed humor/style abstractions with conditions,
limitations and linked human counterexamples. Source changes invalidate the whole
pattern. Ordinary relevant context uses the summary; explicit evidence requests
keep source passages. Existing factual memory, five-source bound, fresh native
checks, withdrawal and spending remain. This is enabling work with 24 regression
cases; measured human fidelity is still open. The private pattern remains offline
pending specific OpenAI payload approval. See the evolution research and storage
notes for validation, lifecycle and rollback boundaries.


## Human focus for imaginative follow-ups (2.12.1)

Inferred follow-ups can carry at most 600 characters from the immediately
preceding human setup. Typed conversation, memory, reference and focus origins
prevent retrieved evidence or detached older messages from supplying that topic.
Intervening human chat disables the anchor. The latest question and image pixels
remain focused, recipient judgment remains separate, and added context is reserved
in the existing spending ledger. No extra request, source scope, state or model.

Explicit hypothetical choices may be made conditionally without evidence of
Andrew's actual favorite. Such choices never become human facts. All source,
withdrawal, recipient and emotional rules remain. Amplified humor prototypes
failed their research criteria and are not included. Conditional episode storage
from merged #62 is included as enabling code; its selected private pattern is
still offline and its behavioral study remains open.

## Reviewed memory rollout (2.18.0)

Private `trubot-graph import` manifests commit their complete reviewed observation
batch under one source lock. A validation failure rolls back earlier entries,
including replacements and conflict changes, and keeps prior backups intact.
Batches require one to 100 distinct observation IDs. Successful imports retain
existing backup cleanup, correction, retirement and withdrawal behavior.

Curated episode abstractions remain conditional and tentative, with current
attributed support, applicability controls, provenance and expiry. Ordinary
replies use the relevant abstract mechanism without quoting its source examples.
Population is distinct from independent human validation or general fidelity gains.

## Abstract memory presentation (2.19.0)

Ordinary replies use conditional episode summaries with their uncertainty and
limits. Review counts and confidence explanations stay in the private graph and
explicit evidence requests. A validated abstraction packet prevents raw voice
examples from competing with that guidance. Literal quotes, factual shared support
and timing evidence remain available through the existing source checks. This
is enabling behavior; current production has no active human abstract patterns.


## Complete live conversational setup, 2.19.3

Native human neighbors and same-channel parents, plus historical adjacent blocks,
are supplied as complete text up to 600 UTF-8 bytes per message. Oversized context
is omitted with an explicit gap rather than silently clipped. Native source/media
gaps, speaker roles, reply links, same-channel scope, bounded reads and mandatory
source freshness remain authoritative. Historical bot context is labeled separately
from peers. Authored-source text ceilings remain unchanged. This does not broaden
intake, persist peers, populate a human trait or add provider/HTTP requests. Existing
withdrawal, spending, privacy and compatible rollback remain unchanged.


## Native character pattern evidence gate (2.20.1)

Automatic native studies currently lack durable conversational setup. They cannot
establish recurring humor, style, values, emotional or relationship patterns until
context provenance and edit/delete/visibility invalidation are implemented. The gate
applies to support and counterevidence during generation, validation, storage and
restored recall. Normal sweeping erases incompatible automatic patterns and graph
backups. Reviewed historical studies, operator review and unambiguous native literal
claims/preferences retain their existing contracts. No new API calls or source schema.


## Native dependency capture (2.21.0)

Existing native reply retrieval now records content-free source-to-context links in
memory-graph.sqlite3. At most100 captures/up to five human dependencies each/30-day
capture lifetime, plus the native source retention floor. Speaker/channel/message
IDs, source/capture timestamps, reply relations, full text hashes, media-presence
markers and coverage gaps remain private. Original pixels are not represented by
these hashes, and no peer text or derived human interpretation is persisted.

Shared learning-lock checks reject raced captures. Known peer edits/deletes and
source changes erase links and graph backups; current target-neighbor rows also
block stale restored metadata after correction. Missing graph/denied setup reads
leave ordinary replies available. Withdrawal erases this graph state and preserves
the spending ledger. No schema migration, source replay or new provider/Discord
request. Optional metadata comes from the existing live collector, not a new intake.

A capture records observed bounded setup, not current visibility or complete context.
The automatic native pattern gate remains closed. H55b must add fresh per-dependency
reads before studies/both provider passes/commit, full contextual packets and held-out
validation before opening it. No new abstraction or measured reply-quality gain.
Rollback2.20.1 is schema-compatible and retains the pattern gate, but stops the new
capture lifecycle; sweep/remove native_context and orphan native_context_dependency
nodes with2.21.0 before a deliberate downgrade after capture. Do not restore source
or spending databases to roll back code. Synthetic smoke artifacts keep only
content-free refs/flags/public code under private app-volume0700/0600 and existing
seven-day manual retention/withdrawal cleanup; disposable databases are erased.

## Native context freshness (2.22.1)

The existing learning cycle rechecks up to two captured native neighborhoods, within
six seconds and at most six HTTP reads. Missed peer changes/deletions and lost
read access erase obsolete setup links. Complete current human text stays ephemeral;
stored fingerprints do not certify complete context or current visibility. Timeout
and transient failures do not fabricate deletion. Native abstract-pattern learning
remains gated pending contextual study integration and human validation.

The2.22.1 correction uses one current bounded history page for retained dependency
IDs, plus an exact same-channel parent read if needed. Freshness/attribution checks
still apply to every dependency. No new neighbors enter learning/context; missing
nonparents erase obsolete captures without guessing message deletion. No preserved
freshness certificate or automatic native pattern permission. [Transport study](docs/trubot-evolution/evaluations/2026-10-13-native-freshness-study.md).

## Fresh native study support (2.22.2)

The learner rereads the original native source cohort before each maintenance provider
attempt and before committing a reviewed observation. Missed edits/deletions or lost
read access pause the study; current source attribution, withdrawal and the locked
local commit remain authoritative. The two provider passes retain identical original
evidence. Four bounded read stages admit at most six native sources each, with six
seconds total and four seconds per read. Maintenance retries remain disabled.
This adds no provider attempt or schema and keeps automatic native patterns gated.

Native maintenance studies bind any existing private setup fingerprints to their
resulting observations. A changed or removed setup pauses the study or retires
its dependent memory. The new fingerprints stay local; provider studies remain
target-only and automatic native personality patterns remain gated. See the
[evolution plan](docs/trubot-evolution/plan.md) for semantic-learning prerequisites.


## Brief ordinary replies (2.24.1)

An ordinary addressed draft with more than two prose sentences or sixty words can
receive one complete shorter attempt, shared with repetition recovery. It keeps the
same contextual facts and emotional intent. Quotation, evidence, detail and creative
writing requests retain their runway. Quoted punctuation, decimals and common
abbreviations do not masquerade as extra sentences. No reply is mechanically cut.
The same private-memory recheck and spending guard apply; a failed or still-overlong
repair keeps the original. This is a bounded length correction, not a semantic judge
or a guarantee of humor, naturalness or Andrew fidelity.

## Short reply continuity (2.24.2)

Answers with at most five words and sixty characters retain normal brief continuity
without an optional cosmetic repetition rewrite. Initial memory verification remains.
Longer repeated replies/passages and independent brevity repair still share the existing
single budgeted quality attempt. This boundary also permits a short punchline to repeat;
it does not establish factual truth or solve semantic joke repetition.


## Qualified character patterns (2.26.7)

Humor and style memories now require the same conditional abstraction and separated
support as values, emotions and relationships. New unqualified imports are rejected;
restored unqualified patterns are excluded from replies and removed by normal graph
sweeps. Qualified older patterns remain readable, including those without newer
domain metadata. Literal claims/preferences retain their existing evidence rules.
This enables safer abstract population; it does not add a new human trait or prove
more natural or funnier replies. See the [study](docs/trubot-evolution/evaluations/2026-10-15-abstract-humor-study.md).

## Bounded native reply verification (2.27.2)

Multiple selected native sources in one approved channel share one fresh100-row
history read. Only the selected sources are refreshed; intake cursors and unselected
messages are untouched. Missing IDs require exact reads; denied channels stop.
The existing6s shared deadline and source/scope/withdrawal publication checks remain.
This reduces repeated-read pressure without adding a model call or durable cache.


## Operator recovery of older original photos

After photo memory is initialized, run `trubot-photo-history init` once, then
`trubot-photo-history scan --pages 1` for bounded resumable older-photo recovery.
`status` reports coverage counts and open gaps. The command only reads existing
source text channels, captures at most two pinned-human original photos per run,
and makes no provider calls or Discord posts. The existing study allowance,
128-photo limit and source correction/withdrawal controls apply. Broader history
and reply-quality benefits remain unvalidated. See [H99](docs/trubot-evolution/evaluations/2026-10-18-photo-history.md).


## Recovered original photo recall

The existing model-selected photo action also searches private recovered-photo
records. It ranks the pinned human's source captions and completed pixel profiles,
then freshly checks up to three candidates within eight seconds. One verified
original image reaches the caption continuation. The fixed source, current
recipient permissions, request and pixel hash must still match before publication.
Pending captionless originals remain unsearchable until the existing bounded
pixel-study cadence supplies a profile. Peer posts never become character photos.
This makes supported older views reachable without expanding rolling text intake,
learning scope, provider calls for indexing, or the spending allowance.
