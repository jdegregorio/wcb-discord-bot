"""Authored facts do not need to carry another speaker's adjacent stance."""

import json

import pytest
from test_authored_completeness import archived
from test_learning import NOW, source

from trubot.learning import LearningUnavailable
from trubot.native_context import NativeEpisode

AUTHORED = "I oppose mascot slots. I would accept two reserve slots, not active slots."
PEER = "I support replacing kickers."


@pytest.mark.parametrize(
    "question",
    [
        "What do you remember about league roster discussions around 2020?",
        "What did Andrew say about mascot slots?",
        "What view did you express in this league discussion?",
        "Which proposal did you support?",
        "Do you recall your old roster position?",
    ],
)
def test_ordinary_authored_recall_excludes_adjacent_stances(tmp_path, question):
    _, _, memory = archived(tmp_path, AUTHORED)
    candidates = memory.candidates("mascot", guild_id=77, now=NOW)
    packet = memory.render_packet(candidates, request=question, now=NOW)
    evidence = json.loads(packet.text.split("\n", 1)[1])
    assert evidence[0]["text"] == AUTHORED
    assert PEER not in packet.text
    assert "adjacent_context_only" not in evidence[0]
    assert evidence[0]["source"] == candidates[0].source
    assert not packet.allow_voice_examples


@pytest.mark.parametrize(
    "question",
    [
        "What was the setup for your mascot comment?",
        "Explain the joke about mascot slots.",
        "What context was that mascot remark responding to?",
        "What was said before your mascot comment?",
        "Show the conversation around your mascot reply.",
        "What evidence supports your mascot stance?",
        "Quote what you said about mascot slots.",
        "What would you say about mascot slots?",
        "",
    ],
)
def test_context_and_creative_requests_keep_separate_human_setup(tmp_path, question):
    _, _, memory = archived(tmp_path, AUTHORED)
    packet = memory.render_packet(
        memory.candidates("mascot", guild_id=77, now=NOW), request=question, now=NOW
    )
    evidence = json.loads(packet.text.split("\n", 1)[1])
    assert evidence[0]["text"] == AUTHORED
    assert PEER in packet.text
    assert evidence[0]["adjacent_context_only"][0]["author"] == "peer (not persona evidence)"
    assert packet.allow_voice_examples


def test_exact_quote_and_native_setup_are_preserved(tmp_path):
    store, _, memory = archived(tmp_path, AUTHORED)
    candidates = memory.candidates("mascot", guild_id=77, now=NOW)
    packet = memory.render_packet(
        candidates, request="What did Andrew say?", quotation="I oppose mascot slots", now=NOW
    )
    assert PEER in packet.text
    store.observe(source(content="No mascot slots."), now=NOW)
    episode = NativeEpisode("No mascot slots.", None, ({"author": "peer", "text": PEER},))
    candidates = [
        c
        for c in memory.candidates("mascot", guild_id=77, now=NOW)
        if c.source["kind"] == "discord"
    ]
    packet = memory.render_packet(
        candidates, request="What did Andrew say?", native_episodes={source().id: episode}, now=NOW
    )
    assert PEER in packet.text
    assert packet.allow_voice_examples


def test_authored_recall_rechecks_edit_removal_and_withdrawal(tmp_path):
    store, archive, memory = archived(tmp_path, AUTHORED)
    candidates = memory.candidates("mascot", guild_id=77, now=NOW)
    with archive._transaction() as db:
        db.execute("UPDATE messages SET content=? WHERE target=1", ("Keep mascots.",))
    packet = memory.render_packet(candidates, request="What did you say?", now=NOW)
    assert "Keep mascots." in packet.text and AUTHORED not in packet.text
    archive.remove_document(candidates[0].source["document"], now=NOW)
    assert not memory.render(candidates, request="What did you say?", now=NOW)
    store.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        memory.render(candidates, request="What did you say?", now=NOW)


@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_authored_recall_handlers_do_not_restore_adjacent_voice(tmp_path, mode):
    from dataclasses import replace
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, patch

    from test_discord_client import fake_channel, fake_message, make_client

    from trubot.ingestion import MessageIngestor
    from trubot.memory import ContextMemory

    store, _, _ = archived(tmp_path, AUTHORED)
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._settings = replace(client._settings, development_guild_id=78)
    ingestor = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(store)
    channel = fake_channel()
    channel.guild = SimpleNamespace(id=78, owner_id=1)
    message = fake_message(channel)
    message.content = message.clean_content = "🤖 What did Andrew say about mascot slots?"
    channel.fetch_message.return_value = message
    client._attention.activate(10, NOW)
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "get_channel", return_value=channel),
        patch("trubot.discord_client.voice_context", return_value=PEER) as voice,
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
                message.content = message.clean_content = "What did Andrew say about mascot slots?"
            await client.on_message(message)
        assert len(responder.calls) == 1
        packets = [m.content for m in responder.calls[0][0] if m.origin == "memory"]
        assert len(packets) == 1
        assert AUTHORED in packets[0] and PEER not in packets[0]
        voice.assert_not_called()
        channel.send.assert_awaited_once_with("Hot")
        assert store.status()["messages"] == 0
    await client.close()
