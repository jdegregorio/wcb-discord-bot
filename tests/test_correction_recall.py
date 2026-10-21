"""Explicit correction recall needs peer setup without making it authored evidence."""

import json

import pytest
from test_authored_completeness import archived
from test_learning import NOW

AUTHORED = "If the draft is delayed, do our third-round picks disappear?"
CORRECTION = "No. Picks carry over. Only waiver priority resets."


@pytest.mark.parametrize(
    "question",
    [
        "What correction do you remember about the draft delay?",
        "What corrections did you recall about draft picks?",
        "What clarification do you remember about the draft delay?",
        "What clarifications did you recall about draft picks?",
        "What did you say that got corrected about draft picks?",
        "Do you remember how the draft rule was clarified?",
    ],
)
def test_correction_recall_keeps_complete_peer_explanation(tmp_path, question):
    _, archive, memory = archived(tmp_path, AUTHORED)
    with archive._transaction() as db:
        db.execute("UPDATE messages SET content=? WHERE target=0", (CORRECTION,))
    selected = memory.candidates("draft", guild_id=77, now=NOW)
    packet = memory.render_packet(selected, request=question, now=NOW)
    evidence = json.loads(packet.text.split("\n", 1)[1])
    assert evidence[0]["text"] == AUTHORED
    assert evidence[0]["source"] == selected[0].source
    assert evidence[0]["adjacent_context_only"] == [
        {"author": "peer (not persona evidence)", "text": CORRECTION}
    ]
    assert not packet.allow_voice_examples


@pytest.mark.parametrize(
    "question",
    [
        "What did you say about draft picks?",
        "What do you remember about the draft?",
        "What view did you express about draft picks?",
        "Do you recall your draft position?",
        "What did you say about autocorrection?",
        "What did you say about clarificationism?",
    ],
)
def test_ordinary_authored_recall_still_excludes_peer_stances(tmp_path, question):
    _, _, memory = archived(tmp_path, AUTHORED)
    packet = memory.render_packet(
        memory.candidates("draft", guild_id=77, now=NOW), request=question, now=NOW
    )
    evidence = json.loads(packet.text.split("\n", 1)[1])
    assert evidence[0]["text"] == AUTHORED
    assert "adjacent_context_only" not in evidence[0]
    assert not packet.allow_voice_examples


@pytest.mark.parametrize("body", [CORRECTION, "x" * 600, "🦆" * 151])
def test_correction_context_keeps_existing_complete_or_gap_bound(tmp_path, body):
    _, archive, memory = archived(tmp_path, AUTHORED)
    with archive._transaction() as db:
        db.execute("UPDATE messages SET content=? WHERE target=0", (body,))
    packet = memory.render_packet(
        memory.candidates("draft", guild_id=77, now=NOW),
        request="What correction do you remember about draft picks?",
        now=NOW,
    )
    item = json.loads(packet.text.split("\n", 1)[1])[0]
    if len(body.encode()) <= 600:
        assert item["adjacent_context_only"][0]["text"] == body
        assert not item["context_gaps"]
    else:
        assert not item["adjacent_context_only"]
        assert "omitted" in item["context_gaps"][0]
        assert body[:20] not in packet.text
    assert not packet.allow_voice_examples


def test_correction_words_in_source_cannot_select_context_route(tmp_path):
    _, _, memory = archived(tmp_path, "I corrected the draft list. " + AUTHORED)
    packet = memory.render_packet(
        memory.candidates("draft", guild_id=77, now=NOW),
        request="What do you remember about draft picks?",
        now=NOW,
    )
    assert "adjacent_context_only" not in packet.text


@pytest.mark.parametrize("change", ["peer_edit", "removal", "withdrawal", "unchanged"])
async def test_correction_context_changes_are_checked_before_publication(tmp_path, change):
    from dataclasses import replace
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, patch

    from test_discord_client import fake_channel, fake_message, make_client

    from trubot.conversation import ReplyMode
    from trubot.ingestion import MessageIngestor
    from trubot.memory import ContextMemory

    store, archive, _ = archived(tmp_path, AUTHORED)
    with archive._transaction() as db:
        db.execute("UPDATE messages SET content=? WHERE target=0", (CORRECTION,))
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._settings = replace(client._settings, development_guild_id=78)
    ingestor = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(store)
    channel = fake_channel()
    channel.guild = SimpleNamespace(id=78, owner_id=1)
    message = fake_message(channel)
    message.content = message.clean_content = "What correction do you remember about draft picks?"
    seen = []

    async def reply(messages, **kwargs):
        packets = [m.content for m in messages if m.origin == "memory"]
        assert len(packets) == 1 and CORRECTION in packets[0]
        assert '"author": "peer (not persona evidence)"' in packets[0]
        seen.append(True)
        if change == "peer_edit":
            with archive._transaction() as db:
                db.execute("UPDATE messages SET content=? WHERE target=0", ("Changed setup.",))
        elif change == "removal":
            ref = client._memory.candidates("draft", guild_id=77, now=NOW)[0].source
            archive.remove_document(ref["document"], now=NOW)
        elif change == "withdrawal":
            store.forget(now=NOW)
        return "The picks carry over."

    responder.reply = reply
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch("trubot.discord_client.voice_context", return_value="") as voice,
    ):
        result = await client._respond(
            channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=1,
            anchor=message,
            target=message.content,
        )
        assert voice.call_count == (1 if change == "removal" else 0)
    assert seen == [True]
    assert result is (change == "unchanged")
    if change == "unchanged":
        channel.send.assert_awaited_once_with("The picks carry over.")
    else:
        channel.send.assert_not_awaited()
    assert store.status()["messages"] == 0
    await client.close()
