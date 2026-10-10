# Trubot

Trubot is the Will Carter Bowl League of Champions’ Discord character, shaped
by attributed league conversations, contextual voice examples and bounded
source-backed memory.

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
