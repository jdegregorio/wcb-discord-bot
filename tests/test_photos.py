"""Pixel-grounded photo lifecycle, bounded maintenance and reference generation."""

import hashlib
import io
import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from PIL import Image
from test_aurora import generator, image_response, png
from test_learning import AUDIT, NOW
from test_native_context import channel_with, message

from trubot.archives import ArchiveStore
from trubot.budget import BudgetUnavailable
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable
from trubot.photos import DAILY_STUDIES, PhotoMemory, PhotoStore, main
from trubot.recall_window import recall_window

PROFILE = {
    "scene": "trail_camera",
    "description": "A woodland clearing.",
    "framing": "Low fixed camera, tree on left, open ground to right.",
    "people": False,
    "reusable": True,
}


def photo_bytes():
    out = io.BytesIO()
    Image.new("RGB", (64, 32), "green").save(out, format="JPEG")
    return out.getvalue()


@pytest.fixture
def photos(tmp_path):
    learning = MessageIngestor(
        LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW),
        frozenset({10}),
        clock=lambda: NOW,
    )
    learning.verified = True
    archive = ArchiveStore.initialize(learning.store)
    PhotoStore(archive).initialize(now=NOW)
    responder = SimpleNamespace(study_json=AsyncMock(return_value=dict(PROFILE)))
    memory = PhotoMemory(learning, responder)
    channel, _ = channel_with()
    client = MagicMock(spec=discord.Client)
    client.fetch_channel = AsyncMock(return_value=channel)
    client.get_channel.return_value = channel
    memory.client = client
    return memory, channel, client, responder


def attached(channel, mid=100, **kwargs):
    return message(
        channel,
        mid,
        attachments=[
            SimpleNamespace(
                id=mid + 1,
                url=f"https://cdn.discordapp.com/attachments/1/{mid}/photo.jpg",
                size=len(photo_bytes()),
                content_type="image/jpeg",
            )
        ],
        **kwargs,
    )


async def captured(photos, **kwargs):
    memory, channel, _, _ = photos
    msg = attached(channel, **kwargs)
    channel.fetch_message.return_value = msg
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())):
        assert await memory.capture(msg)
    return msg, memory.store.rows()[0]


def ready(memory, row, profile=None):
    assert memory.store.claim(row["episode"], now=NOW)
    memory.store.finish(row["episode"], profile or dict(PROFILE))


async def test_capture_is_private_hashed_attributed_idempotent_and_correctable(photos):
    memory, _, _, _ = photos
    msg, row = await captured(photos)
    assert row["author"] == 42 and row["state"] == "pending"
    assert row["asset"] == hashlib.sha256(photo_bytes()).hexdigest()
    assert memory.store.archives.path.stat().st_mode & 0o077 == 0
    episode = memory.store.archives.visual_context(row["episode"])
    assert episode["context"][0]["target"] is True
    with patch("trubot.photos.download_image", AsyncMock()) as download:
        assert not await memory.capture(msg)
    download.assert_not_awaited()
    ready(memory, row)
    ref = await memory.reference("trail_camera")
    assert ref and await memory.current(ref)
    with Image.open(io.BytesIO(ref.data)) as image:
        assert image.size == (64, 32) and not image.getexif()
    msg.content = "Corrected caption."
    assert not await memory.current(ref)
    memory.store.drop(10, [msg.id], deleted=False, now=NOW)
    assert memory.store.rows() == []
    with pytest.raises(LearningUnavailable):
        memory.store.archives.read_asset(row["asset"])
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())):
        assert await memory.capture(msg)
    memory.store.drop(10, [msg.id], deleted=True, now=NOW)
    with (
        patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())),
        pytest.raises(LearningUnavailable, match="suppressed"),
    ):
        await memory.capture(msg)


@pytest.mark.parametrize("kind", ["peer", "people", "not_reusable", "wrong_scene", "pending"])
async def test_ineligible_frames_cannot_guide_character_images(photos, kind):
    memory, _, _, _ = photos
    _, row = await captured(photos, author=43 if kind == "peer" else 42)
    profile = dict(PROFILE)
    if kind == "people":
        profile["people"] = True
    if kind == "not_reusable":
        profile["reusable"] = False
    if kind == "wrong_scene":
        profile["scene"] = "other"
    if kind != "pending":
        ready(memory, row, profile)
    assert await memory.reference("trail_camera") is None
    assert await memory.reference("Marquette") is None


@pytest.mark.parametrize("kind", ["bot", "webhook", "other_guild", "other_channel", "paused"])
async def test_photo_capture_never_expands_intake(photos, kind):
    memory, channel, _, _ = photos
    msg = attached(channel)
    if kind == "bot":
        msg.author.bot = True
    if kind == "webhook":
        msg.webhook_id = 1
    if kind == "other_guild":
        msg.guild = SimpleNamespace(id=88)
    if kind == "other_channel":
        msg.channel = MagicMock(spec=discord.TextChannel)
        msg.channel.id, msg.channel.guild = 30, channel.guild
    if kind == "paused":
        memory.learning.verified = False
    with patch("trubot.photos.download_image", AsyncMock()) as download:
        assert not await memory.capture(msg)
    download.assert_not_awaited()


async def test_fresh_access_signature_and_withdrawal_gate_reference_reuse(photos):
    memory, channel, client, _ = photos
    msg, row = await captured(photos)
    ready(memory, row)
    ref = await memory.reference("trail_camera")
    assert ref
    channel.fetch_message.side_effect = TimeoutError
    assert not await memory.current(ref)
    channel.fetch_message.side_effect = None
    channel.fetch_message.return_value = msg
    client.fetch_channel.return_value = SimpleNamespace(id=10)
    assert not await memory.current(ref)
    client.fetch_channel.return_value = channel
    memory.learning.store.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        await memory.reference("trail_camera")
    assert not memory.store.archives.path.exists()


async def test_claims_survive_source_edits_process_restart_and_daily_cap(photos):
    memory, _, _, _ = photos
    msg, row = await captured(photos)
    for i in range(DAILY_STUDIES):
        assert PhotoStore(memory.store.archives).claim(row["episode"], now=NOW)
        assert not PhotoStore(memory.store.archives).claim(row["episode"], now=NOW)
        msg.content = f"Edited {i}"
        with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())):
            assert await memory.capture(msg)
    assert not memory.store.claim(row["episode"], now=NOW)
    assert memory.store.claim(row["episode"], now=NOW + timedelta(days=2))


async def test_cycle_captures_and_describes_pixels_once_without_learning_profile_as_belief(photos):
    memory, channel, client, responder = photos
    msg = attached(channel, mid=discord.utils.time_snowflake(NOW - timedelta(minutes=1)))
    channel.fetch_message.return_value = msg

    async def history(**kwargs):
        yield msg

    channel.history = history
    with patch("trubot.photos.download_image", AsyncMock(return_value=photo_bytes())):
        await memory.cycle(client)
        await memory.cycle(client)
    assert responder.study_json.await_count == 1
    args = responder.study_json.call_args.kwargs
    assert len(args["images"]) == 1 and args["payload"] == {"animated": False}
    await args["source_check"]()
    row = memory.store.rows()[0]
    assert row["state"] == "ready" and json.loads(row["profile"])["version"] == "pixel-scene-v1"
    assert memory.store.cursors()[0][1] == msg.id
    assert await memory.reference("trail_camera")


async def test_actual_edit_input_and_separate_image_token_cost(photos, private_test_ledger):
    memory, _, _, _ = photos
    _, row = await captured(photos)
    ready(memory, row)
    response = image_response()
    response.usage.input_tokens_details.image_tokens = 1000
    response.usage.input_tokens = 1100
    response.usage.total_tokens = 2500
    gen, client = generator(private_test_ledger)
    gen.photos = memory
    client.images.edit = AsyncMock(return_value=response)
    result = await gen.generate_life("trail_camera")
    client.images.generate.assert_not_awaited()
    args = client.images.edit.call_args.kwargs
    assert args["image"][0] == "reference.jpg" and args["image"][2] == "image/jpeg"
    assert "camera position" in args["prompt"] and "AI-generated" in result.caption
    assert result.data == png() and await result.source_check()
    assert private_test_ledger.summary()["runtime_usd"] == 0.0505
    memory.store.drop(10, [100], deleted=True, now=NOW)
    assert not await result.source_check()


@pytest.mark.parametrize(
    "question",
    [
        "see anything cool in the UP recently?",
        "Seen anything interesting lately?",
        "Have you spotted anything recently?",
    ],
)
def test_casual_sightings_use_dated_recall(question):
    assert recall_window(question) == timedelta(days=14)


@pytest.mark.parametrize(
    "profile",
    [
        {},
        PROFILE | {"description": "x" * 601},
        PROFILE | {"people": "no"},
        PROFILE | {"scene": "unknown"},
    ],
)
async def test_invalid_profile_is_never_usable(photos, profile):
    memory, _, _, _ = photos
    _, row = await captured(photos)
    assert memory.store.claim(row["episode"], now=NOW)
    with pytest.raises(LearningUnavailable):
        memory.store.finish(row["episode"], profile)


def test_reference_budget_rejects_unbounded_image_tokens(private_test_ledger):
    with pytest.raises(BudgetUnavailable):
        private_test_ledger.reserve_image(prompt_bytes=10, image_tokens=80001)


async def test_private_photo_cli_counts_only(photos, monkeypatch, capsys):
    memory, _, _, _ = photos
    await captured(photos)
    monkeypatch.setattr(
        "sys.argv", ["trubot-photos", "status", "--path", str(memory.learning.store.path)]
    )
    main()
    assert json.loads(capsys.readouterr().out) == {"photos": 1, "ready": 0, "channels": 2}


async def test_bad_download_records_gap_without_blocking_incremental_progress(photos):
    memory, channel, client, _ = photos
    mid = discord.utils.time_snowflake(NOW - timedelta(minutes=1))
    msg = attached(channel, mid=mid)

    async def history(**kwargs):
        yield msg

    channel.history = history
    with patch("trubot.photos.download_image", AsyncMock(side_effect=ValueError("unavailable"))):
        await memory.cycle(client)
    assert memory.store.cursors()[0][1] == mid
    with memory.store.archives._transaction() as db:
        assert db.execute("SELECT reason FROM photo_gaps").fetchone()[0] == "ValueError"
    assert memory.store.rows() == []


async def test_profile_correction_revokes_inflight_reference(photos):
    memory, _, _, _ = photos
    _, row = await captured(photos)
    ready(memory, row)
    reference = await memory.reference("trail_camera")
    assert reference
    with memory.store.archives._transaction() as db:
        db.execute("UPDATE photo_profiles SET profile='{}'")
    assert not await memory.current(reference)


@pytest.mark.parametrize("change", ["delete", "edit_attachment"])
async def test_source_change_during_download_cannot_retain_stale_pixels(photos, change):
    memory, channel, _, _ = photos
    msg = attached(channel)
    channel.fetch_message.return_value = msg

    async def download(_url):
        if change == "delete":
            memory.store.drop(10, [msg.id], deleted=True, now=NOW)
        else:
            msg.attachments[0].id += 2
            msg.content = "A replacement image."
        return photo_bytes()

    with patch("trubot.photos.download_image", download), pytest.raises(LearningUnavailable):
        await memory.capture(msg)
    assert memory.store.rows() == []
    assert memory.store.archives.status()["image_assets"] == 0
