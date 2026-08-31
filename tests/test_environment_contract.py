import json
from pathlib import Path
from typing import Any

from trubot.config import DEFAULT_ALLOWED_CHANNEL_IDS, Settings


def test_machine_readable_environment_contract_matches_runtime_defaults() -> None:
    schema_path = Path(__file__).parents[1] / "env.schema.json"
    schema: dict[str, Any] = json.loads(schema_path.read_text())
    properties = schema["properties"]
    settings = Settings.from_env(
        {"DISCORD_TOKEN": "discord-secret", "OPENAI_API_KEY": "openai-secret"}
    )

    assert schema["required"] == ["DISCORD_TOKEN", "OPENAI_API_KEY"]
    assert properties["TRUBOT_OPENAI_MODEL"]["default"] == settings.openai_model
    assert properties["OPENAI_MAX_OUTPUT_TOKENS"]["default"] == (settings.openai_max_output_tokens)
    assert properties["TRUBOT_HISTORY_LIMIT"]["default"] == settings.history_limit
    assert properties["TRUBOT_HISTORY_WINDOW_MINUTES"]["default"] == (
        settings.history_window_seconds / 60
    )
    assert properties["TRUBOT_FOLLOWUP_WINDOW_MINUTES"]["default"] == (
        settings.followup_window_seconds / 60
    )
    assert properties["TRUBOT_AUTO_DAILY_LIMIT"]["default"] == settings.auto_daily_limit
    assert {
        int(value) for value in properties["TRUBOT_ALLOWED_CHANNEL_IDS"]["default"].split(",")
    } == DEFAULT_ALLOWED_CHANNEL_IDS
    assert all("TRELLO" not in name for name in properties)
