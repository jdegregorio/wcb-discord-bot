import asyncio
import io
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from openai import AsyncOpenAI
from PIL import Image
from test_discord_client import make_client

from trubot.aurora import (
    REGIONS,
    AuroraStore,
    Opportunity,
    collect_opportunity,
    main,
    morning_window,
    select_opportunity,
    solar_elevation,
)
from trubot.aurora_feature import AuroraFeature
from trubot.aurora_image import AuroraImage, AuroraImageGenerator
from trubot.budget import BudgetExceeded, BudgetUnavailable
from trubot.config import ConfigurationError, Settings
from trubot.learning import LearningUnavailable

NOW = datetime(2026, 10, 17, 12, tzinfo=UTC)
OBSERVED = datetime(2026, 10, 17, 3, tzinfo=UTC)
OPPORTUNITY = Opportunity(
    "2026-10-17",
    "KCMX",
    "the Keweenaw",
    5.33,
    (
        OBSERVED.isoformat(),
        (OBSERVED + timedelta(minutes=45)).isoformat(),
    ),
)


def activity(kp=5.33):
    return [
        {"time_tag": "2026-10-17T03:00:00", "Kp": kp, "station_count": 8},
        {"time_tag": "2026-10-17T09:00:00", "Kp": 1, "station_count": 8},
    ]


def weather(at=OBSERVED):
    return {
        "properties": {
            "timestamp": at.isoformat(),
            "cloudLayers": [{"amount": "CLR"}],
            "visibility": {"unitCode": "wmoUnit:m", "value": 16093, "qualityControl": "C"},
            "presentWeather": [],
        }
    }


def feeds():
    return {"KCMX": {"features": [weather(), weather(OBSERVED + timedelta(minutes=45))]}}


@pytest.fixture
def store(tmp_path):
    tmp_path.chmod(0o700)
    return AuroraStore.initialize(tmp_path / "aurora.sqlite3")


def test_qualifying_overlapping_night_and_quiet_baseline():
    result = select_opportunity(activity(), feeds(), now=NOW)
    assert result == OPPORTUNITY
    assert select_opportunity(activity(4.99), feeds(), now=NOW) is None
    assert select_opportunity(activity(), feeds(), now=NOW + timedelta(hours=4)) is None


@pytest.mark.parametrize("hour", [0, 7, 11, 23])
def test_local_morning_only(hour):
    assert morning_window(NOW.replace(hour=hour + 4 if hour < 20 else 23)) is None


@pytest.mark.parametrize(("day", "hours"), [("2026-03-08", 11), ("2026-11-01", 13)])
def test_dst_window_is_calendar_based(day, hours):
    now = datetime.fromisoformat(day + "T14:00:00+00:00")
    start, end = morning_window(now)
    assert (end - start).total_seconds() == hours * 3600


def test_darkness_summer_day_and_night():
    assert solar_elevation(datetime(2026, 6, 21, 18, tzinfo=UTC), REGIONS[0]) > 60
    assert solar_elevation(datetime(2026, 6, 21, 5, tzinfo=UTC), REGIONS[0]) < -12
    assert solar_elevation(datetime(2026, 6, 21, 1, tzinfo=UTC), REGIONS[0]) > -12
    with pytest.raises(ValueError):
        morning_window(NOW.replace(tzinfo=None))


@pytest.mark.parametrize(
    "change",
    [
        {"cloudLayers": []},
        {"cloudLayers": None},
        {"cloudLayers": [{"amount": "BKN"}]},
        {"cloudLayers": [{"amount": "VV"}]},
        {"cloudLayers": [{"amount": "CLR"}, {"amount": "OVC"}]},
        {"presentWeather": None},
        {"presentWeather": [{"weather": "rain"}]},
        {"visibility": {"unitCode": "wmoUnit:m", "value": None, "qualityControl": "C"}},
        {"visibility": {"unitCode": "wmoUnit:m", "value": 7999, "qualityControl": "C"}},
        {"visibility": {"unitCode": "wmoUnit:m", "value": 10000, "qualityControl": "Z"}},
        {"visibility": {"unitCode": "wmoUnit:mi", "value": 10000, "qualityControl": "C"}},
        {"visibility": {"unitCode": "wmoUnit:m", "value": float("nan"), "qualityControl": "C"}},
        {"timestamp": "2026-10-17T03:00:00"},
        {"timestamp": "bad"},
        {"timestamp": "2026-10-17T07:00:00+00:00"},
    ],
)
def test_unknown_cloudy_rain_invalid_or_misaligned_is_not_clear(change):
    data = feeds()
    for row in data["KCMX"]["features"]:
        row["properties"].update(change)
    assert select_opportunity(activity(), data, now=NOW) is None


@pytest.mark.parametrize(
    "data",
    [
        None,
        [],
        [["header"]],
        [{"time_tag": "bad"}],
        [{"time_tag": "2026-10-17T03:00:00", "Kp": 12, "station_count": 8}],
        [{"time_tag": "2026-10-17T03:00:00", "Kp": True, "station_count": 8}],
        [{"time_tag": "2026-10-17T03:00:00", "Kp": float("nan"), "station_count": 8}],
    ],
)
def test_invalid_activity_feed_fails_closed(data):
    with pytest.raises(ValueError):
        select_opportunity(data, feeds(), now=NOW)


def test_sparse_duplicate_stale_and_daytime_evidence():
    data = feeds()
    data["KCMX"]["features"] = [weather(), weather()]
    assert select_opportunity(activity(), data, now=NOW) is None
    data["KCMX"]["features"] = [weather(), weather(OBSERVED + timedelta(minutes=29))]
    assert select_opportunity(activity(), data, now=NOW) is None
    assert select_opportunity(activity(), {"KP53": {"features": []}}, now=NOW) is None
    with pytest.raises(ValueError, match="completed night"):
        select_opportunity(activity()[:1], feeds(), now=NOW)
    with pytest.raises(ValueError, match="Ambiguous"):
        select_opportunity(activity() * 2, feeds(), now=NOW)
    assert (
        select_opportunity(
            [r | {"station_count": 5} for r in activity()] + activity(1), feeds(), now=NOW
        )
        is None
    )
    day = datetime(2026, 6, 21, 1, tzinfo=UTC)
    daytime = {"KCMX": {"features": [weather(day), weather(day + timedelta(minutes=30))]}}
    kp = [
        {"time_tag": "2026-06-21T00:00:00", "Kp": 8, "station_count": 8},
        {"time_tag": "2026-06-21T09:00:00", "Kp": 1, "station_count": 8},
    ]
    assert select_opportunity(kp, daytime, now=day.replace(hour=12)) is None


def test_durable_atomic_claim_and_failure_restart(store):
    assert not store.seen(OPPORTUNITY.morning)
    assert store.claim(OPPORTUNITY)
    assert not AuroraStore(store.path).claim(OPPORTUNITY)
    store.finish(OPPORTUNITY.morning, "send_uncertain")
    assert AuroraStore(store.path).seen(OPPORTUNITY.morning)
    store.finish(OPPORTUNITY.morning, "posted", 123)
    with store.transaction() as db:
        row = db.execute("SELECT status,message_id FROM nights").fetchone()
    assert row == ("posted", "123")
    assert store.path.stat().st_mode & 0o077 == 0
    with pytest.raises(ValueError):
        store.finish(OPPORTUNITY.morning, "retry")
    with pytest.raises(FileExistsError):
        AuroraStore.initialize(store.path)


def test_missing_unsafe_schema_and_retention(store, tmp_path):
    with pytest.raises(FileNotFoundError):
        AuroraStore(tmp_path / "missing.sqlite3").seen(OPPORTUNITY.morning)
    old = replace(OPPORTUNITY, morning="2026-08-01")
    assert store.claim(old)
    assert store.claim(OPPORTUNITY)
    assert not store.seen(old.morning)
    with store.transaction() as db:
        db.execute("PRAGMA user_version=2")
    with pytest.raises(LearningUnavailable):
        store.seen(OPPORTUNITY.morning)
    store.path.chmod(0o644)
    with pytest.raises(LearningUnavailable):
        store.seen(OPPORTUNITY.morning)


def test_cli_content_free(store, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["trubot-aurora", "status", "--path", str(store.path)])
    main()
    assert json.loads(capsys.readouterr().out) == {"nights": {}}


@pytest.mark.asyncio
async def test_feature_qualifies_once_without_repeat_cost(store):
    images = SimpleNamespace(generate=AsyncMock(return_value=AuroraImage(b"png", "caption", "alt")))
    collect = AsyncMock(return_value=OPPORTUNITY)
    feature = AuroraFeature(store, images, collect=collect)
    assert await feature.prepare(now=NOW)
    assert await feature.prepare(now=NOW) is None
    assert await feature.prepare(now=NOW + timedelta(hours=4)) is None
    assert images.generate.await_count == collect.await_count == 1


@pytest.mark.asyncio
async def test_feature_no_op_and_provider_failure_are_bounded(store):
    images = SimpleNamespace(generate=AsyncMock(side_effect=RuntimeError))
    collect = AsyncMock(return_value=None)
    feature = AuroraFeature(store, images, collect=collect)
    assert await feature.prepare(now=NOW) is None
    images.generate.assert_not_awaited()
    collect.return_value = OPPORTUNITY
    with pytest.raises(RuntimeError):
        await feature.prepare(now=NOW)
    assert await feature.prepare(now=NOW) is None
    assert images.generate.await_count == 1


def png():
    data = io.BytesIO()
    Image.new("RGB", (1536, 1024)).save(data, format="PNG")
    return data.getvalue()


def image_response(data=None):
    import base64

    return SimpleNamespace(
        data=[SimpleNamespace(b64_json=base64.b64encode(data or png()).decode())],
        usage=SimpleNamespace(
            input_tokens=100,
            output_tokens=1400,
            total_tokens=1500,
            input_tokens_details=SimpleNamespace(image_tokens=0, text_tokens=100),
        ),
    )


def generator(ledger, response=None, error=None):
    client = MagicMock(spec=AsyncOpenAI)
    client.with_options.return_value = client
    client.images = SimpleNamespace(
        generate=AsyncMock(return_value=response or image_response(), side_effect=error)
    )
    return AuroraImageGenerator(client, ledger), client


@pytest.mark.asyncio
async def test_real_adapter_prices_shared_ledger_and_provenance(private_test_ledger):
    gen, client = generator(private_test_ledger)
    result = await gen.generate(OPPORTUNITY, purpose="maintenance")
    assert result.data == png()
    assert "AI-generated" in result.caption and "not a confirmed sighting" in result.caption
    assert "Not a photograph" in result.description
    args = client.images.generate.call_args.kwargs
    assert args["quality"] == "medium" and args["size"] == "1536x1024" and args["n"] == 1
    assert client.with_options.call_args.kwargs["max_retries"] == 0
    summary = private_test_ledger.summary()
    assert summary["attempts"] == 1 and summary["maintenance_usd"] == 0.0425


@pytest.mark.asyncio
async def test_image_failure_and_missing_usage_hold_full_reservation(private_test_ledger):
    gen, client = generator(private_test_ledger, error=RuntimeError)
    with pytest.raises(RuntimeError):
        await gen.generate(OPPORTUNITY)
    assert client.images.generate.await_count == 1
    response = image_response()
    response.usage = None
    gen, _ = generator(private_test_ledger, response)
    with pytest.raises(BudgetUnavailable):
        await gen.generate(OPPORTUNITY)
    assert private_test_ledger.summary()["unsettled_attempts"] == 2


@pytest.mark.asyncio
async def test_invalid_image_accounted_but_not_postable(private_test_ledger):
    gen, _ = generator(private_test_ledger, image_response(b"not pixels"))
    with pytest.raises(OSError):
        await gen.generate(OPPORTUNITY)
    assert private_test_ledger.summary()["unsettled_attempts"] == 0


def test_image_budget_exhaustion_and_wrong_pricing(private_test_ledger):
    ledger = private_test_ledger
    r = ledger.reserve_image(prompt_bytes=100)
    with pytest.raises(BudgetUnavailable, match="pricing"):
        ledger.settle(r, input_tokens=1, cached_input_tokens=0, output_tokens=1)
    with pytest.raises(BudgetUnavailable, match="bound"):
        ledger.reserve_image(prompt_bytes=2001)
    with pytest.raises(BudgetUnavailable):
        ledger.settle_image(r, input_tokens=True, output_tokens=1)
    with patch("trubot.budget.RUNTIME_LIMIT", 1), pytest.raises(BudgetExceeded):
        ledger.reserve_image(prompt_bytes=100)
    r = ledger.reserve_image(prompt_bytes=100)
    with pytest.raises(BudgetUnavailable, match="exceeded"):
        ledger.settle_image(r, input_tokens=100, output_tokens=20000)
    with pytest.raises(BudgetUnavailable, match="reconciliation"):
        ledger.check()


@pytest.mark.asyncio
async def test_actual_discord_publication_once_and_cooldown(store):
    client, responder, _, tracker = make_client(clock=lambda: NOW)
    client._settings = replace(client._settings, aurora_channel_id=10, auto_delay_seconds=600)
    client._aurora_timing_ok = AsyncMock(return_value=True)
    channel = MagicMock(spec=discord.TextChannel)
    channel.id, channel.guild = 10, SimpleNamespace(id=77)
    channel.send = AsyncMock(return_value=SimpleNamespace(id=123))

    async def history(**kwargs):
        assert kwargs == {"limit": 1}
        yield SimpleNamespace(created_at=NOW - timedelta(hours=4))

    channel.history = history
    identity = SimpleNamespace(guild_id=77)
    client._learning = SimpleNamespace(
        verified=True, identity=identity, store=SimpleNamespace(identity=lambda: identity)
    )
    images = SimpleNamespace(generate=AsyncMock(return_value=AuroraImage(png(), "caption", "alt")))
    client._aurora = AuroraFeature(store, images, collect=AsyncMock(return_value=OPPORTUNITY))
    with patch.object(client, "get_channel", return_value=channel):
        assert await client._aurora_cycle()
        assert not await client._aurora_cycle()
    assert channel.send.await_count == images.generate.await_count == 1
    args = channel.send.call_args.kwargs
    assert args["file"].description == "alt" and not args["allowed_mentions"].everyone
    assert tracker.snapshot(10, NOW).ambient_replies_today == 1
    assert not tracker.scheduled_eligible(10, NOW + timedelta(minutes=5))
    assert not responder.calls
    await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("condition", ["busy", "wrong-guild", "withdrawn", "unverified", "cap"])
async def test_scheduled_gate_prevents_any_paid_attempt(store, condition):
    client, _, _, tracker = make_client(clock=lambda: NOW)
    client._settings = replace(client._settings, aurora_channel_id=10, auto_delay_seconds=600)
    client._aurora_timing_ok = AsyncMock(return_value=True)
    channel = MagicMock(spec=discord.TextChannel)
    channel.id, channel.guild = 10, SimpleNamespace(id=78 if condition == "wrong-guild" else 77)

    async def history(**_kwargs):
        yield SimpleNamespace(created_at=NOW if condition == "busy" else NOW - timedelta(hours=4))

    channel.history = history
    identity = SimpleNamespace(guild_id=77)

    def read_identity():
        if condition == "withdrawn":
            raise LearningUnavailable("withdrawn")
        return identity

    client._learning = SimpleNamespace(
        verified=condition != "unverified",
        identity=identity,
        store=SimpleNamespace(identity=read_identity),
    )
    images = SimpleNamespace(generate=AsyncMock())
    client._aurora = AuroraFeature(store, images, collect=AsyncMock(return_value=OPPORTUNITY))
    if condition == "cap":
        for _ in range(tracker.policy.daily_limit):
            tracker.record_reply(10, NOW - timedelta(hours=4), ambient=True)
    with patch.object(client, "get_channel", return_value=channel):
        if condition == "withdrawn":
            with pytest.raises(LearningUnavailable):
                await client._aurora_cycle()
        else:
            assert not await client._aurora_cycle()
    images.generate.assert_not_awaited()
    await client.close()


def test_config_channel_must_already_be_allowed():
    with pytest.raises(ConfigurationError, match="already be allowed"):
        Settings.from_env(
            {"DISCORD_TOKEN": "test", "OPENAI_API_KEY": "test", "TRUBOT_AURORA_CHANNEL_ID": "999"}
        )


@pytest.mark.asyncio
async def test_outside_window_does_not_fetch():
    with patch("trubot.aurora.aiohttp.ClientSession") as session:
        assert await collect_opportunity(now=NOW + timedelta(hours=5)) is None
        session.assert_not_called()


@pytest.mark.asyncio
async def test_concurrent_feature_claims_only_one_generation(store):
    images = SimpleNamespace(
        generate=AsyncMock(return_value=AuroraImage(b"image", "caption", "alt"))
    )
    feature = AuroraFeature(store, images, collect=AsyncMock(return_value=OPPORTUNITY))
    result = await asyncio.gather(feature.prepare(now=NOW), feature.prepare(now=NOW))
    assert sum(x is not None for x in result) == 1
    assert images.generate.await_count == 1


@pytest.mark.asyncio
async def test_cancelled_generation_is_not_retried(store):
    images = SimpleNamespace(generate=AsyncMock(side_effect=asyncio.CancelledError))
    feature = AuroraFeature(store, images, collect=AsyncMock(return_value=OPPORTUNITY))
    with pytest.raises(asyncio.CancelledError):
        await feature.prepare(now=NOW)
    assert await feature.prepare(now=NOW) is None
    assert images.generate.await_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["send", "activity-during-generation"])
async def test_send_or_context_race_cannot_repeat(store, failure):
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._settings = replace(client._settings, aurora_channel_id=10, auto_delay_seconds=600)
    client._aurora_timing_ok = AsyncMock(return_value=True)
    channel = MagicMock(spec=discord.TextChannel)
    channel.id, channel.guild = 10, SimpleNamespace(id=77)
    channel.send = AsyncMock(side_effect=RuntimeError("transport"))
    identity = SimpleNamespace(guild_id=77)
    client._learning = SimpleNamespace(
        verified=True, identity=identity, store=SimpleNamespace(identity=lambda: identity)
    )
    checks = iter([True, failure != "activity-during-generation", True])
    images = SimpleNamespace(generate=AsyncMock(return_value=AuroraImage(png(), "caption", "alt")))
    client._aurora = AuroraFeature(store, images, collect=AsyncMock(return_value=OPPORTUNITY))
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch.object(
            client, "_aurora_channel_ready", AsyncMock(side_effect=lambda _: next(checks))
        ),
    ):
        if failure == "send":
            with pytest.raises(RuntimeError):
                await client._aurora_cycle()
        else:
            assert not await client._aurora_cycle()
        assert not await client._aurora_cycle()
    assert images.generate.await_count == 1
    assert channel.send.await_count == (1 if failure == "send" else 0)
    with store.transaction() as db:
        status = db.execute("SELECT status FROM nights").fetchone()[0]
    assert status == ("send_uncertain" if failure == "send" else "deferred")
    await client.close()


class FeedResponse:
    def __init__(self, data, status=200):
        self.status = status
        self.data = data
        self.content = SimpleNamespace(
            read=AsyncMock(
                return_value=(data if isinstance(data, bytes) else json.dumps(data).encode())
            )
        )

    def raise_for_status(self):
        if self.status >= 400:
            raise RuntimeError("HTTP failure")

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None


@pytest.mark.asyncio
async def test_public_feed_transport_uses_fixed_endpoints_and_real_detector():
    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)

    def get(url, **kwargs):
        assert kwargs["allow_redirects"] is False
        if "planetary" in url:
            return FeedResponse(activity())
        assert url.startswith("https://api.weather.gov/stations/")
        assert kwargs["params"]["limit"] == "500"
        return FeedResponse(feeds()["KCMX"] if "KCMX" in url else {"features": []})

    session.get.side_effect = get
    with patch("trubot.aurora.aiohttp.ClientSession", return_value=session):
        assert await collect_opportunity(now=NOW) == OPPORTUNITY
    assert session.get.call_count == 4


@pytest.mark.asyncio
@pytest.mark.parametrize("response", [FeedResponse(b"x" * 4_000_001), FeedResponse({}, 302)])
async def test_unbounded_or_redirected_public_feed_rejected(response):
    session = MagicMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.get.return_value = response
    with (
        patch("trubot.aurora.aiohttp.ClientSession", return_value=session),
        pytest.raises(ValueError),
    ):
        await collect_opportunity(now=NOW)


@pytest.mark.asyncio
async def test_sensitive_timing_defers_before_image_cost(store):
    images = SimpleNamespace(generate=AsyncMock())
    feature = AuroraFeature(store, images, collect=AsyncMock(return_value=OPPORTUNITY))
    assert await feature.prepare(now=NOW, before_generation=AsyncMock(return_value=False)) is None
    assert await feature.prepare(now=NOW) is None
    images.generate.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ('{"allowed":true}', True),
        ('{"allowed":false}', False),
        ('{"allowed":1}', False),
        ('{"allowed":true,"extra":0}', False),
        ("bad", False),
        ("[]", False),
    ],
)
async def test_timing_judge_exact_contract_and_shared_accounting(text, expected):
    from test_openai_responder import FakeOpenAI, make_responder

    fake = FakeOpenAI(text)
    responder = make_responder(fake)
    assert await responder.allow_scheduled_share(["A synthetic friendly conversation."]) is expected
    request = fake.responses.request
    assert request["max_output_tokens"] == 32 and not request["store"]
    assert request["text"]["format"]["strict"] is True
    fake.responses.request = None
    assert not await responder.allow_scheduled_share(["x" * 6001])
    assert not await responder.allow_scheduled_share(["x"] * 11)
    assert fake.responses.request is None


@pytest.mark.asyncio
async def test_timing_context_retains_only_complete_human_text():
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._responder.allow_scheduled_share = AsyncMock(return_value=False)
    channel = MagicMock(spec=discord.TextChannel)
    rows = [
        SimpleNamespace(
            author=SimpleNamespace(bot=False),
            webhook_id=None,
            attachments=[],
            embeds=[],
            content="A synthetic serious worry.",
        ),
        SimpleNamespace(
            author=SimpleNamespace(bot=True),
            webhook_id=None,
            attachments=[],
            embeds=[],
            content="Earlier bot joke.",
        ),
    ]

    async def history(**kwargs):
        assert kwargs["limit"] == 10 and kwargs["after"] == NOW - timedelta(hours=6)
        for row in rows:
            yield row

    channel.history = history
    assert not await client._aurora_timing_ok(channel)
    client._responder.allow_scheduled_share.assert_awaited_once_with(["A synthetic serious worry."])
    rows[0].attachments = [object()]
    assert not await client._aurora_timing_ok(channel)
    assert client._responder.allow_scheduled_share.await_count == 1
    await client.close()


@pytest.mark.asyncio
async def test_optional_worker_failure_and_lifecycle_do_not_stop_reply_client(store, caplog):
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._aurora = AuroraFeature(store, SimpleNamespace(generate=AsyncMock()))

    async def cycle():
        client._closing = True
        raise RuntimeError("synthetic transport failure")

    with (
        patch.object(client, "_aurora_cycle", side_effect=cycle),
        patch("trubot.discord_client.asyncio.sleep", AsyncMock()),
    ):
        client._start_aurora()
        task = client._aurora_task
        client._start_aurora()
        assert client._aurora_task is task
        await task
        assert "Aurora cycle unavailable error_type=RuntimeError" in caplog.text
    client._closing = False
    client._aurora_task = None
    client._start_aurora()
    await client._stop_aurora()
    assert client._aurora_task is None
    await client.close()
