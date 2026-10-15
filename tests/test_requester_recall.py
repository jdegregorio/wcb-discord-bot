"""A private character corpus must not establish a different speaker's own past."""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from test_discord_client import fake_channel, fake_message, make_client
from test_learning import AUDIT, NOW

from trubot.archives import ArchiveStore
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore
from trubot.memory import ContextMemory, requester_recall


@pytest.mark.parametrize(
    "question",
    [
        "What did I say about reserve rules back in 2020?",
        "Remind me what my opinion was in that old discussion.",
        "What was my old view on reserve slots?",
        "When have I actually posted about rookies?",
        "Where had I written that statement?",
        "Which did I prefer?",
        "What were my previous preferences?",
        "WHAT DID I REALLY THINK ABOUT THE RULE?",
        "Do you remember what I said about roster rules?",
        "How I reacted back then, can you remind me?",
        "Quote my old message about roster rules.",
        "Remind me of my previous opinion on roster rules.",
        "Could you quote my old words on roster rules?",
        "What did I just say about reserve slots?",
        "What baseball team have I said I support?",
        "Which side of the roster expansion debate did I support?",
        "What reserve slot proposal did I say I preferred in 2020?",
        "Which team had I previously liked?",
        "What other roster changes have I ever supported?",
        "What position did I take on roster slots?",
        "What\tbaseball team\nhave I said I support?",
        "Do you remember which baseball team have I said I support?",
    ],
)
def test_explicit_request_for_speakers_own_past(question):
    assert requester_recall(question)


@pytest.mark.parametrize(
    "question",
    [
        "What do you remember from 2020?",
        "What was your view on reserve slots?",
        "What did Andrew say about reserve slots?",
        "If I wanted two slots, what would you say?",
        "What would I pick in this fictional league?",
        "What did we say about that?",
        'Quote your line "What did I say about reserve slots?"',
        "What did you mean by “What was my opinion?”",
        "I want to know what your old opinion was.",
        "Remind me what my league uses for scoring.",
        "Should I quote my old message, or rewrite it?",
        "What baseball team have you said you support?",
        "Which side of the debate did Andrew support?",
        "Which side would I support in a fictional league?",
        "What would you say if I supported two slots?",
        "What would you think if I said I supported two slots?",
        'Quote your line "What baseball team have I said I support?"',
        "Explain “Which side of the debate did I support?” as grammar.",
        'Quote your line "What baseball team\nhave I said I support?"',
        "What baseball team would you say I support?",
        "What roster slot should I take?",
    ],
)
def test_persona_recall_hypotheticals_and_quotes_keep_current_routing(question):
    assert not requester_recall(question)


@pytest.fixture
def client_memory(tmp_path):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    archive = ArchiveStore.initialize(store)
    archive.import_document(
        b"fixture.target\n  8:01 AM\nI preferred two reserve slots to unlimited slots.",
        channel="fixture",
        target_alias="fixture.target",
        alias_basis="Entirely invented attribution",
        origin={"kind": "synthetic"},
        period_hint="fixture_2020.txt",
        now=NOW,
    )
    client, responder, _, _ = make_client()
    learning = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learning.verified = True
    client._learning, client._memory = learning, ContextMemory(store)
    return client, responder, store


@pytest.mark.asyncio
@pytest.mark.parametrize("author_id", [1, None])
@pytest.mark.parametrize(
    "question_text",
    [
        "What did I say about reserve rules back in 2020?",
        "What reserve slot proposal did I say I preferred in 2020?",
    ],
)
async def test_other_or_unknown_author_never_retrieves_character_sources(
    client_memory, author_id, question_text
):
    client, _, store = client_memory
    question = "Andrew Truax: " + question_text
    try:
        with (
            patch.object(
                client._memory, "candidates", wraps=client._memory.candidates
            ) as candidates,
            patch("trubot.discord_client.voice_context") as voice,
        ):
            result = await client._memory_context(
                fake_channel(),
                question,
                [ConversationMessage("assistant", "You preferred two reserve slots.")],
                requester_user_id=42,
                focus_author_user_id=author_id,
            )
        assert "CURRENT SPEAKER RECALL" in result
        assert "two reserve slots" not in result
        assert "Earlier bot replies" in result
        candidates.assert_not_called()
        voice.assert_not_called()
        assert store.status()["messages"] == 0
    finally:
        await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "question_text",
    [
        "What did I say about reserve slots in 2020?",
        "What reserve slot proposal did I say I preferred in 2020?",
    ],
)
async def test_verified_source_author_keeps_own_history_retrieval(client_memory, question_text):
    client, _, _ = client_memory
    try:
        result = await client._memory_context(
            fake_channel(),
            "A different display name: " + question_text,
            [],
            requester_user_id=1,
            focus_author_user_id=42,
        )
        assert "I preferred two reserve slots" in result
        assert "CURRENT SPEAKER RECALL" not in result
    finally:
        await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", [ReplyMode.DIRECT, ReplyMode.FOLLOW_UP, ReplyMode.REACTION])
@pytest.mark.parametrize(
    "question_text",
    [
        "What did I say about reserve slots in 2020?",
        "What reserve slot proposal did I say I preferred in 2020?",
    ],
)
async def test_real_handler_scopes_to_focus_author_not_reactor(client_memory, mode, question_text):
    client, responder, _ = client_memory
    channel = fake_channel()
    anchor = fake_message(channel, user_id=1)
    anchor.clean_content = anchor.content = question_text
    anchor.author.display_name = "Andrew Truax"
    try:
        assert await client._respond(
            channel,
            mode=mode,
            requester_user_id=42,
            anchor=anchor,
            target="Andrew Truax: " + question_text,
        )
        memory = next(m.content for m in responder.calls[0][0] if m.origin == "memory")
        assert "CURRENT SPEAKER RECALL" in memory
        assert "I preferred two reserve slots" not in memory
        # The available live peer history remains in the normal channel context.
        assert responder.calls[0][0][0].content == "Joe: Code 12346633"
        channel.send.assert_awaited_once_with("Hot")
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_development_permission_and_withdrawal_precede_subject_routing(client_memory):
    client, _, store = client_memory
    channel = fake_channel()
    channel.guild = SimpleNamespace(id=client._settings.development_guild_id, owner_id=1)
    question = "Peer: What did I say about reserve slots?"
    try:
        denied = await client._memory_context(
            channel, question, [], requester_user_id=2, focus_author_user_id=1
        )
        assert denied == ""
        allowed = await client._memory_context(
            channel, question, [], requester_user_id=1, focus_author_user_id=1
        )
        assert "CURRENT SPEAKER RECALL" in allowed
        store.forget(now=NOW + timedelta(seconds=1))
        withdrawn = await client._memory_context(
            channel, question, [], requester_user_id=1, focus_author_user_id=1
        )
        assert withdrawn == ""
    finally:
        await client.close()
