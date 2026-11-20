"""Fictional shared-topic growth must not displace the question's own evidence."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from test_discord_client import fake_channel, fake_message, make_client
from test_episode_memory import seed_pattern
from test_graph_selection import add
from test_learning import AUDIT, NOW

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore
from trubot.memory import ContextMemory


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def crowded(stores, *, generic=False):
    for i in range(5):
        add(stores, i, topic="shared", aliases=("picnic" if generic else "orbital picnic",))
    return add(stores, 99, topic="shared", aliases=("glacier picnic",))


@pytest.mark.parametrize("generic", [False, True])
def test_matching_relationship_precedes_shared_concept_neighbors(stores, generic):
    wanted = crowded(stores, generic=generic)
    for graph in (stores[2], GraphStore(stores[0])):
        result = graph.lookup("glacier picnic", guild_id=77, now=NOW)
        assert result[0]["id"] == wanted
        assert len(result) == 4  # Useful connected neighbors are still available.


def test_neighbors_do_not_inherit_another_observations_specificity(stores):
    add(stores, 0, topic="shared", aliases=("picnic",))
    exact = add(stores, 99, topic="shared", aliases=("glacier picnic",))
    independent = add(stores, 80, aliases=("glacier picnic",))
    result = stores[2].lookup("glacier picnic", guild_id=77, now=NOW)
    assert {r["id"] for r in result[:2]} == {exact, independent}


def test_matching_owner_keeps_its_complete_conflict_before_neighbors(stores):
    wanted = crowded(stores)
    contrary = add(stores, 98, aliases=("garden picnic",), contradicts=[wanted])
    result = stores[2].lookup("glacier picnic", guild_id=77, now=NOW)
    assert {r["id"] for r in result[:2]} == {wanted, contrary}
    assert all(r["status"] == "contested" for r in result[:2])
    assert len(result) == 4


def test_crowded_abstract_memory_keeps_conditions_and_counterevidence(stores):
    for i in range(10, 15):
        add(stores, i, topic="pattern", aliases=("roster",))
    learning, _, _ = seed_pattern(stores, id="z-pattern")
    memory = ContextMemory(learning)
    candidates = memory.candidates("roster brainstorming", guild_id=77, now=NOW)
    packet = memory.render_packet(
        candidates, now=NOW, verified_after=NOW, request="roster brainstorming"
    )
    assert "ABSTRACT EPISODE MEMORY" in packet.text
    assert "Serious votes need sincere answers" in packet.text
    assert "croissant" not in packet.text and not packet.allow_voice_examples


def test_matching_owner_reaches_the_bounded_validation_window(stores):
    for i in range(70):
        add(stores, i, topic="shared", aliases=("orbital picnic",))
    wanted = add(stores, 99, topic="shared", aliases=("glacier picnic",))
    graph = stores[2]
    with patch.object(graph, "_valid", wraps=graph._valid) as validate:
        assert graph.lookup("glacier picnic", guild_id=77, now=NOW)[0]["id"] == wanted
    assert validate.call_count <= 64


@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_crowded_matching_memory_reaches_reply_handlers(stores, mode):
    wanted = crowded(stores)
    learning, _, _ = stores
    client, responder, _, _ = make_client(clock=lambda: NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(learning)
    channel = fake_channel()

    async def history(**kwargs):
        for row in []:
            yield row

    channel.history = history
    message = fake_message(channel, direct=mode == "direct")
    message.id, message.guild, message.reference = 123, channel.guild, None
    message.attachments, message.embeds = [], []
    message.content = message.clean_content = ("🤖 " if mode == "direct" else "") + "glacier picnic"
    try:
        with (
            patch.object(client, "get_channel", return_value=channel),
            patch.object(ingestor, "refresh", new_callable=AsyncMock),
        ):
            if mode == "reaction":
                channel.fetch_message.return_value = message
                await client.on_raw_reaction_add(
                    SimpleNamespace(
                        user_id=1,
                        channel_id=10,
                        message_id=123,
                        emoji=SimpleNamespace(name="ThomasJones"),
                        member=SimpleNamespace(bot=False),
                    )
                )
            else:
                if mode == "followup":
                    client._attention.activate(10, NOW)
                await client.on_message(message)
        context = "\n".join(m.content for m in responder.calls[0][0])
        assert wanted in context
        channel.send.assert_awaited_once()
    finally:
        await client.close()
