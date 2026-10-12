"""Invented source pairs verify relevance independently of generated answer wording."""

import json
from unittest.mock import patch

import pytest
from test_learning import AUDIT, NOW
from test_voice_memory import add

from trubot.archives import ArchiveStore
from trubot.learning import LearningStore
from trubot.personality import StyleExample
from trubot.voice_memory import voice_context


@pytest.fixture
def archive(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return ArchiveStore.initialize(learning)


@pytest.mark.parametrize(
    "query",
    [
        "hello there",
        "What is your humor style in casual league banter?",
        "A fictional friend is upset and just wants someone to listen.",
        "Tomatoes",
        "baseball",
        "football",
        "league",
    ],
)
def test_irrelevant_setup_cannot_be_admitted_by_answer_or_fallback(archive, query):
    add(
        archive,
        "peer\n  8:00 AM\nHow is your garden?\nlegacy.target\n  8:01 AM\nTomatoes win again.",
    )
    with patch(
        "trubot.voice_memory.STYLE_EXAMPLES",
        (StyleExample("How is your garden?", "Tomatoes win again."),),
    ):
        assert voice_context(archive.learning, query, guild_id=77) == ""


def test_shared_expanded_topic_is_not_setup_relevance(archive):
    add(
        archive,
        "peer\n  8:00 AM\nHow about those kickers?\nlegacy.target\n  8:01 AM\n"
        "Never punt on snacks.",
    )
    with patch(
        "trubot.voice_memory.STYLE_EXAMPLES",
        (StyleExample("How about those kickers?", "Never punt on snacks."),),
    ):
        assert (
            voice_context(archive.learning, "Who is your favorite football player?", guild_id=77)
            == ""
        )
        assert "Never punt on snacks." in voice_context(archive.learning, "A kicker?", guild_id=77)


def test_only_relevant_setups_survive_without_padding(archive):
    catalog = []
    for i, topic in enumerate(("garden", "race", "recipe", "garden")):
        setup, answer = f"How is the {topic} number {i}?", f"Secret answer {i}."
        add(archive, f"peer\n  8:00 AM\n{setup}\nlegacy.target\n  8:01 AM\n{answer}", i)
        catalog.append(StyleExample(setup, answer))
    with patch("trubot.voice_memory.STYLE_EXAMPLES", tuple(catalog)):
        data = json.loads(voice_context(archive.learning, "garden", guild_id=77).split("\n", 1)[1])
        assert len(data) == 2
        assert all("garden" in x["preceding_peer_context_only"] for x in data)


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_unrelated_voice_is_omitted_by_real_handler_path(archive, mode):
    from dataclasses import replace
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    from test_discord_client import fake_channel, fake_message, make_client

    from trubot.ingestion import MessageIngestor
    from trubot.memory import ContextMemory

    add(
        archive,
        "peer\n  8:00 AM\nHow is your garden?\nlegacy.target\n  8:01 AM\nTomatoes win again.",
    )
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._settings = replace(client._settings, development_guild_id=78)
    learning = MessageIngestor(archive.learning, frozenset({10}), clock=lambda: NOW)
    learning.verified = True
    client._learning, client._memory = learning, ContextMemory(archive.learning)
    channel = fake_channel()
    channel.guild = SimpleNamespace(id=78, owner_id=1)
    message = fake_message(channel)
    message.content = message.clean_content = "🤖 A fictional friend needs encouragement."
    channel.fetch_message.return_value = message
    client._attention.activate(10, NOW)
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "get_channel", return_value=channel),
        patch(
            "trubot.voice_memory.STYLE_EXAMPLES",
            (StyleExample("How is your garden?", "Tomatoes win again."),),
        ),
    ):
        if mode == "reaction":
            await client.on_raw_reaction_add(
                SimpleNamespace(
                    channel_id=10,
                    user_id=1,
                    message_id=message.id,
                    emoji=SimpleNamespace(name="🍆"),
                    member=SimpleNamespace(bot=False),
                )
            )
        else:
            if mode == "followup":
                message.content = message.clean_content = "A fictional friend needs encouragement."
            await client.on_message(message)
        assert len(responder.calls) == 1
        assert all("SOURCE-CHECKED VOICE CONTEXT" not in m.content for m in responder.calls[0][0])
        channel.send.assert_awaited_once_with("Hot")
        assert archive.learning.status()["messages"] == 0
    await client.close()


def test_matching_examples_remain_capped_and_deduplicated(archive):
    catalog = []
    for i in range(6):
        setup, answer = f"Garden update {i}?", f"Harvest number {i}."
        body = f"peer\n  8:00 AM\n{setup}\nlegacy.target\n  8:01 AM\n{answer}"
        add(archive, body, i)
        add(archive, body, i + 10)
        catalog.append(StyleExample(setup, answer))
    with patch("trubot.voice_memory.STYLE_EXAMPLES", tuple(catalog)):
        data = json.loads(voice_context(archive.learning, "garden", guild_id=77).split("\n", 1)[1])
        assert len(data) == 3
        assert len({x["andrew_authored_words"] for x in data}) == 3
