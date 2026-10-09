from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from test_discord_client import fake_channel, fake_message, make_client
from test_graph import observation
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable
from trubot.lexical import phrase, words
from trubot.memory import ContextMemory, score, terms


@pytest.mark.parametrize(
    ("singular", "plural"),
    [
        ("champion", "champions"),
        ("draft", "drafts"),
        ("kicker", "kickers"),
        ("league", "leagues"),
        ("matchup", "matchups"),
        ("opponent", "opponents"),
        ("pick", "picks"),
        ("player", "players"),
        ("playoff", "playoffs"),
        ("quarterback", "quarterbacks"),
        ("roster", "rosters"),
        ("rule", "rules"),
        ("seed", "seeds"),
        ("team", "teams"),
        ("trade", "trades"),
        ("waiver", "waivers"),
        ("winner", "winners"),
    ],
)
def test_explicit_nouns_have_symmetric_case_insensitive_retrieval(singular, plural):
    assert phrase(singular) == phrase(plural.upper())
    assert terms(singular) == terms(plural)
    assert (
        score(singular, terms(plural))
        == score(plural, terms(singular))
        == (0 if singular == "team" else 1)
    )


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("Sox", "sock"),
        ("Bears", "bear"),
        ("Dallas", "Dalla"),
        ("Jones", "Jone"),
        ("news", "new"),
        ("winner", "winning"),
        ("pick", "pickaxe"),
        ("seed", "seeding"),
        ("top seed", "seed top"),
        ("playoff opponent", "playoff schedule opponent"),
    ],
)
def test_names_arbitrary_stems_verbs_substrings_and_order_stay_distinct(left, right):
    assert phrase(left) != phrase(right)
    assert phrase(left) not in phrase(right)


def test_numbers_and_punctuation_keep_phrase_boundaries():
    assert words("1 seed: PLAYOFF-OPPONENTS") == ("1", "seed", "playoff", "opponent")
    assert phrase("playoff opponent") in phrase("the playoff-opponents are here")
    assert phrase("seed") not in phrase("seedling")
    assert "draft" in terms("2020drafts")


def setup_graph(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(learning)
    graph = GraphStore.initialize(learning)
    learning.observe(source(content="I opposed the selection proposal."), now=NOW)
    graph.import_observation(
        observation(
            {"kind": "discord", "message_id": source().id},
            id="selection",
            entities=[{"id": "selection", "kind": "concept", "aliases": ["playoff opponent"]}],
        ),
        now=NOW,
    )
    return learning, graph


def test_plural_graph_recall_retains_authority_conflicts_and_exact_quotes(tmp_path):
    learning, graph = setup_graph(tmp_path)
    query = "Tell me about choosing playoff opponents"
    memory = ContextMemory(learning)
    candidates = memory.candidates(query, guild_id=77, now=NOW)
    assert len(candidates) == 1 and candidates[0].source["graph_ids"]
    assert "CONNECTED REVIEWED MEMORY" in memory.render(candidates, now=NOW, verified_after=NOW)
    assert not memory.render(candidates, now=NOW, verified_after=NOW + timedelta(seconds=1))
    assert not graph.lookup(query, guild_id=78, now=NOW)
    assert not graph.lookup("playoff schedule opponent", guild_id=77, now=NOW)
    assert GraphStore(learning).lookup(query, guild_id=77, now=NOW)
    learning.observe(source(1, content="I favor the selection proposal."), now=NOW)
    graph.import_observation(
        observation(
            {"kind": "discord", "message_id": source(1).id},
            id="contrary",
            contradicts=["selection"],
            entities=[{"id": "other", "kind": "concept", "aliases": ["different idea"]}],
        ),
        now=NOW,
    )
    assert len(graph.lookup(query, guild_id=77, now=NOW)) == 2
    candidates = memory.candidates(query, guild_id=77, now=NOW)
    text = memory.render(candidates, now=NOW, verified_after=NOW)
    assert "I opposed" in text and "I favor" in text and "contested" in text
    learning.invalidate(10, [source().id], deleted=True, now=NOW)
    assert not graph.lookup(query, guild_id=77, now=NOW)
    assert "I opposed" not in memory.render(candidates, now=NOW)
    learning.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        graph.lookup(query, guild_id=77, now=NOW)


def test_lexical_plurals_retrieve_sources_without_rewriting_or_fuzzy_quoting(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    learning.observe(source(content="That draft pick matters."), now=NOW)
    memory = ContextMemory(learning)
    candidates = memory.candidates("Do draft picks matter?", guild_id=77, now=NOW)
    assert len(candidates) == 1
    assert "That draft pick matters." in memory.render(candidates)
    assert not memory.candidates(
        "source", guild_id=77, now=NOW, quotation="That draft picks matters."
    )
    assert memory.candidates("source", guild_id=77, now=NOW, quotation="That draft pick matters.")
    learning.invalidate(10, [source().id], deleted=False, now=NOW)
    assert not memory.render(candidates)


@pytest.mark.asyncio
async def test_inflected_reviewed_memory_reaches_production_handler_with_refresh(tmp_path):
    learning, _ = setup_graph(tmp_path)
    client, responder, _, _ = make_client(clock=lambda: NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(learning)
    channel = fake_channel()

    async def history(**_kwargs):
        for item in []:
            yield item

    channel.history = history
    message = fake_message(channel)
    message.guild = channel.guild
    message.content = message.clean_content = "🤖 What about choosing playoff opponents?"
    message.attachments, message.embeds, message.reference = [], [], None
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch.object(ingestor, "refresh", new_callable=AsyncMock) as refresh,
    ):
        await client.on_message(message)
        refresh.assert_awaited_once_with(channel, source().id)
    context = responder.calls[0][0]
    assert any("CONNECTED REVIEWED MEMORY" in m.content for m in context)
    assert any("I opposed the selection proposal." in m.content for m in context)
    channel.send.assert_awaited_once()
