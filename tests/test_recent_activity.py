"""Recent lived experience needs dated evidence and the correct human owner."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from test_discord_client import fake_channel, fake_message, make_client
from test_learning import AUDIT, NOW, source
from test_native_context import message

from trubot.archives import ArchiveStore
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore
from trubot.memory import ContextMemory, recent_recall, requester_recall
from trubot.recall_window import recall_window


@pytest.mark.parametrize(
    ("question", "hours"),
    [
        ("Where have you traveled recently?", 336),
        ("Where have I traveled recently?", 336),
        ("Have you gone on any trips in the past week?", 168),
        ("Where did Andrew visit in the last two days?", 48),
        ("What have you been doing lately?", 336),
        ("What have I been doing lately?", 336),
        ("Have you been camping in the last 48 hours?", 48),
        ("What have you been reading recently?", 336),
    ],
)
def test_explicit_recent_activity_uses_the_existing_bounded_window(question, hours):
    assert recall_window(question) == timedelta(hours=hours)


@pytest.mark.parametrize(
    "question",
    [
        "Where would you travel for a week?",
        "If you could go anywhere recently, where would you choose?",
        "What should I read lately?",
        "Have the Sox been playing recently?",
        "Where has the team traveled recently?",
        "What are the latest travel restrictions?",
        "Where have you traveled in 2020?",
        "Where have you traveled recently in 2020?",
        'Explain the question "Where have you traveled recently?"',
        "What would you think if I traveled recently?",
        "Have you considered my travel proposal recently?",
    ],
)
def test_advice_hypotheticals_quotes_and_external_events_keep_their_route(question):
    assert not recent_recall(question)


@pytest.fixture
def memory(tmp_path):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    archive = ArchiveStore.initialize(store)
    archive.import_document(
        b"legacy.target\n  8:00 AM\nI traveled to the Lantern Islands on a trip.",
        channel="general",
        target_alias="legacy.target",
        alias_basis="Synthetic audit",
        origin={"kind": "synthetic"},
        now=NOW,
    )
    return ContextMemory(store)


def test_undated_activity_cannot_establish_a_recent_trip_but_broad_recall_survives(memory):
    query = "Where have you traveled recently?"
    assert memory.candidates(query, guild_id=77, now=NOW) == []
    assert "no verified recent human source" in memory.render([], request=query, now=NOW)
    assert memory.candidates("Where have you traveled?", guild_id=77, now=NOW)


def test_current_activity_is_usable_and_old_future_wrong_author_are_excluded(memory):
    store = memory.learning
    store.observe(source(0, content="I traveled to Lantern Island.", created_at=NOW), now=NOW)
    store.observe(
        source(1, content="I traveled to Pebble Island.", created_at=NOW - timedelta(days=20)),
        now=NOW,
    )
    store.observe(source(2, content="I traveled to Pine Island.", author_id=43), now=NOW)
    store.observe(source(3, content="I traveled to Cloud Island."), now=NOW)
    with store._transaction() as db:
        db.execute(
            "UPDATE messages SET created_at=? WHERE id=?",
            ((NOW + timedelta(days=1)).isoformat(), source(3).id),
        )
    query = "Where have you traveled recently?"
    candidates = memory.candidates(query, guild_id=77, now=NOW)
    assert [c.content for c in candidates] == ["I traveled to Lantern Island."]
    packet = memory.render(candidates, request=query, now=NOW)
    assert "Lantern Island" in packet and "Pebble Island" not in packet
    store.invalidate(10, [source(0).id], deleted=True, now=NOW)
    assert "no verified recent human source" in memory.render(candidates, request=query, now=NOW)


@pytest.mark.parametrize(
    "question",
    ["Where have I traveled recently?", "What have I been doing lately?"],
)
async def test_other_requester_cannot_borrow_persona_activity(memory, question):
    assert requester_recall(question)
    client, _, _, _ = make_client(clock=lambda: NOW)
    learner = MessageIngestor(memory.learning, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    client._learning, client._memory = learner, memory
    try:
        with patch.object(memory, "candidates", side_effect=AssertionError("wrong author")):
            result = await client._memory_context(
                fake_channel(),
                f"Owner: {question}",
                [],
                requester_user_id=1,
                focus_author_user_id=1,
            )
        assert "CURRENT SPEAKER RECALL" in result
    finally:
        await client.close()


async def test_recent_activity_never_adds_undated_voice_examples(memory):
    client, _, _, _ = make_client(clock=lambda: NOW)
    learner = MessageIngestor(memory.learning, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    client._learning, client._memory = learner, memory
    try:
        with patch("trubot.discord_client.voice_context", MagicMock(side_effect=AssertionError)):
            result = await client._memory_context(
                fake_channel(), "Owner: Where have you traveled recently?", []
            )
        assert "no verified recent human source" in result
        assert "Lantern Islands" not in result
    finally:
        await client.close()


@pytest.mark.parametrize("state", ["current", "changed", "unavailable", "withdrawn"])
async def test_recent_activity_source_is_rechecked_before_actual_handler_publication(memory, state):
    store = memory.learning
    text = "I traveled to Lantern Island."
    store.observe(source(content=text, created_at=NOW), now=NOW)
    client, responder, _, _ = make_client(clock=lambda: NOW)
    learner = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    client._learning, client._memory = learner, memory
    channel = fake_channel()
    anchor = fake_message(channel)
    anchor.reference, anchor.attachments, anchor.embeds = None, [], []
    generated = False

    async def refresh(_channel, identifier):
        if generated and state == "unavailable":
            raise TimeoutError
        current = "I stayed at Pebble Island." if generated and state == "changed" else text
        store.observe(source(content=current, created_at=NOW), now=NOW)
        return message(channel, identifier, text=current, created_at=NOW)

    async def reply(messages, **kwargs):
        nonlocal generated
        assert any(text in row.content and row.origin == "memory" for row in messages)
        assert kwargs["refresh_check"] is not None
        generated = True
        if state == "withdrawn":
            store.forget(now=NOW)
        return "Lantern Island."

    responder.reply = reply
    try:
        with (
            patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
            patch.object(client, "get_channel", return_value=channel),
            patch.object(learner, "refresh", side_effect=refresh),
            patch("trubot.discord_client.collect_native_episode", AsyncMock(return_value=None)),
        ):
            posted = await client._respond(
                channel,
                mode=ReplyMode.DIRECT,
                requester_user_id=1,
                anchor=anchor,
                target="Owner: Where have you traveled recently?",
            )
        assert generated
        assert posted is (state == "current")
        if posted:
            channel.send.assert_awaited_once_with("Lantern Island.")
        else:
            channel.send.assert_not_awaited()
    finally:
        await client.close()


@pytest.mark.parametrize("mode", list(ReplyMode))
async def test_requester_activity_keeps_human_ownership_through_handler(memory, mode):
    client, responder, _, _ = make_client(clock=lambda: NOW)
    channel = fake_channel()
    anchor = fake_message(channel, user_id=1)
    anchor.reference, anchor.attachments, anchor.embeds = None, [], []
    learner = MessageIngestor(memory.learning, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    client._learning, client._memory = learner, memory
    own = ConversationMessage(
        "user", "Owner: This fictional trip is to Pine Island.", author_user_id=1
    )
    rows = [
        own,
        ConversationMessage("assistant", "You went to Lantern Island."),
        ConversationMessage("user", "Owner: I went to Lantern Island.", author_user_id=2),
    ]
    try:
        with patch("trubot.discord_client.collect_history", AsyncMock(return_value=rows)):
            assert await client._respond(
                channel,
                mode=mode,
                requester_user_id=2,
                anchor=anchor,
                target="Owner: Where have I traveled recently?",
            )
        given = responder.calls[0][0]
        assert [m for m in given if m.origin != "memory"] == [own]
        assert any("CURRENT SPEAKER RECALL" in m.content for m in given)
        assert not any("Lantern Island" in m.content for m in given)
    finally:
        await client.close()
