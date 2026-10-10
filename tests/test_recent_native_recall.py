import asyncio
import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import discord
import pytest
from test_discord_client import fake_channel, make_client
from test_learning import AUDIT, NOW, source
from test_native_context import message

from trubot.archives import ArchiveStore
from trubot.conversation import ConversationMessage
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore
from trubot.memory import ContextMemory, recent_recall
from trubot.native_context import collect_native_episode


@pytest.mark.parametrize(
    ("query", "recent"),
    [
        ("Quote something you said in the league recently, and what were you replying to?", True),
        ("What have you been saying recently?", True),
        ("Quote a recent league exchange.", True),
        ("What did you say recently about baseball?", True),
        ("What is the latest league news?", False),
        ("What were you saying in 2020?", False),
        ("Recall a recent conversation from 2020.", False),
        ("Who won the latest baseball game?", False),
    ],
)
def test_recent_intent_separates_authored_recall_from_current_facts(query, recent):
    assert recent_recall(query) is recent


@pytest.fixture
def setup(tmp_path):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    archive = ArchiveStore.initialize(store)
    archive.import_document(
        b"legacy.target\n  8:00 AM\nA recent league conversation about baseball.",
        channel="general",
        target_alias="legacy.target",
        alias_basis="Synthetic audit",
        origin={"kind": "synthetic"},
        now=NOW,
    )
    return store, ContextMemory(store)


def test_recent_setup_request_retrieves_short_dated_answers_and_no_undated_fallback(setup):
    store, memory = setup
    for i in range(4):
        store.observe(source(i, content=f"Yep {i}.", created_at=NOW - timedelta(days=i)), now=NOW)
    query = "Quote something you said in the league recently, and what were you replying to?"
    candidates = memory.candidates(query, guild_id=77, now=NOW)
    assert [c.content for c in candidates] == ["Yep 0.", "Yep 1.", "Yep 2."]
    assert "recent league conversation" not in memory.render(candidates, request=query, now=NOW)
    old = memory.candidates("baseball", guild_id=77, now=NOW)
    rendered = memory.render(old, request=query, now=NOW)
    assert "no verified recent human source" in rendered
    assert "A recent league conversation" not in rendered
    assert "no verified recent human source" in memory.render(
        candidates, request=query, now=NOW + timedelta(days=15)
    )


def test_recent_topics_retention_future_and_native_media_gaps(setup):
    store, memory = setup
    store.retention_days = 3
    store.observe(source(0, content="Sox baseball!", created_at=NOW - timedelta(days=1)), now=NOW)
    store.observe(source(1, content="Old baseball", created_at=NOW - timedelta(days=5)), now=NOW)
    store.observe(source(2, content="New draft idea.", created_at=NOW - timedelta(days=1)), now=NOW)
    # Corrupt/future source timestamps must not establish recency.
    with store._transaction() as db:
        db.execute(
            "UPDATE messages SET created_at=? WHERE id=?",
            ((NOW + timedelta(days=1)).isoformat(), source(2).id),
        )
    query = "What did you say recently about baseball?"
    candidates = memory.candidates(query, guild_id=77, now=NOW)
    assert [c.content for c in candidates] == ["Sox baseball!"]
    data = json.loads(memory.render(candidates, request=query, now=NOW).split("\n")[1])
    assert data[0]["conversation_context_only"]["human_messages"] == []
    assert data[0]["conversation_context_only"]["gaps"]
    assert (
        memory.candidates("What did you say recently about volcanoes?", guild_id=77, now=NOW) == []
    )


@pytest.mark.parametrize("exhausted", [False, True])
async def test_all_source_refreshes_precede_optional_context_within_shared_deadline(
    setup, exhausted
):
    store, memory = setup
    channel = fake_channel()
    for i in range(3):
        store.observe(
            source(i, content=f"Yep {i}.", created_at=NOW - timedelta(minutes=i)), now=NOW
        )
    client, _, _, _ = make_client(clock=lambda: NOW)
    learner = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    client._learning, client._memory = learner, memory
    elapsed, events = [0.0], []

    async def refresh(_channel, identifier):
        events.append(("refresh", identifier))
        if exhausted:
            elapsed[0] += 3.0
        return message(channel, identifier, text=f"Yep {identifier - source().id}.", created_at=NOW)

    async def collect(_channel, identifier, **_kwargs):
        events.append(("context", identifier))
        raise TimeoutError

    shim = SimpleNamespace(
        to_thread=asyncio.to_thread,
        wait_for=asyncio.wait_for,
        get_running_loop=lambda: SimpleNamespace(time=lambda: elapsed[0]),
    )
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch.object(learner, "refresh", side_effect=refresh),
        patch("trubot.discord_client.collect_native_episode", side_effect=collect),
        patch("trubot.discord_client.voice_context", side_effect=AssertionError("undated voice")),
        patch("trubot.discord_client.asyncio", shim),
    ):
        result = await client._memory_context(channel, "Tim: What did you say recently?", [])
    expected_refreshes = 2 if exhausted else 3
    assert [event[0] for event in events] == (
        ["refresh"] * expected_refreshes + ([] if exhausted else ["context"] * 2)
    )
    assert "Yep 0." in result and "Yep 1." in result
    assert "native setup and source media pixels not supplied" in result
    await client.close()


async def test_owner_scoped_empty_recent_recall_never_uses_prior_bot_or_undated_voice(setup):
    store, memory = setup
    client, _, _, _ = make_client(clock=lambda: NOW)
    learner = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    client._learning, client._memory = learner, memory
    channel = fake_channel()
    client._settings = SimpleNamespace(development_guild_id=88, allowed_channel_ids=frozenset({10}))
    channel.guild = SimpleNamespace(id=88, owner_id=7)
    history = [ConversationMessage("assistant", "I just said this invented historical line.")]
    with patch("trubot.discord_client.voice_context", side_effect=AssertionError("undated voice")):
        assert (
            await client._memory_context(
                channel, "Tim: What did you say recently?", history, requester_user_id=8
            )
            == ""
        )
        result = await client._memory_context(
            channel, "Tim: What did you say recently?", history, requester_user_id=7
        )
    assert "no verified recent human source" in result
    assert "invented historical line" not in result
    store.forget(now=NOW)
    result = await client._memory_context(
        channel, "Tim: What did you say recently?", history, requester_user_id=7
    )
    assert "no verified recent human source" in result
    # Restore the real settings before normal client disposal.
    from trubot.config import Settings

    client._settings = Settings(discord_token="test", openai_api_key="test")
    await client.close()


async def test_denied_context_stops_reference_reads_and_marks_focus_media_gap():
    channel = fake_channel()
    focus = message(channel, 100, attachments=[object()])
    focus.reference = discord.MessageReference(message_id=99, channel_id=10, guild_id=77)

    async def history(**_kwargs):
        raise discord.Forbidden(SimpleNamespace(status=403, reason="Denied"), "Denied")
        yield

    channel.history = history
    channel.fetch_message = AsyncMock(return_value=focus)
    from trubot.learning import Identity

    episode = await collect_native_episode(
        channel, 100, identity=Identity(42, 77, frozenset({10})), now=NOW, retention_days=180
    )
    channel.fetch_message.assert_awaited_once_with(100)
    assert episode.neighbors == ()
    assert len(episode.gaps) == 2
    assert "source media pixels not retrieved" in episode.gaps[0]
