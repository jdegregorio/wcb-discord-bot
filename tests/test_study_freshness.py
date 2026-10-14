"""Missed gateway edits must not establish obsolete durable memories."""

from types import SimpleNamespace

import pytest
from test_distillation import proposal, seed, worker
from test_ingestion import message
from test_learning import AUDIT, BASE, NOW

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore
from trubot.learning import LearningStore


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


@pytest.mark.parametrize("change_stage", ["memory_extract", "memory_review"])
async def test_missed_discord_edit_blocks_next_pass_or_commit(stores, change_stage):
    seed(stores)
    distiller, client, responder, channel = worker(stores)
    fetch = channel.fetch_message.side_effect
    changed = False

    def current(identifier):
        if changed and identifier == BASE:
            return message(channel, 0, content="I dislike caramel now.")
        return fetch(identifier)

    channel.fetch_message.side_effect = current

    async def generate(**kwargs):
        nonlocal changed
        # Real adapter calls this before each request, with maintenance retries disabled.
        await kwargs["source_check"]()
        if kwargs["name"] == change_stage:
            changed = True
        if kwargs["name"] == "memory_extract":
            return proposal(SimpleNamespace(passages=kwargs["payload"]["sources"]))
        return {"accepted": True, "basis": "Two original statements.", "contradicts": []}

    responder.study_json.side_effect = generate
    await distiller.cycle(client)
    assert not stores[2].lookup("dessert", guild_id=77, now=NOW)
    assert stores[2].status()["nodes"].get("preference", 0) == 0


@pytest.mark.parametrize("change_stage", ["memory_extract", "memory_review"])
@pytest.mark.parametrize(
    "failure",
    [
        "delete",
        "forbidden",
        "transport",
        "timeout",
        "wrong_author",
        "wrong_id",
        "bot",
        "webhook",
        "scope",
        "membership",
        "withdrawal",
    ],
)
async def test_current_read_failures_never_commit(stores, change_stage, failure, caplog):
    import discord

    seed(stores)
    learning, _, graph = stores
    distiller, client, responder, channel = worker(stores)
    fetch = channel.fetch_message.side_effect
    changed = False

    def current(identifier):
        if not changed or identifier != BASE:
            return fetch(identifier)
        if failure in {"delete", "forbidden", "transport"}:
            status = {"delete": 404, "forbidden": 403, "transport": 500}[failure]
            error = {
                "delete": discord.NotFound,
                "forbidden": discord.Forbidden,
                "transport": discord.HTTPException,
            }[failure]
            raise error(SimpleNamespace(status=status, reason="private"), "PRIVATE_PAYLOAD")
        if failure == "timeout":
            raise TimeoutError("PRIVATE_PAYLOAD")
        row = fetch(identifier)
        if failure == "wrong_author":
            row.author.id = 43
        elif failure == "wrong_id":
            row.id += 100
        elif failure == "bot":
            row.author.bot = True
        elif failure == "webhook":
            row.webhook_id = 123
        return row

    channel.fetch_message.side_effect = current

    async def generate(**kwargs):
        nonlocal changed
        await kwargs["source_check"]()
        if kwargs["name"] == change_stage:
            changed = True
            if failure == "scope":
                channel.guild.id = 78
            elif failure == "membership":
                distiller.ingestor.verified = False
            elif failure == "withdrawal":
                learning.forget(now=NOW)
        if kwargs["name"] == "memory_extract":
            return proposal(SimpleNamespace(passages=kwargs["payload"]["sources"]))
        return {"accepted": True, "basis": "Synthetic only", "contradicts": []}

    responder.study_json.side_effect = generate
    assert await distiller.cycle(client) is None
    if failure != "withdrawal":
        assert graph.status()["nodes"].get("preference", 0) == 0
    assert "PRIVATE_PAYLOAD" not in caplog.text
    assert channel.send.await_count == 0


async def test_unchanged_study_reads_original_cohort_at_every_boundary(stores):
    seed(stores)
    distiller, client, responder, channel = worker(stores)
    original = responder.study_json.side_effect
    packets = []

    async def generate(**kwargs):
        await kwargs["source_check"]()
        packets.append(kwargs["payload"]["sources"])
        return await original(**kwargs)

    responder.study_json.side_effect = generate
    assert await distiller.cycle(client) == "accepted"
    assert packets[0] == packets[1]
    reads = [x.args[0] for x in channel.fetch_message.await_args_list]
    assert set(reads[:2]) == {BASE, BASE + 1}
    assert reads == reads[:2] * 4
    assert stores[2].lookup("dessert", guild_id=77, now=NOW)


async def test_real_adapter_rereads_after_reservation_before_provider(stores, private_test_ledger):
    import json
    from unittest.mock import AsyncMock

    from test_openai_responder import FakeOpenAI, make_responder

    seed(stores)
    distiller, client, _, channel = worker(stores)
    fetch = channel.fetch_message.side_effect
    changed = False

    def current(identifier):
        if changed and identifier == BASE:
            return message(channel, 0, content="I dislike caramel now.")
        return fetch(identifier)

    channel.fetch_message.side_effect = current
    api = FakeOpenAI()
    distiller.responder = make_responder(api)

    async def generate(**kwargs):
        nonlocal changed
        passages = json.loads(kwargs["input"][0]["content"])["sources"]
        changed = True
        return SimpleNamespace(
            output_text=json.dumps(proposal(SimpleNamespace(passages=passages))),
            usage=SimpleNamespace(
                input_tokens=1000,
                input_tokens_details=SimpleNamespace(cached_tokens=800),
                output_tokens=10,
            ),
        )

    api.responses.create = AsyncMock(side_effect=generate)
    assert await distiller.cycle(client) is None
    assert api.responses.create.await_count == 1
    assert not stores[2].lookup("dessert", guild_id=77, now=NOW)
    # The existing guard conservatively retains a pre-I/O failed reservation.
    summary = private_test_ledger.summary()
    assert summary["attempts"] == 2 and summary["unsettled_attempts"] == 1
    assert summary["maintenance_usd"] > 0
