"""Invented closing qualifications must survive the real memory-admission path."""

import json
from unittest.mock import patch

import discord
import pytest
from test_discord_client import make_client
from test_learning import AUDIT, BASE, NOW, source
from test_native_context import IDENTITY, channel_with, message

from trubot.archives import ArchiveStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore
from trubot.memory import ContextMemory
from trubot.native_context import collect_native_episode

QUALIFIED = (
    "We are recruiting a dragon for the roster. "
    + "Background logistics. " * 16
    + ("This is only pretend, not a real offer.")
)


@pytest.mark.parametrize("parent", [False, True])
async def test_native_complete_qualification_and_link_reach_memory_packet(tmp_path, parent):
    assert 350 < len(QUALIFIED.encode()) <= 600
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(store)
    store.observe(source(content="The dragon roster idea sounds great."), now=NOW)
    memory = ContextMemory(store)
    channel, focus = channel_with()
    focus.id, focus.created_at = BASE, source().created_at
    focus.content = "The dragon roster idea sounds great."
    neighbor = message(channel, BASE - 1, author=9, text=QUALIFIED, created_at=focus.created_at)
    if parent:
        focus.reference = discord.MessageReference(
            message_id=neighbor.id, channel_id=10, guild_id=77
        )

    async def history(**kwargs):
        assert kwargs["limit"] == 5
        if not parent:
            yield neighbor

    channel.history = history

    async def fetch(identifier):
        return focus if identifier == focus.id else neighbor

    channel.fetch_message.side_effect = fetch
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._learning = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    client._learning.verified = True
    client._memory = memory
    with patch.object(client, "get_channel", return_value=channel):
        packet = await client._memory_context(
            channel, "Tim: What did Andrew say recently about the dragon roster?", []
        )
    assert QUALIFIED in packet
    assert "peer (not persona evidence)" in packet
    assert ('"focus_replies_to_this": true' in packet) is parent
    assert store.status()["messages"] == 1
    store.forget(now=NOW)
    assert await client._memory_context(channel, "Tim: dragon roster", []) == ""
    await client.close()


@pytest.mark.parametrize("body", ["x" * 600, "🦆" * 150], ids=["ascii", "unicode"])
async def test_exact_native_byte_bound_is_complete(body):
    channel, focus = channel_with()
    row = message(channel, 99, text=body, author=9)

    async def history(**_kwargs):
        yield row

    channel.history = history
    episode = await collect_native_episode(
        channel, focus.id, identity=IDENTITY, now=NOW, retention_days=180
    )
    assert episode.neighbors[0]["text"] == body
    assert not episode.gaps


@pytest.mark.parametrize("parent", [False, True])
@pytest.mark.parametrize("body", ["private prefix " + "x" * 600, "🦆" * 151])
async def test_oversized_native_context_has_gap_and_never_a_prefix(body, parent):
    channel, focus = channel_with()
    long_row = message(channel, 99, text=body, author=9)
    short_row = message(channel, 101, text="Short reaction.", author=8)
    if parent:
        focus.reference = discord.MessageReference(message_id=99, channel_id=10, guild_id=77)

    async def history(**_kwargs):
        for row in [short_row] if parent else [long_row, short_row]:
            yield row

    channel.history = history
    channel.fetch_message.side_effect = [focus, long_row] if parent else [focus]
    episode = await collect_native_episode(
        channel, focus.id, identity=IDENTITY, now=NOW, retention_days=180
    )
    assert [r["text"] for r in episode.neighbors] == ["Short reaction."]
    assert any("omitted" in gap and "size" in gap for gap in episode.gaps)
    assert "private prefix" not in json.dumps(episode.as_data())
    assert "🦆" not in json.dumps(episode.as_data(), ensure_ascii=False)
    assert channel.fetch_message.await_count == (2 if parent else 1)


@pytest.mark.parametrize("body", [QUALIFIED, "x" * 600, "🦆" * 150, "x" * 601, "🦆" * 151])
def test_historical_context_is_complete_or_an_explicit_gap(tmp_path, body):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    archive = ArchiveStore.initialize(store)
    raw = (
        f"peer\n  8:00 AM\n{body}\nfixture.target\n  8:01 AM\n"
        "The dragon roster idea sounds great.\npeer\n  8:02 AM\nShort reaction."
    )
    archive.import_document(
        raw.encode(),
        channel="synthetic",
        target_alias="fixture.target",
        alias_basis="Invented private-context regression",
        origin={"kind": "synthetic"},
        now=NOW,
    )
    memory = ContextMemory(store)
    candidates = memory.candidates("dragon roster", guild_id=77, now=NOW)
    packet = memory.render(candidates, request="dragon roster", now=NOW)
    evidence = json.loads(packet.split("\n")[1])[0]
    neighbors = evidence["adjacent_context_only"]
    if len(body.encode()) <= 600:
        assert neighbors[0]["text"] == body
        assert not evidence.get("context_gaps")
    else:
        assert [r["text"] for r in neighbors] == ["Short reaction."]
        assert any("omitted" in gap and "size" in gap for gap in evidence["context_gaps"])
        assert body[:350] not in packet
    archive.remove_document(candidates[0].source["document"], now=NOW)
    assert memory.render(candidates, request="dragon roster", now=NOW) == ""
