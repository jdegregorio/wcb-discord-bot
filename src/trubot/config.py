"""Runtime configuration with explicit parsing and validation."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_ALLOWED_CHANNEL_IDS = frozenset(
    {
        1042804140490883084,
        1042804380354752592,
        1043023451482505229,
        1171482001275093112,
    }
)
DEFAULT_REACTION_EMOJIS = frozenset({"ThomasJones", "🍆"})
DEFAULT_READY_FILE = Path("/tmp/wcb-bot-ready")  # noqa: S108 - isolated container heartbeat
_LOG_LEVELS = frozenset({"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"})


class ConfigurationError(ValueError):
    """Raised when runtime configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated process settings.

    Secret fields are deliberately excluded from ``repr`` so an innocent log
    statement cannot disclose deployment credentials.
    """

    discord_token: str = field(repr=False)
    openai_api_key: str = field(repr=False)
    allowed_channel_ids: frozenset[int] = DEFAULT_ALLOWED_CHANNEL_IDS
    reaction_emoji_names: frozenset[str] = DEFAULT_REACTION_EMOJIS
    openai_model: str = "gpt-5.6-luna"
    openai_timeout_seconds: float = 45.0
    openai_max_retries: int = 2
    openai_max_output_tokens: int = 180
    history_limit: int = 15
    auto_delay_seconds: float = 10 * 60
    auto_activity_window_seconds: float = 60 * 60
    auto_min_interval_seconds: float = 2 * 60 * 60
    auto_daily_limit: int = 3
    auto_min_participants: int = 2
    ready_file: Path = DEFAULT_READY_FILE
    health_refresh_seconds: float = 60.0
    health_max_age_seconds: float = 180.0
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        values = os.environ if env is None else env

        allowed_channels = _integer_set(
            values,
            "TRUBOT_ALLOWED_CHANNEL_IDS",
            ",".join(str(value) for value in sorted(DEFAULT_ALLOWED_CHANNEL_IDS)),
        )
        reaction_emojis = _string_set(
            values,
            "TRUBOT_REACTION_EMOJIS",
            ",".join(sorted(DEFAULT_REACTION_EMOJIS)),
        )

        settings = cls(
            discord_token=_required(values, "DISCORD_TOKEN"),
            openai_api_key=_required(values, "OPENAI_API_KEY"),
            allowed_channel_ids=allowed_channels,
            reaction_emoji_names=reaction_emojis,
            openai_model=_nonempty(values, "TRUBOT_OPENAI_MODEL", "gpt-5.6-luna"),
            openai_timeout_seconds=_number(values, "OPENAI_TIMEOUT_SECONDS", 45.0),
            openai_max_retries=_integer(values, "OPENAI_MAX_RETRIES", 2),
            openai_max_output_tokens=_integer(values, "OPENAI_MAX_OUTPUT_TOKENS", 180),
            history_limit=_integer(values, "TRUBOT_HISTORY_LIMIT", 15),
            auto_delay_seconds=60 * _number(values, "TRUBOT_AUTO_DELAY_MINUTES", 10.0),
            auto_activity_window_seconds=60
            * _number(values, "TRUBOT_AUTO_ACTIVITY_WINDOW_MINUTES", 60.0),
            auto_min_interval_seconds=60
            * 60
            * _number(values, "TRUBOT_AUTO_MIN_INTERVAL_HOURS", 2.0),
            auto_daily_limit=_integer(values, "TRUBOT_AUTO_DAILY_LIMIT", 3),
            auto_min_participants=_integer(values, "TRUBOT_AUTO_MIN_PARTICIPANTS", 2),
            ready_file=Path(_nonempty(values, "HEALTH_READY_FILE", str(DEFAULT_READY_FILE))),
            health_refresh_seconds=_number(values, "HEALTH_REFRESH_SECONDS", 60.0),
            health_max_age_seconds=_number(values, "HEALTH_MAX_AGE_SECONDS", 180.0),
            log_level=_nonempty(values, "LOG_LEVEL", "INFO").upper(),
        )
        settings._validate()
        return settings

    def _validate(self) -> None:
        _at_least_one(self.allowed_channel_ids, "TRUBOT_ALLOWED_CHANNEL_IDS")
        _at_least_one(self.reaction_emoji_names, "TRUBOT_REACTION_EMOJIS")
        _greater_than(self.openai_timeout_seconds, 0, "OPENAI_TIMEOUT_SECONDS")
        _at_least(self.openai_max_retries, 0, "OPENAI_MAX_RETRIES")
        _between(self.openai_max_output_tokens, 1, 4096, "OPENAI_MAX_OUTPUT_TOKENS")
        _between(self.history_limit, 1, 100, "TRUBOT_HISTORY_LIMIT")
        _at_least(self.auto_delay_seconds, 0, "TRUBOT_AUTO_DELAY_MINUTES")
        _greater_than(
            self.auto_activity_window_seconds,
            0,
            "TRUBOT_AUTO_ACTIVITY_WINDOW_MINUTES",
        )
        _at_least(self.auto_min_interval_seconds, 0, "TRUBOT_AUTO_MIN_INTERVAL_HOURS")
        _at_least(self.auto_daily_limit, 0, "TRUBOT_AUTO_DAILY_LIMIT")
        _at_least(self.auto_min_participants, 2, "TRUBOT_AUTO_MIN_PARTICIPANTS")
        _greater_than(self.health_refresh_seconds, 0, "HEALTH_REFRESH_SECONDS")
        _greater_than(self.health_max_age_seconds, 0, "HEALTH_MAX_AGE_SECONDS")
        if self.health_max_age_seconds <= self.health_refresh_seconds:
            raise ConfigurationError(
                "HEALTH_MAX_AGE_SECONDS must be greater than HEALTH_REFRESH_SECONDS"
            )
        if self.log_level not in _LOG_LEVELS:
            raise ConfigurationError(f"LOG_LEVEL must be one of {', '.join(sorted(_LOG_LEVELS))}")


def _required(env: Mapping[str, str], name: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise ConfigurationError(f"{name} is required")
    return value


def _nonempty(env: Mapping[str, str], name: str, default: str) -> str:
    value = env.get(name, default).strip()
    if not value:
        raise ConfigurationError(f"{name} must not be empty")
    return value


def _number(env: Mapping[str, str], name: str, default: float) -> float:
    raw = env.get(name, str(default)).strip()
    try:
        return float(raw)
    except ValueError as error:
        raise ConfigurationError(f"{name} must be a number") from error


def _integer(env: Mapping[str, str], name: str, default: int) -> int:
    raw = env.get(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError as error:
        raise ConfigurationError(f"{name} must be an integer") from error


def _integer_set(env: Mapping[str, str], name: str, default: str) -> frozenset[int]:
    raw_values = _split_csv(env.get(name, default))
    try:
        values = frozenset(int(value) for value in raw_values)
    except ValueError as error:
        raise ConfigurationError(f"{name} must be a comma-separated list of integers") from error
    if any(value <= 0 for value in values):
        raise ConfigurationError(f"{name} values must be positive")
    return values


def _string_set(env: Mapping[str, str], name: str, default: str) -> frozenset[str]:
    return frozenset(_split_csv(env.get(name, default)))


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _at_least_one(values: frozenset[object], name: str) -> None:
    if not values:
        raise ConfigurationError(f"{name} must contain at least one value")


def _greater_than(value: float, minimum: float, name: str) -> None:
    if value <= minimum:
        raise ConfigurationError(f"{name} must be greater than {minimum:g}")


def _at_least(value: float, minimum: float, name: str) -> None:
    if value < minimum:
        raise ConfigurationError(f"{name} must be at least {minimum:g}")


def _between(value: int, minimum: int, maximum: int, name: str) -> None:
    if not minimum <= value <= maximum:
        raise ConfigurationError(f"{name} must be between {minimum} and {maximum}")
