# Trubot

Trubot is the Will Carter Bowl League of Champions’ Discord personality bot: a
dry, oddly sincere, Thomas-Jones-obsessed league member who occasionally has the
best one-liner in the channel.

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

All timing, limits, channel IDs, and reaction names are configurable. State is
intentionally in memory: a restart resets ambient counters, attention windows,
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

```sh
uv sync --locked --all-groups
cp .env.example .env
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
| `TRUBOT_OPENAI_MODEL` | `gpt-6-luna` | API-compatible model override |
| `OPENAI_TIMEOUT_SECONDS` | `45` | End-to-end SDK request timeout |
| `OPENAI_MAX_RETRIES` | `2` | SDK retry count for transient failures |
| `OPENAI_MAX_OUTPUT_TOKENS` | `512` | Hard total token ceiling; explicit/ambient replies are also capped at 180 |
| `TRUBOT_ALLOWED_CHANNEL_IDS` | four current league channel IDs | Comma-separated Discord channel IDs |
| `TRUBOT_REACTION_EMOJIS` | `ThomasJones,🍆` | Comma-separated reaction names |
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
docker run --rm --env-file .env wcb-trubot:local
```

The image runs as an unprivileged user and reports healthy only while the
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
Monthly runtime spend is not yet measured or capped; the persistent ledger and
spending guard are the next roadmap item.
