import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from test_aurora import generator
from test_context_tools import Provider, responder, response
from test_discord_client import make_client

from trubot.aurora_image import AuroraImage
from trubot.budget import UsageLedger
from trubot.learning import LearningUnavailable
from trubot.outdoors import (
    FORECAST_URL,
    LIFE_SCENES,
    Forecast,
    OutdoorFeature,
    OutdoorStore,
    forecast,
    main,
    posting_window,
    read_forecast,
    seasonal_scenes,
)
from trubot.requested_scenes import requested_region
from trubot.up_conditions import UPConditionsSkill

NOW = datetime(2026, 10, 18, 17, tzinfo=UTC)
IMAGE = AuroraImage(b"png", "Winter can take its time.\n-# AI-generated U.P. scene.", "Generated.")


def feed(kp=6):
    return [
        {"time_tag": (NOW - timedelta(hours=3)).isoformat(), "kp": 2, "observed": "observed"},
        {"time_tag": NOW.isoformat(), "kp": kp, "observed": "estimated"},
        {"time_tag": (NOW + timedelta(hours=3)).isoformat(), "kp": kp, "observed": "predicted"},
    ]


@pytest.fixture
def store(tmp_path):
    tmp_path.chmod(0o700)
    return OutdoorStore.initialize(tmp_path / "outdoors.sqlite3", now=NOW - timedelta(days=8))


def test_wake_atomic_across_clients_and_threads(store):
    with ThreadPoolExecutor(4) as pool:
        keys = list(pool.map(lambda _: OutdoorStore(store.path).wake(NOW), range(4)))
    assert sum(k is not None for k in keys) == 1
    assert not store.due(NOW - timedelta(days=1))
    assert not store.due(NOW + timedelta(minutes=239))
    assert store.due(NOW + timedelta(hours=4))
    assert not store.wake(NOW + timedelta(seconds=1))
    assert store.summary()["outcomes"] == {"quiet": 1}


def test_initial_week_quiet_and_clock_rollback(tmp_path):
    tmp_path.chmod(0o700)
    store = OutdoorStore.initialize(tmp_path / "new.sqlite3", now=NOW)
    key = store.wake(NOW)
    assert store.reflect(key, now=NOW, signal=Forecast("available")) is None
    assert not store.due(NOW - timedelta(seconds=1))
    assert store.summary()["next_wake_utc"] == (NOW + timedelta(hours=4)).isoformat()
    with pytest.raises(FileExistsError):
        OutdoorStore.initialize(store.path)


def test_weekly_attempt_limit_rotation_and_terminal_claims(store):
    key = store.wake(NOW)
    first = store.reflect(key, now=NOW, signal=Forecast("unavailable"))
    assert first.scene == "woodpile"
    store.finish(key, "failed")
    assert store.reflect(key, now=NOW, signal=Forecast("available")) is None
    later = NOW + timedelta(days=6)
    assert store.reflect(store.wake(later), now=later, signal=Forecast("available")) is None
    later = NOW + timedelta(days=7)
    second = store.reflect(store.wake(later), now=later, signal=Forecast("available"))
    assert second.scene == "trail_camera"
    store.finish(second.morning, "send_uncertain")
    store.finish(second.morning, "posted", 123)
    with pytest.raises(LearningUnavailable):
        store.finish(second.morning, "failed")
    with pytest.raises(ValueError):
        store.finish(second.morning, "retry")
    assert store.summary()["outcomes"] == {"failed": 1, "posted": 1, "quiet": 1}


@pytest.mark.parametrize(
    ("minutes", "status", "promising", "hour", "expected"),
    [
        (20, "available", True, 2, 20),
        (20, "unavailable", True, 2, 60),
        (20, "available", True, 17, 60),
        (60, "available", False, 2, 60),
        (480, "available", True, 2, 480),
    ],
)
def test_private_plan_clamped_without_confirmed_sighting(
    store, minutes, status, promising, hour, expected
):
    now = NOW.replace(hour=hour)
    key = store.wake(now)
    assert (
        store.reflect(
            key,
            now=now,
            signal=Forecast(status, promising),
            next_minutes=minutes,
            consider_scene=False,
        )
        is None
    )
    assert store.summary()["next_wake_utc"] == (now + timedelta(minutes=expected)).isoformat()
    assert store.summary()["outcomes"] == {"quiet": 1}
    assert store.summary()["aurora_confirmation"] == "unavailable_no_automatic_aurora_posts"


def test_stale_reflection_cannot_rewrite_newer_schedule(store):
    first = store.wake(NOW)
    second = store.wake(NOW + timedelta(hours=4))
    assert store.reflect(first, now=NOW, signal=Forecast("available", True)) is None
    assert (
        store.reflect(
            second, now=NOW + timedelta(hours=4), signal=Forecast("available"), consider_scene=False
        )
        is None
    )
    with pytest.raises(ValueError):
        store.reflect(second, now=NOW, signal=Forecast("available"), next_minutes=True)


@pytest.mark.parametrize(
    ("month", "scene"),
    [(10, "woodpile"), (1, "lake_freeze"), (4, "lake_thaw"), (7, "trail_camera")],
)
def test_seasonal_catalog_and_post_hours(month, scene):
    assert seasonal_scenes(NOW.replace(month=month))[0] == scene
    assert posting_window(NOW)
    assert not posting_window(NOW.replace(hour=1))
    assert not posting_window(NOW.replace(hour=10))


@pytest.mark.parametrize("bad", [None, [], {}, [None], [{}], [{}] * 101])
def test_malformed_forecast_is_unknown(bad):
    assert forecast(bad, NOW) == Forecast("unavailable")


@pytest.mark.parametrize(
    "change",
    [{"kp": True}, {"kp": 10}, {"kp": float("nan")}, {"observed": "mystery"}, {"time_tag": "bad"}],
)
def test_invalid_values_cannot_trigger_rapid_checks(change):
    assert forecast([{**r, **change} for r in feed()], NOW) == Forecast("unavailable")


def test_freshness_future_only_duplicates_and_quiet_forecast():
    assert forecast(feed(), NOW) == Forecast("available", True)
    assert forecast(feed(1), NOW) == Forecast("available", False)
    assert forecast(feed(), NOW + timedelta(days=2)) == Forecast("unavailable")
    assert forecast(feed() * 2, NOW) == Forecast("unavailable")
    assert forecast([feed()[2]], NOW) == Forecast("unavailable")
    assert forecast([feed()[0]], NOW) == Forecast("unavailable")


async def test_fixed_bounded_forecast_and_outage():
    with patch("trubot.outdoors._fetch", AsyncMock(return_value=feed())) as fetch:
        assert await read_forecast(now=NOW) == Forecast("available", True)
        assert fetch.call_args.args[1] == FORECAST_URL
    for error in [TimeoutError(), ValueError("bad json")]:
        with patch("trubot.outdoors._fetch", AsyncMock(side_effect=error)):
            assert await read_forecast(now=NOW) == Forecast("unavailable")


async def test_quiet_planning_is_independent_of_image_calls_and_restarts(store):
    images = SimpleNamespace(generate_life=AsyncMock(return_value=IMAGE))
    planner = AsyncMock(return_value=(480, False))
    collect = AsyncMock(return_value=Forecast("available", True))
    feature = OutdoorFeature(store, images, collect=collect, planner=planner)
    assert await feature.prepare(now=NOW) is None
    images.generate_life.assert_not_awaited()
    planner.assert_awaited_once()
    assert (
        await OutdoorFeature(OutdoorStore(store.path), images, collect=collect).prepare(
            now=NOW + timedelta(minutes=30)
        )
        is None
    )
    assert collect.await_count == 1
    assert store.summary()["outcomes"] == {"quiet": 1}


@pytest.mark.parametrize("failure", ["timing", "provider", "cancel", "planner"])
async def test_failure_never_retries_paid_image(store, failure):
    images = SimpleNamespace(generate_life=AsyncMock(return_value=IMAGE))
    planner = AsyncMock(return_value=(240, True))
    if failure in {"provider", "cancel"}:
        images.generate_life.side_effect = (
            RuntimeError if failure == "provider" else asyncio.CancelledError
        )
    if failure == "planner":
        planner.side_effect = ValueError
    feature = OutdoorFeature(
        store, images, collect=AsyncMock(return_value=Forecast("available")), planner=planner
    )
    try:
        result = await feature.prepare(
            now=NOW, before_generation=AsyncMock(return_value=failure != "timing")
        )
        assert result is None
    except (RuntimeError, ValueError, asyncio.CancelledError):
        assert failure != "timing"
    assert await feature.prepare(now=NOW + timedelta(seconds=1)) is None
    assert images.generate_life.await_count == (1 if failure in {"provider", "cancel"} else 0)


@pytest.mark.parametrize("kind", sorted(LIFE_SCENES))
async def test_each_scene_uses_existing_accounted_adapter_and_provenance(private_test_ledger, kind):
    gen, client = generator(private_test_ledger)
    image = await gen.generate_requested(kind, purpose="maintenance")
    assert image.data and len(image.caption.splitlines()[0]) < 40
    assert "AI-generated" in image.caption and "Not a real photo" in image.description
    prompt = client.images.generate.call_args.kwargs["prompt"]
    assert "Michigan" in prompt and len(prompt.encode()) <= 2000
    assert private_test_ledger.summary()["attempts"] == 1
    if kind == "lake_freeze":
        assert "Not Lake Superior" in prompt and "safe to walk on" in prompt
    with pytest.raises(ValueError):
        await gen.generate_life("untrusted scene")


@pytest.mark.parametrize(
    ("phrase", "kind"),
    [
        ("🤖 Generate a woodpile picture in the UP.", "woodpile"),
        ("Create a trail-camera image in the Upper Peninsula.", "trail_camera"),
        ("Make an original lake freezing scene in the UP.", "lake_freeze"),
        ("Please draw a lake thawing illustration in the U.P.", "lake_thaw"),
        ("Don't generate a woodpile picture in the UP.", None),
        ("Sam, generate a woodpile picture in the UP.", None),
        ("Generate a woodpile picture in the UP of my house.", None),
        ("Generate a real trail-camera image in the UP.", None),
        ("Generate a lake freezing picture in the UP and call it real.", None),
    ],
)
def test_closed_scene_grammar(phrase, kind):
    assert requested_region(phrase, bot_user_id=999) == kind


@pytest.mark.parametrize(
    "data",
    [
        {"next_check_minutes": 240, "consider_scene": False},
        {"next_check_minutes": 20, "consider_scene": True},
        {"next_check_minutes": True, "consider_scene": False},
        {"next_check_minutes": 1, "consider_scene": False},
        {"next_check_minutes": 240, "consider_scene": "yes"},
    ],
)
async def test_private_planner_contract_and_same_ledger(tmp_path, data):
    provider = Provider([response(json.dumps(data))])
    r = responder(provider, UsageLedger(tmp_path / "usage.sqlite3"), UPConditionsSkill())
    valid = (
        type(data["next_check_minutes"]) is int
        and data["next_check_minutes"] in {20, 60, 240, 480}
        and type(data["consider_scene"]) is bool
    )
    if valid:
        assert await r.plan_outdoor_check(Forecast("available", True), NOW) == (
            data["next_check_minutes"],
            data["consider_scene"],
        )
    else:
        with pytest.raises(ValueError):
            await r.plan_outdoor_check(Forecast("available"), NOW)
    req = provider.requests[0]
    assert req["store"] is False and "tools" not in req
    assert req["text"]["format"]["strict"] is True
    assert r._budget.summary()["attempts"] == 1


def test_missing_unsafe_schema_retention_and_cli(store, tmp_path, monkeypatch, capsys):
    with pytest.raises(FileNotFoundError):
        OutdoorStore(tmp_path / "absent").due(NOW)
    store.wake(NOW)
    store.wake(NOW + timedelta(days=40))
    assert store.summary()["wakes"] == 1
    monkeypatch.setattr("sys.argv", ["trubot-outdoors", "status", "--path", str(store.path)])
    main()
    assert json.loads(capsys.readouterr().out)["wakes"] == 1
    with store.transaction() as db:
        db.execute("DELETE FROM plan")
    for call in (lambda: store.due(NOW), lambda: store.wake(NOW), store.summary):
        with pytest.raises(LearningUnavailable):
            call()
    with store.transaction() as db:
        db.execute("PRAGMA user_version=2")
    with pytest.raises(LearningUnavailable):
        store.due(NOW)
    with pytest.raises(SystemExit):
        main()
    store.path.chmod(0o644)
    with pytest.raises(LearningUnavailable):
        store.due(NOW)
    unsafe = tmp_path / "unsafe"
    unsafe.mkdir(mode=0o755)
    with pytest.raises(LearningUnavailable):
        OutdoorStore.initialize(unsafe / "state")


async def test_real_handler_sends_once_and_context_race_defers(store):
    from dataclasses import replace

    client, _, _, tracker = make_client(clock=lambda: NOW)
    client._settings = replace(client._settings, aurora_channel_id=10)
    images = SimpleNamespace(generate_life=AsyncMock(return_value=IMAGE))
    client._aurora = OutdoorFeature(
        store, images, collect=AsyncMock(return_value=Forecast("available"))
    )
    channel = MagicMock(spec=discord.TextChannel)
    channel.id = 10
    channel.send = AsyncMock(return_value=SimpleNamespace(id=555))
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch.object(client, "_outdoor_scope_current", AsyncMock(return_value=True)),
        patch.object(client, "_aurora_channel_ready", AsyncMock(return_value=True)),
        patch.object(client, "_aurora_timing_ok", AsyncMock(return_value=True)),
        patch.object(
            client, "_outdoor_context_stamp", AsyncMock(return_value=((1, "unchanged", "quiet"),))
        ),
    ):
        assert await client._aurora_cycle()
        assert not await client._aurora_cycle()
    assert channel.send.await_count == images.generate_life.await_count == 1
    assert isinstance(channel.send.call_args.kwargs["nonce"], int)
    assert store.summary()["outcomes"] == {"posted": 1}
    assert tracker.snapshot(10, NOW).ambient_replies_today == 1
    await client.close()


@pytest.mark.parametrize("boundary", [0, 1])
async def test_withdrawal_or_access_loss_stops_public_and_paid_checks(store, boundary):
    collect = AsyncMock(return_value=Forecast("available"))
    planner = AsyncMock(return_value=(240, True))
    images = SimpleNamespace(generate_life=AsyncMock())
    checks = AsyncMock(side_effect=[False] if boundary == 0 else [True, False])
    feature = OutdoorFeature(store, images, collect=collect, planner=planner)
    assert await feature.prepare(now=NOW, before_check=checks) is None
    assert await feature.prepare(now=NOW + timedelta(minutes=1), before_check=checks) is None
    assert collect.await_count == boundary
    planner.assert_not_awaited()
    images.generate_life.assert_not_awaited()
    assert store.summary()["next_wake_utc"] == (NOW + timedelta(hours=4)).isoformat()


@pytest.mark.parametrize("failure", ["context", "activity", "send"])
async def test_generation_and_publication_races_remain_closed(store, failure):
    from dataclasses import replace

    client, _, _, _ = make_client(clock=lambda: NOW)
    client._settings = replace(client._settings, aurora_channel_id=10)
    images = SimpleNamespace(generate_life=AsyncMock(return_value=IMAGE))
    client._aurora = OutdoorFeature(
        store, images, collect=AsyncMock(return_value=Forecast("available"))
    )
    channel = MagicMock(spec=discord.TextChannel)
    channel.id = 10
    channel.send = AsyncMock(side_effect=RuntimeError if failure == "send" else None)
    ready = AsyncMock(side_effect=[True, failure != "activity"])
    stamp = AsyncMock(
        side_effect=[
            ((1, "before", "quiet"),),
            ((1, "after" if failure == "context" else "before", "quiet"),),
        ]
    )
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch.object(client, "_outdoor_scope_current", AsyncMock(return_value=True)),
        patch.object(client, "_aurora_channel_ready", ready),
        patch.object(client, "_aurora_timing_ok", AsyncMock(return_value=True)),
        patch.object(client, "_outdoor_context_stamp", stamp),
    ):
        if failure == "send":
            with pytest.raises(RuntimeError):
                await client._aurora_cycle()
        else:
            assert not await client._aurora_cycle()
        assert not await client._aurora_cycle()
    assert images.generate_life.await_count == 1
    assert channel.send.await_count == (failure == "send")
    assert store.summary()["outcomes"] == {"send_uncertain" if failure == "send" else "deferred": 1}
    await client.close()


@pytest.mark.parametrize("allowed", [True, False])
async def test_fresh_permissions_and_context_fingerprint(store, allowed):
    from dataclasses import replace

    client, _, _, _ = make_client(clock=lambda: NOW)
    client._settings = replace(client._settings, aurora_channel_id=10)
    identity = SimpleNamespace(guild_id=77)
    client._learning = SimpleNamespace(
        verified=True, identity=identity, store=SimpleNamespace(identity=lambda: identity)
    )
    client._aurora = OutdoorFeature(store, SimpleNamespace(generate_life=AsyncMock()))
    channel = MagicMock(spec=discord.TextChannel)
    channel.id = 10
    channel.guild = MagicMock()
    channel.guild.id = 77
    channel.guild.fetch_channel = AsyncMock(return_value=channel)
    channel.guild.fetch_member = AsyncMock(return_value=object())
    channel.permissions_for = MagicMock(
        return_value=SimpleNamespace(
            view_channel=True, read_message_history=True, send_messages=True, attach_files=allowed
        )
    )
    row = SimpleNamespace(
        id=123,
        edited_at=None,
        content="ordinary discussion",
        author=SimpleNamespace(id=1),
        attachments=[],
        embeds=[],
        created_at=NOW - timedelta(hours=1),
    )

    async def history(**kwargs):
        yield row

    channel.history = history
    with patch.object(
        type(client), "user", new_callable=lambda: property(lambda _: SimpleNamespace(id=999))
    ):
        assert await client._outdoor_scope_current(channel) is allowed
        assert await client._aurora_channel_ready(channel) is allowed
    first = await client._outdoor_context_stamp(channel)
    row.content = "Changed sensitive discussion"
    assert first != await client._outdoor_context_stamp(channel)
    assert channel.guild.fetch_channel.await_count == 2
    await client.close()


@pytest.mark.parametrize(
    "text,status",
    [
        ("[]", "completed"),
        ("{}", "completed"),
        ('{"next_check_minutes":240,"consider_scene":false,"extra":1}', "completed"),
        ('{"next_check_minutes":240,"consider_scene":false}', "incomplete"),
    ],
)
async def test_malformed_planner_cannot_authorize_anything(tmp_path, text, status):
    provider = Provider([response(text, status=status)])
    r = responder(provider, UsageLedger(tmp_path / "usage.sqlite3"), UPConditionsSkill())
    with pytest.raises(ValueError):
        await r.plan_outdoor_check(Forecast("available"), NOW)
    assert len(provider.requests) == 1


def test_app_wires_private_planner_and_preserves_opt_in(private_test_ledger):
    from trubot.app import build_client
    from trubot.config import Settings

    settings = Settings(
        discord_token="test",
        openai_api_key="test",
        allowed_channel_ids=frozenset({10}),
        aurora_channel_id=10,
        usage_ledger_path=private_test_ledger.path,
    )
    with patch("trubot.app.AsyncOpenAI"):
        client = build_client(settings)
    assert isinstance(client._aurora, OutdoorFeature)
    assert client._aurora.planner == client._responder.plan_outdoor_check
    assert client._aurora.store.path.name == "outdoors.sqlite3"


async def test_planner_spending_rejection_makes_no_provider_or_image_attempt(store, tmp_path):
    from trubot.budget import BudgetExceeded

    provider = Provider([])
    r = responder(provider, UsageLedger(tmp_path / "usage.sqlite3"), UPConditionsSkill())
    images = SimpleNamespace(generate_life=AsyncMock())
    feature = OutdoorFeature(
        store,
        images,
        collect=AsyncMock(return_value=Forecast("available", True)),
        planner=r.plan_outdoor_check,
    )
    with (
        patch.object(r._budget, "reserve", side_effect=BudgetExceeded("Monthly limit reached")),
        pytest.raises(BudgetExceeded),
    ):
        await feature.prepare(now=NOW)
    assert provider.requests == []
    images.generate_life.assert_not_awaited()
    # A reconstructed worker respects the pre-I/O safe fallback rather than retrying.
    assert (
        await OutdoorFeature(OutdoorStore(store.path), images).prepare(
            now=NOW + timedelta(minutes=1)
        )
        is None
    )
    assert store.summary()["reasons"] == {"check_failed": 1}


@pytest.mark.parametrize(
    ("hour", "minute", "allowed"), [(12, 59, False), (13, 0, True), (0, 59, True), (1, 0, False)]
)
def test_seasonal_post_window_exact_boundaries_in_detroit(hour, minute, allowed):
    # October UTC is four hours ahead. Midnight UTC is still the preceding day.
    assert posting_window(NOW.replace(hour=hour, minute=minute)) is allowed
