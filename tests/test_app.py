from unittest.mock import MagicMock, patch

import pytest
from test_learning import AUDIT, NOW

from trubot.app import build_client, main
from trubot.budget import UsageLedger
from trubot.config import ConfigurationError, Settings
from trubot.learning import LearningStore


def test_build_client_wires_minimal_discord_intents_and_openai_settings(
    private_test_ledger: UsageLedger,
) -> None:
    settings = Settings(
        discord_token="discord-secret",
        openai_api_key="openai-secret",
        allowed_channel_ids=frozenset({10}),
        usage_ledger_path=private_test_ledger.path,
    )
    with patch("trubot.app.AsyncOpenAI") as client_class:
        client = build_client(settings)

    client_class.assert_called_once_with(
        api_key="openai-secret",
        timeout=45.0,
        max_retries=0,
        base_url="https://api.openai.com/v1",
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


def test_withdrawn_learning_does_not_disable_runtime_or_reset_spending(
    tmp_path, private_test_ledger
):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    store.forget(now=NOW)
    before = private_test_ledger.summary()
    settings = Settings(
        discord_token="discord-secret",
        openai_api_key="openai-secret",
        learning_store_path=store.path,
        usage_ledger_path=private_test_ledger.path,
    )
    with patch("trubot.app.AsyncOpenAI"):
        client = build_client(settings)
    assert client._learning is None
    assert client._responder is not None
    assert private_test_ledger.summary() == before


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
