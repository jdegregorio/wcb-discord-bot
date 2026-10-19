"""Bounded real capture, backward paging, private checkpoints and failure isolation."""

import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from test_learning import NOW
from test_native_context import message
from test_photos import attached, photo_bytes, photos  # noqa: F401

from trubot.learning import LearningUnavailable
from trubot.photo_history import PhotoHistory, main


@pytest.fixture
def history(photos):  # noqa: F811
    memory, channel, client, _ = photos
    channel.guild.fetch_member = AsyncMock(return_value=SimpleNamespace(id=999))
    channel.permissions_for.return_value = SimpleNamespace(
        view_channel=True, read_message_history=True
    )
    client.user = SimpleNamespace(id=999)
    client.fetch_guild = AsyncMock(return_value=channel.guild)
    client._connection = SimpleNamespace(_add_guild=MagicMock())
    job = PhotoHistory(memory)
    job.initialize(now=NOW)
    return job, channel, client


def page(channel, rows):
    calls = []

    async def history(**kwargs):
        calls.append(kwargs)
        assert kwargs["limit"] == 100 and kwargs["oldest_first"] is False
        for row in rows:
            if row.id < kwargs["before"].id:
                yield row
                if sum(m.id < kwargs["before"].id for m in rows[: rows.index(row) + 1]) == 100:
                    break

    channel.history = history
    return calls


def row(job, channel=10):
    return next(r for r in job.rows() if r["channel"] == channel)


async def test_restart_resumes_backward_without_touching_recent_intake(history):
    job, channel, client = history
    recent_before = job.photos.store.cursors()
    cursor = row(job)["before_id"]
    rows = [message(channel, cursor - n, author=9) for n in range(1, 106)]
    calls = page(channel, rows)
    first = await job.scan(client)
    assert first["scanned"] == 100 and first["pages"] == 1
    assert row(job)["before_id"] == cursor - 100 and row(job)["state"] == "scanning"
    restarted = PhotoHistory(job.photos)
    restarted.initialize(now=NOW + timedelta(days=1))
    second = await restarted.scan(client, pages=2)
    assert second["scanned"] == 5 and row(job)["state"] == "complete"
    assert [call["before"].id for call in calls] == [cursor, cursor - 100]
    assert job.photos.store.cursors() == recent_before
    assert first["provider_calls"] == second["provider_calls"] == 0
    assert row(job, 20)["state"] == "out_of_scope"


async def test_two_real_original_captures_resume_before_unprocessed_third(history):
    job, channel, client = history
    cursor = row(job)["before_id"]
    rows = [attached(channel, cursor - n, created_at=NOW - timedelta(days=200)) for n in (1, 2, 3)]
    page(channel, rows)
    channel.fetch_message.side_effect = lambda mid: next(m for m in rows if m.id == mid)
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())) as download:
        first = await job.scan(client, pages=6)
        assert first["captured"] == 2 and download.await_count == 2
        assert row(job)["before_id"] == rows[1].id
        assert row(job)["state"] == "scanning"
        second = await PhotoHistory(job.photos).scan(client, pages=6)
        assert second["captured"] == 1 and download.await_count == 3
    assert row(job)["state"] == "complete"
    assert len(job.photos.store.rows()) == 3
    for stored in job.photos.store.rows():
        assert stored["author"] == 42 and stored["state"] == "pending"
        assert job.archives.read_asset(stored["asset"]) == photo_bytes()
    job.photos.responder.study_json.assert_not_awaited()
    assert job.photos.learning.store.status()["messages"] == 0


async def test_peer_bot_webhook_embed_and_wrong_channel_never_enter_memory(history):
    job, channel, client = history
    cursor = row(job)["before_id"]
    peer = attached(channel, cursor - 1, author=9)
    bot = attached(channel, cursor - 2, author=42)
    bot.author.bot = True
    hook = attached(channel, cursor - 3, webhook_id=7)
    embed = message(
        channel,
        cursor - 4,
        embeds=[
            SimpleNamespace(
                image=SimpleNamespace(url="https://example.com/a.jpg"),
                thumbnail=SimpleNamespace(url=None),
            )
        ],
    )
    page(channel, [peer, bot, hook, embed])
    job.photos.capture = AsyncMock()
    result = await job.scan(client)
    assert result["scanned"] == 4 and result["captured"] == 0
    job.photos.capture.assert_not_awaited()
    assert [call.args for call in client.fetch_channel.await_args_list] == [(10,), (10,)]


async def test_denied_permission_is_not_empty_complete_and_channel_rounds_are_fair(history):
    job, channel, client = history
    cursor = row(job)["before_id"]
    channel.permissions_for.return_value.read_message_history = False
    channel.history = MagicMock()
    result = await job.scan(client, pages=2)
    assert result["gaps"] == 1 and row(job)["state"] == "unavailable"
    assert row(job)["before_id"] == cursor and row(job, 20)["state"] == "out_of_scope"
    channel.history.assert_not_called()


async def test_permission_lost_after_empty_page_does_not_mark_complete(history):
    job, channel, client = history
    cursor = row(job)["before_id"]
    calls = 0

    async def history(**kwargs):
        nonlocal calls
        calls += 1
        channel.permissions_for.return_value.read_message_history = False
        if False:
            yield

    channel.history = history
    result = await job.scan(client)
    assert result["gaps"] == calls == 1
    assert row(job)["state"] == "unavailable" and row(job)["before_id"] == cursor


async def test_capture_failure_records_gap_advances_and_does_not_retry_automatically(history):
    job, channel, client = history
    cursor = row(job)["before_id"]
    page(channel, [attached(channel, cursor - 1)])
    job.photos.capture = AsyncMock(side_effect=TimeoutError("private URL must not escape"))
    result = await job.scan(client)
    assert result["gaps"] == 1 and result["captured"] == 0
    assert row(job)["before_id"] == cursor - 1 and row(job)["state"] == "complete"
    await job.scan(client, pages=2)
    job.photos.capture.assert_awaited_once()


async def test_capacity_keeps_unprocessed_candidate_open(history):
    job, channel, client = history
    cursor = row(job)["before_id"]
    page(channel, [attached(channel, cursor - 1)])
    job.photos.store.rows = MagicMock(return_value=[{}] * 128)
    job.photos.capture = AsyncMock()
    result = await job.scan(client)
    assert result["captured"] == result["scanned"] == 0
    assert row(job)["state"] == "capacity" and row(job)["before_id"] == cursor
    job.photos.capture.assert_not_awaited()


@pytest.mark.parametrize("pages", [0, 7, True, 1.5])
async def test_unbounded_pages_rejected_before_network(history, pages):
    job, _, client = history
    with pytest.raises(LearningUnavailable):
        await job.scan(client, pages=pages)
    client.fetch_channel.assert_not_awaited()


async def test_withdrawal_during_scan_cannot_checkpoint_or_keep_archive(history):
    job, channel, client = history
    page(channel, [])
    job.photos.learning.store.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        await job.scan(client)
    assert not job.archives.path.exists()
    client.fetch_channel.assert_not_awaited()


def test_job_lock_private_nonblocking_and_symlink_rejected(history, tmp_path):
    job, _, _ = history
    path = job.archives.path.with_name("photo-history.lock")
    with (
        job.exclusive(),
        pytest.raises(LearningUnavailable, match="already running"),
        PhotoHistory(job.photos).exclusive(),
    ):
        pytest.fail("Overlapping job entered")
    assert path.stat().st_mode & 0o077 == 0
    path.unlink()
    target = tmp_path / "target"
    target.write_text("unchanged")
    path.symlink_to(target)
    with pytest.raises(OSError), job.exclusive():
        pytest.fail("Symlink entered")
    assert target.read_text() == "unchanged"


async def test_malformed_page_and_wrong_fetched_channel_fail_closed(history):
    job, channel, client = history
    cursor = row(job)["before_id"]
    page(channel, [message(channel, cursor - 2), message(channel, cursor - 1)])
    with pytest.raises(LearningUnavailable, match="Invalid backward"):
        await job.scan(client)
    assert row(job)["before_id"] == cursor
    channel.id = 99
    with pytest.raises(LearningUnavailable, match="channel mismatch"):
        await job.scan(client)


def test_checkpoint_compare_and_swap_and_no_reinitialization_reset(history):
    job, _, _ = history
    initial = row(job)
    job.checkpoint(
        initial, before=initial["before_id"] - 1, scanned=1, captured=0, gaps=0, state="scanning"
    )
    with pytest.raises(LearningUnavailable, match="checkpoint changed"):
        job.checkpoint(
            initial,
            before=initial["before_id"] - 2,
            scanned=2,
            captured=0,
            gaps=0,
            state="scanning",
        )
    with pytest.raises(LearningUnavailable, match="must not move forward"):
        job.checkpoint(
            initial,
            before=initial["before_id"] + 1,
            scanned=0,
            captured=0,
            gaps=0,
            state="scanning",
        )
    job.initialize(now=NOW + timedelta(days=30))
    assert row(job)["scanned"] == 1 and row(job)["before_id"] == initial["before_id"] - 1
    assert "42" not in json.dumps(job.status())


def test_cli_errors_never_print_private_payload(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["trubot-photo-history", "scan"])
    with (
        patch(
            "trubot.photo_history.run", AsyncMock(side_effect=RuntimeError("private text secret"))
        ),
        pytest.raises(SystemExit) as error,
    ):
        main()
    assert error.value.code == 2
    assert "private text secret" not in capsys.readouterr().err


async def test_network_failure_records_open_gap_and_moves_to_next_channel(history):
    job, _, client = history
    cursor = row(job)["before_id"]
    client.fetch_channel.side_effect = TimeoutError()
    result = await job.scan(client, pages=2)
    assert result["gaps"] == 1 and result["scanned"] == 0
    assert row(job)["state"] == "unavailable" and row(job)["before_id"] == cursor
    assert row(job, 20)["state"] == "out_of_scope"


async def test_source_identity_mismatch_stops_before_network(history):
    job, _, client = history
    with (
        patch.object(job.learning.store, "identity", return_value=object()),
        pytest.raises(LearningUnavailable, match="identity unavailable"),
    ):
        await job.scan(client)
    client.fetch_channel.assert_not_awaited()


async def test_authenticated_http_client_required(history):
    job, _, client = history
    client.user = None
    with pytest.raises(LearningUnavailable, match="Authenticated"):
        await job.scan(client)


async def test_source_guild_and_channel_rows_fail_closed(history):
    job, channel, client = history
    client.fetch_guild.return_value = SimpleNamespace(id=78)
    with pytest.raises(LearningUnavailable, match="guild mismatch"):
        await job.scan(client)
    client.fetch_guild.return_value = channel.guild
    wrong = message(channel, row(job)["before_id"] - 1)
    wrong.guild = SimpleNamespace(id=78)
    page(channel, [wrong])
    with pytest.raises(LearningUnavailable, match="page changed scope"):
        await job.scan(client)


async def test_cli_init_and_status_do_not_connect_or_call_provider(history, tmp_path):
    from trubot.photo_history import run

    job, _, _ = history
    settings = SimpleNamespace(
        learning_store_path=job.learning.store.path,
        learning_retention_days=180,
        allowed_channel_ids=frozenset({10}),
        openai_api_key="synthetic-key",
        openai_model="gpt-6-luna",
        openai_max_output_tokens=256,
        usage_ledger_path=tmp_path / "usage.sqlite3",
    )
    api_context = MagicMock()
    api_context.__aenter__ = AsyncMock(return_value=MagicMock())
    api_context.__aexit__ = AsyncMock()
    with (
        patch("trubot.photo_history.Settings.from_env", return_value=settings),
        patch("trubot.photo_history.AsyncOpenAI", return_value=api_context),
        patch("trubot.photo_history.discord.Client") as discord_client,
    ):
        initial = await run("init", pages=1)
        assert await run("status", pages=1) == initial
    discord_client.assert_not_called()
    api_context.__aenter__.return_value.responses.create.assert_not_called()
