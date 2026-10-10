import json
from unittest.mock import patch

import pytest
from test_learning import AUDIT, NOW

from trubot.archives import ArchiveStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.personality import StyleExample
from trubot.voice_memory import voice_context


@pytest.fixture
def archive(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return ArchiveStore.initialize(learning)


def add(archive, body, index=0, period_hint=None):
    return archive.import_document(
        body.encode(),
        channel="synthetic",
        target_alias="legacy.target",
        alias_basis="Synthetic operator approval",
        origin={"kind": "synthetic", "index": index},
        period_hint=period_hint,
        now=NOW,
    )


def test_catalog_alone_never_provides_evidence_and_missing_state_is_optional(archive):
    assert voice_context(archive.learning, "hello", guild_id=77) == ""
    archive.path.unlink()
    assert voice_context(archive.learning, "hello", guild_id=77) == ""


def test_both_roles_must_match_current_sources_with_provenance_and_corrections(archive):
    add(
        archive,
        "peer\n  8:00 AM\nHow is your garden?\nlegacy.target\n  8:01 AM\nTomatoes win again.",
    )
    catalog = (StyleExample("How is your garden?", "Tomatoes win again."),)
    with patch("trubot.voice_memory.STYLE_EXAMPLES", catalog):
        assert voice_context(archive.learning, "garden", guild_id=78) == ""
        result = voice_context(archive.learning, "garden", guild_id=77)
        data = json.loads(result.split("\n", 1)[1])
        assert len(data) == 1
        assert data[0]["andrew_authored_words"] == "Tomatoes win again."
        assert data[0]["preceding_peer_context_only"] == "How is your garden?"
        assert data[0]["source"]["unknown_date"] is True
        assert data[0]["source"]["target_lines"] == [4, 6]
        assert "not a derived trait" in data[0]["source"]["status"]
        digest = data[0]["source"]["document"]
        archive.remove_document(digest, now=NOW)
        assert voice_context(archive.learning, "garden", guild_id=77) == ""
        archive.learning.forget(now=NOW)
        with pytest.raises(LearningUnavailable):
            voice_context(archive.learning, "garden", guild_id=77)


@pytest.mark.parametrize(
    "body",
    [
        "peer\n  8:00 AM\nHow is your garden?\npeer\n  8:01 AM\nTomatoes win again.",
        "legacy.target\n  8:00 AM\nTomatoes win again.\npeer\n  8:01 AM\nHow is your garden?",
        "peer\n  8:00 AM\nUnrelated setup\nlegacy.target\n  8:01 AM\nTomatoes win again.",
        'peer\n  8:00 AM\nHow is your garden?\nlegacy.target\n  8:01 AM\n"Tomatoes win again."',
        "peer\n  8:00 AM\nHow is your garden?\nlegacy.target\n  8:01 AM\n"
        "Tim said Tomatoes win again.",
        "peer\n  8:00 AM\nHow is your garden?\nlegacy.target\n  8:01 AM\n"
        "replied to a thread:\nTomatoes win again.",
        "peer\n  8:00 AM\nreplied to a thread:\nHow is your garden?\n"
        "legacy.target\n  8:01 AM\nTomatoes win again.",
        "legacy.target\n  8:00 AM\nHow is your garden?\n"
        "legacy.target\n  8:01 AM\nTomatoes win again.",
    ],
)
def test_peer_quotes_missing_setup_and_reversed_context_are_not_voice(archive, body):
    add(archive, body)
    with patch(
        "trubot.voice_memory.STYLE_EXAMPLES",
        (StyleExample("How is your garden?", "Tomatoes win again."),),
    ):
        assert voice_context(archive.learning, "garden", guild_id=77) == ""


def test_examples_are_bounded_deduplicated_and_relevance_ranked(archive):
    catalog = []
    for i in range(6):
        topic = "garden" if i == 5 else "race"
        setup, reply = f"How was the {topic} number {i}?", f"Victory number {i}."
        catalog.append(StyleExample(setup, reply))
        body = f"peer\n  8:00 AM\n{setup}\nlegacy.target\n  8:01 AM\n{reply}"
        add(archive, body, i)
        add(archive, body, i + 10)
    with patch("trubot.voice_memory.STYLE_EXAMPLES", tuple(catalog)):
        result = voice_context(archive.learning, "garden", guild_id=77)
        data = json.loads(result.split("\n", 1)[1])
        assert len(data) == 3
        assert "garden" in data[0]["preceding_peer_context_only"]
        assert len({x["andrew_authored_words"] for x in data}) == 3
        assert len(result) < 10_000


def test_nearby_examples_do_not_duplicate_a_conversation(archive):
    add(
        archive,
        "peer\n  8:00 AM\nSetup zero\nlegacy.target\n  8:01 AM\nResponse zero\n"
        "peer\n  8:02 AM\nSetup one\nlegacy.target\n  8:03 AM\nResponse one",
    )
    with patch(
        "trubot.voice_memory.STYLE_EXAMPLES",
        (StyleExample("Setup zero", "Response zero"), StyleExample("Setup one", "Response one")),
    ):
        result = voice_context(archive.learning, "hello", guild_id=77)
        assert len(json.loads(result.split("\n", 1)[1])) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_source_checked_voice_reaches_handlers_without_becoming_learning(archive, mode):
    from dataclasses import replace
    from types import SimpleNamespace

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

    async def empty_history(**_kwargs):
        for item in []:
            yield item

    channel.history = empty_history
    message = fake_message(channel)
    message.content = message.clean_content = "🤖 hello there"
    channel.fetch_message.return_value = message
    client._attention.activate(10, NOW)
    with (
        patch(
            "trubot.voice_memory.STYLE_EXAMPLES",
            (StyleExample("How is your garden?", "Tomatoes win again."),),
        ),
        patch.object(client, "get_channel", return_value=channel),
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
                message.content = message.clean_content = "hello there"
            await client.on_message(message)
        assert len(responder.calls) == 1
        context = responder.calls[0][0][0].content
        assert "SOURCE-CHECKED VOICE CONTEXT" in context
        assert "Tomatoes win again." in context
        assert "RETRIEVED HISTORICAL EVIDENCE" not in context
        channel.send.assert_awaited_once_with("Hot")
        assert archive.learning.status()["messages"] == 0
        assert await client._memory_context(channel, "hello", [], requester_user_id=2) == ""
        archive.learning.forget(now=NOW)
        assert await client._memory_context(channel, "hello", [], requester_user_id=1) == ""
    await client.close()


def test_voice_context_cannot_bypass_requested_year_scope(archive):
    add(
        archive,
        "peer\n  8:00 AM\nGarden update?\nlegacy.target\n  8:01 AM\nTomatoes win.",
        period_hint="synthetic_2020.txt",
    )
    with patch(
        "trubot.voice_memory.STYLE_EXAMPLES", (StyleExample("Garden update?", "Tomatoes win."),)
    ):
        assert voice_context(archive.learning, "garden 2019", guild_id=77) == ""
        assert "Tomatoes win." in voice_context(archive.learning, "garden 2020", guild_id=77)
        with archive._transaction() as db:
            db.execute("DELETE FROM origins WHERE period_hint='synthetic_2020.txt'")
        assert voice_context(archive.learning, "garden 2020", guild_id=77) == ""
        assert "Tomatoes win." in voice_context(archive.learning, "garden", guild_id=77)
