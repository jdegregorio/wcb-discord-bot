"""Synthetic Discord replies select a human topic, never human evidence."""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import discord
import pytest
from test_behavioral_memory import imported
from test_discord_client import fake_channel, fake_message, make_client, message_for_history
from test_learning import NOW
from test_memory_continuity import stores as continuity_stores

from trubot.conversation import ConversationMessage as M
from trubot.ingestion import MessageIngestor
from trubot.memory import ContextMemory
from trubot.reply_focus import memory_followup_query
from trubot.vision import ImageCollector

stores = continuity_stores


def reference(text, *, role="user", author=2, images=()):
    return M(
        role,
        "REFERENCED MESSAGE (context only): Friend: " + text,
        images,
        origin="reference",
        author_user_id=author,
    )


def test_explicit_human_reference_wins_over_unrelated_immediate_exchange():
    history = [
        M("user", "Friend: Pick a dessert."),
        M("assistant", "Cake."),
        reference("Training progress took a year of work."),
    ]
    assert memory_followup_query("How would you handle that?", history) == (
        "Training progress took a year of work."
    )


async def test_reply_conversion_preserves_authenticated_human_search_subject():
    client, _, _, _ = make_client(clock=lambda: NOW)
    channel = fake_channel()
    anchor = fake_message(channel, direct=True)
    anchor.reference = discord.MessageReference(message_id=123, channel_id=channel.id)
    old = message_for_history("Training progress after a year of work.", author_id=2)
    old.created_at = NOW - timedelta(days=10)
    channel.fetch_message.return_value = old
    try:
        row = await client._reference_context(anchor, ImageCollector())
        assert row is not None and row.author_user_id == 2
        assert memory_followup_query("What do you think about that?", [row]) == old.clean_content
    finally:
        await client.close()


@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_explicit_reply_retrieves_qualified_abstraction_through_handlers(stores, mode):
    learning, _, _ = imported(stores, "value")
    client, responder, _, _ = make_client(clock=lambda: NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(learning)
    channel = fake_channel()

    async def history(**_kwargs):
        yield message_for_history("Pick a dessert.", author_id=1)

    channel.history = history
    old = message_for_history("Training progress after a year of work.", author_id=2)
    old.created_at = NOW - timedelta(days=10)
    channel.fetch_message.return_value = old
    anchor = fake_message(channel, direct=mode == "direct")
    anchor.id, anchor.guild = 456, channel.guild
    anchor.reference = discord.MessageReference(message_id=123, channel_id=10)
    anchor.attachments, anchor.embeds = [], []
    anchor.content = anchor.clean_content = (
        "🤖 " if mode == "direct" else ""
    ) + "How would you handle that?"
    try:
        with (
            patch.object(client, "get_channel", return_value=channel),
            patch.object(ingestor, "refresh_page", AsyncMock(return_value={})),
            patch.object(ingestor, "refresh", new_callable=AsyncMock),
        ):
            if mode == "reaction":

                async def fetch(message_id):
                    return anchor if message_id == anchor.id else old

                channel.fetch_message.side_effect = fetch
                await client.on_raw_reaction_add(
                    SimpleNamespace(
                        user_id=1,
                        channel_id=10,
                        message_id=anchor.id,
                        emoji=SimpleNamespace(name="ThomasJones"),
                        member=SimpleNamespace(bot=False),
                    )
                )
            else:
                if mode == "followup":
                    client._attention.activate(10, NOW)
                await client.on_message(anchor)
        context = "\n".join(m.content for m in responder.calls[0][0])
        assert "ABSTRACT EPISODE MEMORY" in context
        assert "Listen during setbacks" in context
        assert responder.calls[0][3].endswith("How would you handle that?")
        channel.send.assert_awaited_once()
    finally:
        await client.close()


@pytest.mark.parametrize(
    "row",
    [
        reference("Training progress", author=None),
        reference("Training progress", role="assistant"),
        reference("Training progress" * 50),
        reference("Training progress…"),
        reference(""),
        reference("[image attached]"),
        reference("[message with no text]"),
        reference("Training progress [image pixels unavailable]"),
        M("user", "[Referenced message unavailable.]", origin="reference"),
        M("user", "Friend: Training progress", origin="reference", author_user_id=2),
    ],
)
def test_ineligible_reference_cannot_borrow_unrelated_neighbor(row):
    history = [M("user", "Friend: Pick a dessert."), M("assistant", "Cake."), row]
    assert memory_followup_query("What do you think?", history) == "What do you think?"


def test_pixels_and_ambiguous_multiple_references_do_not_create_text_subject():
    from trubot.conversation import ConversationImage

    row = reference("Training progress", images=(ConversationImage("data:invented", "test"),))
    assert memory_followup_query("Why?", [row]) == "Why?"
    assert memory_followup_query("Why?", [reference("one"), reference("two")]) == "Why?"


@pytest.mark.parametrize(
    "question",
    [
        "What do you think about baseball?",
        "What have I said about that?",
        "Show the evidence for that.",
        "What exact day was that?",
        "What did Andrew actually say?",
        "What is my favorite team?",
    ],
)
def test_reference_does_not_replace_explicit_subject_ownership_or_evidence_intent(question):
    assert memory_followup_query(question, [reference("Training progress")]) == question


@pytest.mark.parametrize("failure", ["denied", "missing", "cross_channel", "no_id", "bot_spoof"])
async def test_reference_transport_preserves_access_and_authorship(failure):
    client, _, _, _ = make_client()
    channel = fake_channel()
    anchor = fake_message(channel)
    anchor.reference = discord.MessageReference(
        message_id=None if failure == "no_id" else 123,
        channel_id=11 if failure == "cross_channel" else channel.id,
    )
    if failure in {"denied", "missing"}:
        error = discord.Forbidden if failure == "denied" else discord.NotFound
        channel.fetch_message.side_effect = error(
            SimpleNamespace(status=403, reason="test"), "test"
        )
    else:
        # Human-looking content from a bot cannot establish a human search subject.
        row = message_for_history("Friend: Training progress", author_id=888, bot=True)
        row.content = row.clean_content
        channel.fetch_message.return_value = row
    try:
        row = await client._reference_context(anchor, ImageCollector())
        assert row is not None and row.author_user_id is None
        assert memory_followup_query("Why?", [row]) == "Why?"
        if failure in {"cross_channel", "no_id"}:
            channel.fetch_message.assert_not_awaited()
        else:
            channel.fetch_message.assert_awaited_once_with(123)
    finally:
        await client.close()


@pytest.mark.parametrize("change", ["retire", "correction", "withdrawal", "requester"])
async def test_reference_lookup_keeps_source_and_author_lifecycle(stores, change):
    from test_learning import source

    learning, graph, _ = imported(stores, "value")
    client, _, _, _ = make_client(clock=lambda: NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(learning)
    channel = fake_channel()
    history = [reference("training progress")]
    try:
        with (
            patch.object(client, "get_channel", return_value=channel),
            patch.object(ingestor, "refresh_page", AsyncMock(return_value={})),
            patch.object(ingestor, "refresh", new_callable=AsyncMock),
        ):
            before = await client._memory_context(channel, "How would you handle that?", history)
            assert "ABSTRACT EPISODE MEMORY" in before
            if change == "retire":
                graph.remove("observation:dessert")
            elif change == "correction":
                learning.invalidate(10, [source().id], deleted=False, now=NOW)
            elif change == "withdrawal":
                learning.forget(now=NOW)
            request = (
                "What have I said about that?"
                if change == "requester"
                else "How would you handle that?"
            )
            after = await client._memory_context(channel, request, history, focus_author_user_id=1)
            assert "ABSTRACT EPISODE MEMORY" not in after
    finally:
        await client.close()
