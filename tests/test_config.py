from pathlib import Path

import pytest

from trubot.config import (
    DEFAULT_ALLOWED_CHANNEL_IDS,
    DEFAULT_READY_FILE,
    ConfigurationError,
    Settings,
)

VALID_ENV = {
    "DISCORD_TOKEN": "discord-secret",
    "OPENAI_API_KEY": "openai-secret",
}


def test_defaults_target_luna_responses_workload() -> None:
    settings = Settings.from_env(VALID_ENV)

    assert settings.openai_model == "gpt-5.6-luna"
    assert settings.allowed_channel_ids == DEFAULT_ALLOWED_CHANNEL_IDS
    assert settings.auto_daily_limit == 3
    assert settings.auto_delay_seconds == 600
    assert settings.ready_file == DEFAULT_READY_FILE
    assert "discord-secret" not in repr(settings)
    assert "openai-secret" not in repr(settings)


def test_overrides_are_parsed_and_normalized() -> None:
    settings = Settings.from_env(
        {
            **VALID_ENV,
            "TRUBOT_ALLOWED_CHANNEL_IDS": " 11, 22,11 ",
            "TRUBOT_REACTION_EMOJIS": "ThomasJones, 🏈 ",
            "TRUBOT_AUTO_DELAY_MINUTES": "0.5",
            "TRUBOT_AUTO_ACTIVITY_WINDOW_MINUTES": "15",
            "TRUBOT_AUTO_MIN_INTERVAL_HOURS": "1.5",
            "OPENAI_MAX_RETRIES": "4",
            "OPENAI_MAX_OUTPUT_TOKENS": "200",
            "TRUBOT_HISTORY_LIMIT": "25",
            "HEALTH_READY_FILE": "/run/trubot/custom-ready",
            "HEALTH_REFRESH_SECONDS": "10",
            "HEALTH_MAX_AGE_SECONDS": "20",
            "LOG_LEVEL": "debug",
        }
    )

    assert settings.allowed_channel_ids == frozenset({11, 22})
    assert settings.reaction_emoji_names == frozenset({"ThomasJones", "🏈"})
    assert settings.auto_delay_seconds == 30
    assert settings.auto_activity_window_seconds == 900
    assert settings.auto_min_interval_seconds == 5400
    assert settings.openai_max_retries == 4
    assert settings.openai_max_output_tokens == 200
    assert settings.history_limit == 25
    assert settings.ready_file == Path("/run/trubot/custom-ready")
    assert settings.log_level == "DEBUG"


@pytest.mark.parametrize("missing", ["DISCORD_TOKEN", "OPENAI_API_KEY"])
def test_required_secrets_are_validated(missing: str) -> None:
    env = {**VALID_ENV, missing: "  "}
    with pytest.raises(ConfigurationError, match=f"{missing} is required"):
        Settings.from_env(env)


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("TRUBOT_ALLOWED_CHANNEL_IDS", "abc", "comma-separated list of integers"),
        ("TRUBOT_ALLOWED_CHANNEL_IDS", "-1", "values must be positive"),
        ("TRUBOT_REACTION_EMOJIS", "", "at least one value"),
        ("OPENAI_TIMEOUT_SECONDS", "nope", "must be a number"),
        ("OPENAI_MAX_RETRIES", "1.5", "must be an integer"),
        ("OPENAI_MAX_RETRIES", "-1", "must be at least 0"),
        ("OPENAI_MAX_OUTPUT_TOKENS", "0", "must be between"),
        ("TRUBOT_HISTORY_LIMIT", "101", "must be between"),
        ("TRUBOT_AUTO_ACTIVITY_WINDOW_MINUTES", "0", "must be greater than 0"),
        ("TRUBOT_AUTO_MIN_PARTICIPANTS", "1", "must be at least 2"),
        ("HEALTH_REFRESH_SECONDS", "0", "must be greater than 0"),
        ("TRUBOT_OPENAI_MODEL", "", "must not be empty"),
        ("LOG_LEVEL", "verbose", "must be one of"),
    ],
)
def test_invalid_settings_have_actionable_errors(name: str, value: str, message: str) -> None:
    with pytest.raises(ConfigurationError, match=message):
        Settings.from_env({**VALID_ENV, name: value})


def test_health_max_age_must_exceed_refresh_interval() -> None:
    with pytest.raises(ConfigurationError, match="must be greater than HEALTH_REFRESH_SECONDS"):
        Settings.from_env(
            {
                **VALID_ENV,
                "HEALTH_REFRESH_SECONDS": "30",
                "HEALTH_MAX_AGE_SECONDS": "30",
            }
        )
