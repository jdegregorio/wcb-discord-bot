"""Interrupted real-smoke work must never become an implicit paid/send retry."""

import asyncio
import importlib.util
import json
import logging
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from test_learning import AUDIT, NOW

from trubot.config import Settings
from trubot.learning import LearningStore, LearningUnavailable


@pytest.fixture
def smoke():
    spec = importlib.util.spec_from_file_location(
        "discord_smoke", Path(__file__).parents[1] / "scripts" / "discord_smoke.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def harness(tmp_path, smoke, monkeypatch):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    settings = Settings(
        discord_token="synthetic-discord-secret",
        openai_api_key="synthetic-openai-secret",
        learning_store_path=store.path,
        ready_file=tmp_path / "live-ready",
    )
    settings.ready_file.write_text("production heartbeat")
    owner, bot = SimpleNamespace(id=11, bot=False), SimpleNamespace(id=99, bot=True)
    guild = SimpleNamespace(id=smoke.GUILD, owner_id=owner.id, approximate_member_count=2)
    guild.fetch_member = AsyncMock(
        side_effect=lambda identifier: owner if identifier == 11 else bot
    )
    guild._add_channel = MagicMock()
    channel = MagicMock(spec=discord.TextChannel)
    channel.id, channel.guild = smoke.CHANNEL, guild
    channel.permissions_for.return_value = SimpleNamespace(
        view_channel=True,
        read_message_history=True,
        send_messages=True,
    )
    guild.fetch_channel = AsyncMock(return_value=channel)
    learning = SimpleNamespace(identity=store.identity(), store=store, verified=True)
    learning.verify_member = AsyncMock()
    learning.accepts = MagicMock(return_value=False)
    client = SimpleNamespace(
        _learning=learning,
        user=SimpleNamespace(id=bot.id, bot=True),
        login=AsyncMock(),
        close=AsyncMock(),
        _connection=SimpleNamespace(_add_guild=MagicMock()),
        fetch_guild=AsyncMock(return_value=guild),
        http=SimpleNamespace(send_message=AsyncMock()),
    )
    posted = {}

    async def transport(_channel_id, *, text):
        identifier = 100 + len(posted)
        posted[identifier] = SimpleNamespace(
            id=identifier,
            content=text,
            author=bot,
            webhook_id=None,
        )
        return {"id": str(identifier), "content": text}

    client.http.send_message.side_effect = transport

    async def send(text, **_kwargs):
        data = await client.http.send_message(channel.id, text=text)
        return posted[int(data["id"])]

    channel.send = AsyncMock(side_effect=send)
    channel.fetch_message = AsyncMock(side_effect=lambda identifier: posted[identifier])

    async def handler(payload):
        assert payload.member is owner
        await channel.send("Synthetic answer only.")

    client.on_raw_reaction_add = AsyncMock(side_effect=handler)

    def factory(isolated, *, spending_purpose):
        assert spending_purpose == "maintenance"
        client._settings = isolated
        return client

    build = MagicMock(side_effect=factory)
    monkeypatch.setattr(smoke, "build_client", build)
    receipt = smoke.Receipt(store, "synthetic-run", "attribution")
    return SimpleNamespace(**locals())


async def test_real_transport_observer_records_exact_send_without_raw_text(harness):
    h = harness
    result = await h.smoke.run(h.settings, h.receipt)
    assert result["state"] == "completed" and result["transport_pass"]
    assert result["probe_id"] == 100 and result["answer_id"] == 101
    assert result["response_count"] == 1 and result["auxiliary_closed"]
    assert result["learning_count_unchanged"] and result["ready_isolated"]
    assert not result["main_gateway_tested"] and not result["human_authored_question"]
    assert h.settings.ready_file.read_text() == "production heartbeat"
    raw = h.receipt.path.read_text()
    for private in ("Synthetic answer", "copied link", "vanilla", "secret"):
        assert private not in raw
    assert h.receipt.path.stat().st_mode & 0o777 == 0o600
    assert h.receipt.directory.stat().st_mode & 0o777 == 0o700
    h.client.close.assert_awaited_once()
    assert h.channel.send.await_count == 2
    assert h.client.http.send_message.await_count == 2
    assert h.receipt.read() == result


@pytest.mark.parametrize(
    "state", ["claimed", "probe_sending", "dispatching", "failed", "completed"]
)
async def test_any_prior_claim_prevents_another_client_or_attempt(harness, state):
    h = harness
    record, fresh = h.receipt.claim()
    assert fresh
    record["state"] = state
    h.receipt.save(record)
    assert (await h.smoke.run(h.settings, h.receipt))["state"] == state
    h.build.assert_not_called()
    h.channel.send.assert_not_awaited()


async def test_ambiguous_probe_send_is_consumed_even_without_returned_id(harness):
    h = harness
    h.client.http.send_message.side_effect = TimeoutError("private transport body")
    result = await h.smoke.run(h.settings, h.receipt)
    assert result["state"] == "uncertain" and "probe_id" not in result
    assert "private transport body" not in h.receipt.path.read_text()
    h.build.reset_mock()
    await h.smoke.run(h.settings, h.receipt)
    h.build.assert_not_called()
    assert h.client.http.send_message.await_count == 1
    h.client.close.assert_awaited_once()


async def test_cancellation_after_actual_answer_keeps_exact_reference_and_never_resends(harness):
    h = harness

    async def interrupted(_payload):
        await h.channel.send("Synthetic answer only.")
        raise asyncio.CancelledError

    h.client.on_raw_reaction_add.side_effect = interrupted
    result = await h.smoke.run(h.settings, h.receipt)
    assert result["state"] == "uncertain" and result["answer_id"] == 101
    assert result["response_count"] == 1
    h.build.reset_mock()
    await h.smoke.run(h.settings, h.receipt)
    h.build.assert_not_called()
    assert h.channel.send.await_count == 2
    h.client.close.assert_awaited_once()


async def test_receipt_failure_after_real_send_cannot_trigger_handler_fallback(
    harness, monkeypatch
):
    h = harness
    save = h.receipt.save
    failed = False

    def fail_once(record):
        nonlocal failed
        if "answer_id" in record and not failed:
            failed = True
            raise OSError("private disk path")
        save(record)

    monkeypatch.setattr(h.receipt, "save", fail_once)
    result = await h.smoke.run(h.settings, h.receipt)
    assert failed and result["state"] == "uncertain" and not result["transport_pass"]
    assert h.channel.send.await_count == 2
    assert "private disk path" not in h.receipt.path.read_text()


@pytest.mark.parametrize(
    "defect",
    [
        "guild",
        "members",
        "owner",
        "owner_id",
        "bot_id",
        "channel_id",
        "permissions",
        "learning",
        "allowlist",
    ],
)
async def test_scope_failure_closes_client_before_any_discord_write(harness, defect):
    h = harness
    if defect == "guild":
        h.guild.id = 777
    elif defect == "members":
        h.guild.approximate_member_count = 3
    elif defect == "owner":
        h.owner.bot = True
    elif defect == "owner_id":
        h.owner.id = 123
    elif defect == "bot_id":
        h.bot.id = 123
    elif defect == "channel_id":
        h.channel.id += 1
    elif defect == "permissions":
        h.channel.permissions_for.return_value.send_messages = False
    elif defect == "learning":
        h.learning.accepts.return_value = True
    else:
        h.settings = replace(h.settings, allowed_channel_ids=frozenset({9}))
    result = await h.smoke.run(h.settings, h.receipt)
    assert result["state"] == "failed" and not result["transport_pass"]
    h.channel.send.assert_not_awaited()
    h.client.close.assert_awaited_once()


def test_unsafe_identity_symlink_and_malformed_receipt_never_create_new_attempt(harness):
    h = harness
    with pytest.raises(ValueError):
        h.smoke.Receipt(h.store, "../escape", "attribution")
    h.receipt.claim()
    h.receipt.path.unlink()
    outside = h.tmp_path / "outside"
    outside.write_text("untouched")
    h.receipt.path.symlink_to(outside)
    with pytest.raises(LearningUnavailable):
        h.receipt.claim()
    assert outside.read_text() == "untouched"
    h.receipt.path.unlink()
    h.receipt.path.write_text(json.dumps({"state": "completed", "raw": "private text"}))
    h.receipt.path.chmod(0o600)
    with pytest.raises(ValueError):
        h.receipt.claim()


def test_withdrawal_blocks_receipt_inspection_and_new_work(harness):
    h = harness
    h.receipt.claim()
    h.store.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        h.receipt.read()
    with pytest.raises(LearningUnavailable):
        h.receipt.claim()


def test_concurrent_claims_have_exactly_one_winner(harness):
    from concurrent.futures import ThreadPoolExecutor

    h = harness

    def claim(_index):
        try:
            return h.receipt.claim()[1]
        except ValueError:
            # Another process may still be writing its initial exclusive claim.
            # Unreadable state fails closed instead of becoming permission to run.
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(claim, range(8))) == 1
    assert h.receipt.read()["state"] == "claimed"


def test_cli_failure_never_prints_private_exception_body(harness, monkeypatch, capsys):
    h = harness
    monkeypatch.setattr(
        "sys.argv", ["discord_smoke.py", "status", "--run-id", "safe", "--case", "care"]
    )
    monkeypatch.setattr(
        h.smoke.Settings, "from_env", MagicMock(side_effect=RuntimeError("secret-body"))
    )
    before = logging.root.manager.disable
    assert h.smoke.main() == 1
    assert logging.root.manager.disable == before
    assert json.loads(capsys.readouterr().out) == {"error": "smoke_unavailable"}


async def test_handler_cannot_send_to_another_destination(harness):
    h = harness

    async def wrong_destination(_payload):
        await h.client.http.send_message(999, text="must never reach Discord")

    h.client.on_raw_reaction_add.side_effect = wrong_destination
    result = await h.smoke.run(h.settings, h.receipt)
    assert result["state"] == "uncertain"
    # The only actual transport call is the labeled private development probe.
    assert h.client.http.send_message.await_count == 1
    assert len(h.posted) == 1


@pytest.mark.parametrize("stage", ["claimed", "dispatching"])
async def test_hard_process_exit_preserves_claim_and_prevents_replay(harness, stage):
    h = harness
    # Exit without Python cleanup to exercise the on-disk interruption boundary.
    code = """
import importlib.util
import os
import sys
from pathlib import Path
from trubot.learning import LearningStore
spec = importlib.util.spec_from_file_location("smoke", sys.argv[1])
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)
receipt = smoke.Receipt(LearningStore(Path(sys.argv[2])), "synthetic-run", "attribution")
record, fresh = receipt.claim()
assert fresh
record["state"] = sys.argv[3]
if record["state"] == "dispatching":
    record["probe_id"] = 100
    receipt.save(record)
os._exit(19)
"""
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        code,
        h.smoke.__file__,
        str(h.store.path),
        stage,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        _, stderr = await asyncio.wait_for(process.communicate(), timeout=15)
    finally:
        if process.returncode is None:
            process.kill()
            await process.wait()
    assert process.returncode == 19, stderr.decode()
    record = h.receipt.read()
    assert record["state"] == stage
    assert await h.smoke.run(h.settings, h.receipt) == record
    h.build.assert_not_called()
    h.channel.send.assert_not_awaited()
    assert h.settings.ready_file.read_text() == "production heartbeat"
