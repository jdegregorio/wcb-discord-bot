"""Historical authorship must survive the actual incoming-event/publication path."""

import hashlib
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from test_discord_client import fake_channel, fake_message, make_client, message_for_history
from test_learning import AUDIT, NOW

from trubot.archives import ArchiveStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore
from trubot.memory import ContextMemory


def harness(tmp_path, body):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    archive = ArchiveStore.initialize(store)
    raw = (
        "legacy.target\n  8:00 AM\nI order caramel after dinner.\nlegacy.target\n  8:01 AM\n" + body
    ).encode()
    archive.import_document(
        raw,
        channel="synthetic",
        target_alias="legacy.target",
        alias_basis="Synthetic audit",
        origin={"kind": "synthetic"},
        now=NOW,
    )
    client, responder, _, _ = make_client(clock=lambda: NOW)
    learning = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learning.verified = True
    client._learning, client._memory = learning, ContextMemory(store)
    channel = fake_channel()

    async def history(**_kwargs):
        yield message_for_history("Synthetic setup about dessert.", author_id=1)

    channel.history = history
    message = fake_message(channel)
    message.id = 12345
    message.content = message.clean_content = "🤖 What clarification do you remember about caramel?"
    channel.fetch_message.return_value = message
    client._attention.activate(10, NOW)
    return client, responder, channel, message, store, archive, hashlib.sha256(raw).hexdigest()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
@pytest.mark.parametrize(
    "body,flag",
    [
        ("replied to a thread:\nI prefer vanilla.", "thread_quote_ambiguous"),
        ("https://example.test/dessert\nI prefer vanilla.", "link_preview_ambiguous"),
        ("Image from iOS\nI prefer vanilla.", "attachment_or_preview"),
    ],
)
async def test_incoming_events_preserve_ambiguous_historical_authorship(tmp_path, mode, body, flag):
    client, responder, channel, message, store, _, _ = harness(tmp_path, body)
    try:
        with patch.object(client, "get_channel", return_value=channel):
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
                    message.content = message.clean_content = message.content.removeprefix("🤖 ")
                await client.on_message(message)
        assert len(responder.calls) == 1
        rendered = "\n".join(m.content for m in responder.calls[0][0] if m.origin == "memory")
        assert "I order caramel after dinner." in rendered
        assert "ambiguous target block (not authored evidence)" in rendered
        assert '"author_role": "ambiguous_target_context_only"' in rendered
        assert flag in rendered and "I prefer vanilla." in rendered
        channel.send.assert_awaited_once_with("Hot")
        assert store.status()["messages"] == 0  # No development/peer evidence is learned.
    finally:
        await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("change", ["source_removed", "withdrawal"])
async def test_changed_historical_evidence_stops_handler_publication(tmp_path, change):
    client, responder, channel, message, store, archive, digest = harness(
        tmp_path, "replied to a thread:\nI prefer vanilla."
    )
    original = responder.reply

    async def change_after_generation(*args, **kwargs):
        answer = await original(*args, **kwargs)
        if change == "source_removed":
            archive.remove_document(digest, now=NOW)
        else:
            store.forget(now=NOW)
        return answer

    responder.reply = change_after_generation
    try:
        with patch.object(client, "get_channel", return_value=channel):
            await client.on_message(message)
        assert len(responder.calls) == 1
        channel.send.assert_not_awaited()
    finally:
        await client.close()
