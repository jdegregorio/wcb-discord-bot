# WCB Discord Bot

Discord bot for the Will Carter Bowl League of Champions.

## Runtime configuration

Copy `.env.example` to `.env` for local development. Never commit `.env`; production secrets live in the deployment host's protected secrets directory.

Required variables:

- `DISCORD_TOKEN`
- `OPENAI_API_KEY`
- `TRELLO_KEY`
- `TRELLO_TOKEN`
- `TRELLO_FEATURE_REQUEST_LIST`

Optional variables:

- `OPENAI_MODEL` (default `gpt-4.1-mini`)
- `OPENAI_TIMEOUT_SECONDS` (default `60`)
- `TRUBOT_AUTO_MIN_INTERVAL_HOURS` (default `2`)
- `TRUBOT_AUTO_DAILY_LIMIT` (default `3`)
- `LOG_LEVEL` (default `INFO`)

`TRELLO_BOARD` is retained for compatibility with the existing deployment but is not currently read by the bot. See `env.schema.json` for the machine-readable inventory.

## Development

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python bot.py
```

## Container releases

Pull requests and changes to `main` run the test workflow. Publishing a GitHub release triggers the container workflow, which builds an ARM64 image and publishes immutable semantic-version and commit-SHA tags to:

```text
ghcr.io/jdegregorio/wcb-discord-bot
```

The Raspberry Pi deployment platform detects a newer published GitHub release, pulls its versioned image, waits for the container health check to report a live Discord connection, and records that version as the rollback target.

## Discord installation

Create a bot application in the Discord Developer Portal, enable the intents used by this bot, copy its token into the runtime environment, and invite it using the application's OAuth2 URL. Treat the token like a password.
