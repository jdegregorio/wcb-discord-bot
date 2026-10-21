"""Production-heartbeat survival across the real auxiliary-client lifecycle."""

from dataclasses import replace
from unittest.mock import AsyncMock, patch

import pytest

from trubot.app import build_client
from trubot.config import Settings
from trubot.health import is_ready


def settings_for(tmp_path, ledger):
    return Settings(
        discord_token="discord-secret",
        openai_api_key="openai-secret",
        usage_ledger_path=ledger.path,
        learning_store_path=tmp_path / "missing-learning.sqlite3",
        ready_file=tmp_path / "live-ready",
    )


def heartbeat_snapshot(path):
    stat = path.stat()
    return path.read_bytes(), stat.st_ino, stat.st_mtime_ns


@pytest.mark.parametrize("started", [False, True])
async def test_maintenance_close_preserves_live_heartbeat(tmp_path, private_test_ledger, started):
    settings = settings_for(tmp_path, private_test_ledger)
    settings.ready_file.write_bytes(b"live gateway heartbeat")
    snapshot = heartbeat_snapshot(settings.ready_file)
    before = private_test_ledger.summary()
    with patch("trubot.app.AsyncOpenAI") as api:
        api.return_value.close = AsyncMock()
        api.return_value.with_options.return_value = api.return_value
        client = build_client(settings, spending_purpose="maintenance")
        try:
            if started:
                await client._readiness.start()
                assert is_ready(client._readiness.path, 180)
        finally:
            await client.close()
    assert heartbeat_snapshot(settings.ready_file) == snapshot
    assert is_ready(settings.ready_file, 180)
    assert not client._readiness.path.exists()
    assert private_test_ledger.summary() == before
    assert client._settings.ready_file == client._readiness.path
    assert client._settings.usage_ledger_path == settings.usage_ledger_path
    assert client._settings.learning_store_path == settings.learning_store_path
    assert client._responder._purpose == "maintenance"
    api.return_value.close.assert_awaited_once()


async def test_two_maintenance_clients_cannot_clear_each_others_readiness(
    tmp_path, private_test_ledger
):
    settings = settings_for(tmp_path, private_test_ledger)
    with patch("trubot.app.AsyncOpenAI") as api:
        api.return_value.close = AsyncMock()
        api.return_value.with_options.return_value = api.return_value
        first = build_client(settings, spending_purpose="maintenance")
        second = build_client(settings, spending_purpose="maintenance")
        try:
            await first._readiness.start()
            await second._readiness.start()
            second_before = heartbeat_snapshot(second._readiness.path)
            await first.close()
            assert heartbeat_snapshot(second._readiness.path) == second_before
            assert is_ready(second._readiness.path, 180)
            assert not first._readiness.path.exists()
        finally:
            await first.close()
            await second.close()
    assert not second._readiness.path.exists()
    assert settings.ready_file == tmp_path / "live-ready"


async def test_failed_evaluation_cleanup_leaves_live_client_ready(tmp_path, private_test_ledger):
    settings = settings_for(tmp_path, private_test_ledger)
    with patch("trubot.app.AsyncOpenAI") as api:
        api.return_value.close = AsyncMock()
        api.return_value.with_options.return_value = api.return_value
        live = build_client(settings)
        study = build_client(settings, spending_purpose="maintenance")
        try:
            await live._readiness.start()
            before = heartbeat_snapshot(live._readiness.path)
            with pytest.raises(RuntimeError, match="study stopped"):
                try:
                    raise RuntimeError("study stopped")
                finally:
                    await study.close()
            assert heartbeat_snapshot(live._readiness.path) == before
            assert live._settings is settings
            assert live._readiness.path == settings.ready_file
            assert is_ready(settings.ready_file, 180)
        finally:
            await study.close()
            await live.close()
    assert not settings.ready_file.exists()


async def test_maintenance_settings_keep_source_and_generation_configuration(
    tmp_path, private_test_ledger
):
    settings = settings_for(tmp_path, private_test_ledger)
    with patch("trubot.app.AsyncOpenAI") as api:
        api.return_value.close = AsyncMock()
        api.return_value.with_options.return_value = api.return_value
        client = build_client(settings, spending_purpose="maintenance")
        try:
            isolated = client._settings
            assert replace(isolated, ready_file=settings.ready_file) == settings
            assert isolated.ready_file.is_absolute()
            assert not isolated.ready_file.exists()
            assert isolated.ready_file != settings.ready_file
        finally:
            await client.close()


async def test_explicit_runtime_readiness_path_is_preserved(tmp_path, private_test_ledger):
    settings = settings_for(tmp_path, private_test_ledger)
    with patch("trubot.app.AsyncOpenAI") as api:
        api.return_value.close = AsyncMock()
        api.return_value.with_options.return_value = api.return_value
        client = build_client(settings, spending_purpose="runtime")
        try:
            assert client._readiness.path == settings.ready_file
            await client._readiness.start()
            assert settings.ready_file.exists()
        finally:
            await client.close()
    assert not settings.ready_file.exists()
