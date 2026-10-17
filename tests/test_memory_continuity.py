"""Invented human setups should carry useful memory into immediate follow-ups."""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from test_behavioral_memory import imported
from test_discord_client import fake_channel, fake_message, make_client, message_for_history
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.conversation import ConversationMessage as M
from trubot.graph import GraphStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore
from trubot.memory import ContextMemory
from trubot.reply_focus import MAX_FOCUS_CHARS, memory_followup_query


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    archive = ArchiveStore.initialize(learning)
    graph = GraphStore.initialize(learning)
    texts = (
        "Training progress took months.",
        "Hard training progress deserves credit.",
        "Just listen.",
    )
    for i, text in enumerate(texts):
        learning.observe(source(i, content=text, created_at=NOW - timedelta(days=i + 1)), now=NOW)
    graph.populate(now=NOW)
    return learning, archive, graph


@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_followup_retrieves_qualified_abstraction_from_human_setup(stores, mode):
    learning, _, _ = imported(stores, "value")
    client, responder, _, _ = make_client(clock=lambda: NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(learning)
    channel = fake_channel()
    rows = [
        message_for_history("Training progress after a year of work.", author_id=1),
        message_for_history("That is an achievement.", author_id=999, bot=True),
    ]

    async def history(**_kwargs):
        for row in reversed(rows):
            yield row

    channel.history = history
    message = fake_message(channel, direct=mode == "direct")
    message.id, message.guild, message.reference = 123, channel.guild, None
    message.attachments, message.embeds = [], []
    message.content = message.clean_content = (
        "🤖 " if mode == "direct" else ""
    ) + "How would you handle that?"
    try:
        with (
            patch.object(client, "get_channel", return_value=channel),
            patch.object(ingestor, "refresh_page", AsyncMock(return_value={})),
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
        assert "ABSTRACT EPISODE MEMORY" in context
        assert "Listen during setbacks" in context
        assert responder.calls[0][3].endswith("How would you handle that?")
        channel.send.assert_awaited_once()
    finally:
        await client.close()


@pytest.mark.parametrize(
    "question",
    [
        "How would you handle that?",
        "🤖 How would you handle that?",
        "@Trubot What do you think about that?",
        "What would you do?",
        "So which one would you pick?",
        "Tell me more about it.",
        "Why?",
    ],
)
def test_only_complete_generic_followups_use_the_complete_setup(question):
    setup = "Training progress is worth recognizing, unless they ask for quiet support."
    history = [M("user", "Friend: " + setup), M("assistant", "Not human evidence.")]
    assert memory_followup_query(question, history) == setup


@pytest.mark.parametrize(
    "question",
    [
        "How would you handle that baseball trade?",
        "What do you think about hiking?",
        "What baseball team have I said I support?",
        "What exact day was that?",
        'Show evidence for "training progress".',
        "What did Andrew say about that?",
        "Training progress",
        "Can you tell me why you dislike it?",
        "",
    ],
)
def test_explicit_subject_ownership_and_evidence_intent_do_not_borrow_context(question):
    history = [M("user", "Friend: training progress"), M("assistant", "Sure.")]
    assert memory_followup_query(question, history) == question


@pytest.mark.parametrize(
    "history",
    [
        [],
        [M("assistant", "Training progress")],
        [M("user", "Friend: training progress")],
        [
            M("user", "Friend: training progress"),
            M("assistant", "Good."),
            M("user", "Friend: new subject"),
        ],
        [
            M("user", "Friend: training progress"),
            M("assistant", "Good."),
            M("assistant", "Extra bot topic"),
        ],
        [M("user", "Friend: training progress", origin="memory"), M("assistant", "Good.")],
        [M("user", "Friend: training progress", origin="reference"), M("assistant", "Good.")],
        [M("user", "Friend: training progress", origin="focus"), M("assistant", "Good.")],
        [M("user", "Friend: " + "x" * (MAX_FOCUS_CHARS + 1)), M("assistant", "Good.")],
        [M("user", "Friend: training progress…"), M("assistant", "Good.")],
        [M("user", "Friend: "), M("assistant", "Good.")],
    ],
)
def test_ambiguous_incomplete_or_nonhuman_setup_does_not_activate_lookup(history):
    assert (
        memory_followup_query("How would you handle that?", history) == "How would you handle that?"
    )


def test_new_human_subject_wins_over_memory_and_visual_rows():
    h = [
        M("user", "Friend: old training progress"),
        M("assistant", "Good."),
        M("user", "Friend: a quiet afternoon"),
        M("assistant", "Nice training progress."),
        M("user", "training progress", origin="memory"),
        M("user", "training progress", origin="focus"),
    ]
    assert memory_followup_query("What do you think?", h) == "a quiet afternoon"


@pytest.mark.parametrize("change", ["retire", "correction", "withdrawal", "requester"])
async def test_followup_query_preserves_source_and_author_lifecycle(stores, change):
    learning, graph, _ = imported(stores, "value")
    client, _, _, _ = make_client(clock=lambda: NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(learning)
    channel = fake_channel()
    history = [M("user", "Friend: training progress"), M("assistant", "Good.")]
    request = "How would you handle that?"
    try:
        with (
            patch.object(client, "get_channel", return_value=channel),
            patch.object(ingestor, "refresh_page", AsyncMock(return_value={})),
            patch.object(ingestor, "refresh", new_callable=AsyncMock),
        ):
            before = await client._memory_context(channel, request, history, focus_author_user_id=1)
            assert "ABSTRACT EPISODE MEMORY" in before
            if change == "retire":
                graph.remove("observation:dessert")
            elif change == "correction":
                learning.invalidate(10, [source(0).id], deleted=False, now=NOW)
            elif change == "withdrawal":
                learning.forget(now=NOW)
            else:
                request = "What training progress have I said I made?"
            after = await client._memory_context(channel, request, history, focus_author_user_id=1)
            assert "ABSTRACT EPISODE MEMORY" not in after
    finally:
        await client.close()


async def test_final_source_check_still_discards_an_expanded_memory_reply(stores):
    from trubot.conversation import ReplyMode

    learning, graph, _ = imported(stores, "value")
    client, responder, _, _ = make_client(clock=lambda: NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(learning)
    channel = fake_channel()
    anchor = fake_message(channel)
    anchor.reference, anchor.attachments, anchor.embeds = None, [], []
    history = [M("user", "Friend: training progress"), M("assistant", "Good.")]

    async def reply(messages, **_kwargs):
        assert any("ABSTRACT EPISODE MEMORY" in m.content for m in messages)
        graph.remove("observation:dessert")
        return "This draft used the retired memory."

    responder.reply = reply
    try:
        with (
            patch("trubot.discord_client.collect_history", AsyncMock(return_value=history)),
            patch.object(client, "get_channel", return_value=channel),
            patch.object(ingestor, "refresh_page", AsyncMock(return_value={})),
            patch.object(ingestor, "refresh", new_callable=AsyncMock),
        ):
            assert not await client._respond(
                channel,
                mode=ReplyMode.DIRECT,
                requester_user_id=1,
                anchor=anchor,
                target="How would you handle that?",
            )
        channel.send.assert_not_awaited()
    finally:
        await client.close()
