from unittest.mock import MagicMock, patch

import pytest

from trubot.app import build_client, main
from trubot.config import ConfigurationError, Settings


def test_build_client_wires_minimal_discord_intents_and_openai_settings() -> None:
    settings = Settings(
        discord_token="discord-secret",
        openai_api_key="openai-secret",
        allowed_channel_ids=frozenset({10}),
    )
    with patch("trubot.app.AsyncOpenAI") as client_class:
        client = build_client(settings)

    client_class.assert_called_once_with(
        api_key="openai-secret",
        timeout=45.0,
        max_retries=2,
    )
    assert client.intents.message_content
    assert client.intents.guilds
    assert client.intents.guild_messages
    assert client.intents.guild_reactions
    assert not client.intents.dm_messages
    assert not client.intents.members


def test_main_reports_configuration_errors_without_starting_discord() -> None:
    with (
        patch("trubot.app.load_dotenv"),
        patch("trubot.app.Settings.from_env", side_effect=ConfigurationError("bad config")),
        patch("trubot.app.build_client") as build,
        pytest.raises(SystemExit) as exit_info,
    ):
        main()

    assert exit_info.value.code == 2
    build.assert_not_called()


def test_main_runs_the_composed_client() -> None:
    settings = Settings(discord_token="discord-secret", openai_api_key="openai-secret")
    client = MagicMock()
    with (
        patch("trubot.app.load_dotenv") as load_dotenv,
        patch("trubot.app.Settings.from_env", return_value=settings),
        patch("trubot.app.build_client", return_value=client),
    ):
        main()

    load_dotenv.assert_called_once_with()
    client.run.assert_called_once_with("discord-secret", log_handler=None)
