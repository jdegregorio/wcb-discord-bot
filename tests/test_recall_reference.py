from unittest.mock import patch

import pytest
from test_discord_client import fake_channel, make_client
from test_learning import AUDIT, NOW

from trubot.archives import ArchiveStore
from trubot.conversation import ConversationMessage
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore
from trubot.memory import ContextMemory, RecallPresentation, recall_presentation

QUOTE_A = "The waiver rule should give everybody a fair chance."
QUOTE_B = "That draft clock needs a little more time."
UNKNOWN = "I purchased an imaginary lunar football stadium."


@pytest.fixture
def context(tmp_path):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    archive = ArchiveStore.initialize(store)
    archive.import_document(
        (
            "legacy.target\n  8:00 AM\n"
            + QUOTE_A
            + "\npeer\n  8:30 AM\nA separate draft discussion.\nlegacy.target\n  9:00 AM\n"
            + QUOTE_B
        ).encode(),
        channel="general",
        target_alias="legacy.target",
        alias_basis="Synthetic audit",
        origin={"kind": "synthetic"},
        period_hint="general_2020.txt",
        now=NOW,
    )
    client, _, _, _ = make_client(clock=lambda: NOW)
    learning = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learning.verified = True
    client._learning, client._memory = learning, ContextMemory(store)
    return client, archive


@pytest.mark.parametrize(
    "question",
    [
        "What exact day?",
        "Which specific month was it?",
        "What calendar year was that?",
        "What precise day did you say that?",
    ],
)
def test_qualified_timing_intent(question):
    assert recall_presentation(question) is RecallPresentation.TIMING


@pytest.mark.parametrize(
    "question",
    [
        "Quote one thing you said in 2020.",
        "That draft day was funny.",
        "What do you think of that?",
    ],
)
def test_ordinary_recall_remains_content(question):
    assert recall_presentation(question) is RecallPresentation.CONTENT


@pytest.mark.parametrize(
    "question",
    [
        f"What day did you say that quote “{QUOTE_B}”?",
        f'What source supports "{QUOTE_B}"?',
    ],
)
async def test_focused_quote_wins_over_older_bot_quote(context, question):
    client, _ = context
    try:
        result = await client._memory_context(
            fake_channel(),
            "Tim: " + question,
            [ConversationMessage("assistant", f"“{QUOTE_A}”")],
        )
        assert QUOTE_B in result
        assert QUOTE_A not in result
    finally:
        await client.close()


@pytest.mark.parametrize(
    "question",
    [
        f"What day did you say that quote “{UNKNOWN}”?",
        f"What source supports “{QUOTE_A}” and “{QUOTE_B}”?",
        'What date did you say that "short" quote?',
    ],
)
async def test_unknown_or_ambiguous_focus_never_falls_back_to_old_quote(context, question):
    client, _ = context
    try:
        result = await client._memory_context(
            fake_channel(),
            "Tim: " + question,
            [ConversationMessage("assistant", f"“{QUOTE_A}”")],
        )
        assert QUOTE_A not in result
        assert QUOTE_B not in result
    finally:
        await client.close()


@pytest.mark.parametrize(
    "boundary",
    [
        [
            ConversationMessage("user", "Tim: Who is your baseball team?"),
            ConversationMessage("assistant", "The invented Moon Otters."),
        ],
        [ConversationMessage("user", "Tim: Now talk about baseball.")],
    ],
)
async def test_new_subject_stops_implicit_quote_lookback(context, boundary):
    client, _ = context
    try:
        history = [ConversationMessage("assistant", f"“{QUOTE_A}”"), *boundary]
        result = await client._memory_context(
            fake_channel(), "Tim: When did you say that?", history
        )
        assert QUOTE_A not in result
    finally:
        await client.close()


async def test_timing_evidence_chain_retains_quote_and_unknown_archive_date(context):
    client, _ = context
    try:
        history = [
            ConversationMessage("assistant", f"“{QUOTE_A}”"),
            ConversationMessage("user", "Tim: What exact day?"),
            ConversationMessage("assistant", "I don't know the day."),
        ]
        result = await client._memory_context(
            fake_channel(), "Tim: What source supports that?", history
        )
        assert QUOTE_A in result
        assert "unknown; display clock" in result
        assert "asks for evidence" in result
    finally:
        await client.close()


async def test_explicit_quote_requires_current_source_and_skips_unrelated_voice(context):
    client, archive = context
    question = f"Tim: What day did you say “{QUOTE_A}”?"
    try:
        with patch("trubot.discord_client.voice_context", return_value="UNRELATED VOICE") as voice:
            result = await client._memory_context(fake_channel(), question, [])
            assert QUOTE_A in result
            assert "UNRELATED VOICE" not in result
            voice.assert_not_called()
        with archive._transaction() as db:
            db.execute(
                "UPDATE messages SET content=? WHERE content=?",
                ("Corrected different text.", QUOTE_A),
            )
        result = await client._memory_context(fake_channel(), question, [])
        assert QUOTE_A not in result
        client._learning.store.forget(now=NOW)
        result = await client._memory_context(fake_channel(), question, [])
        assert QUOTE_A not in result
    finally:
        await client.close()


@pytest.mark.parametrize(
    ("question", "history", "expected"),
    [
        ("What exact day?", [ConversationMessage("assistant", f"“{QUOTE_A}”")], QUOTE_A),
        ("When did you say that?", [ConversationMessage("user", f"Peer: “{QUOTE_A}”")], ""),
        ("When did you say that?", [ConversationMessage("assistant", "I do not know.")], ""),
        (
            "When did you say that?",
            [
                ConversationMessage("assistant", f"“{QUOTE_A}”"),
                ConversationMessage("assistant", "Another reply."),
            ],
            "",
        ),
        (
            "When did you say that?",
            [
                ConversationMessage("assistant", f"“{QUOTE_A}”"),
                ConversationMessage("user", "Tim: What source supports baseball?"),
                ConversationMessage("assistant", "Not sure."),
            ],
            "",
        ),
        (f'When did you say that "{QUOTE_B}"?', [], QUOTE_B),
        (f'When did you say “{QUOTE_B}” and "{QUOTE_B}"?', [], QUOTE_B),
        (
            f"When did you say that “{QUOTE_B}?",
            [ConversationMessage("assistant", f"“{QUOTE_A}”")],
            "",
        ),
        (
            "What exact day?",
            [
                ConversationMessage("assistant", f"“{QUOTE_A}”"),
                ConversationMessage("user", "Tim: What exact day?"),
            ],
            QUOTE_A,
        ),
        ("When did you say that?", [], ""),
        ("When did you talk about baseball?", [], None),
        (
            "When did you say that about baseball?",
            [ConversationMessage("assistant", f"“{QUOTE_A}”")],
            None,
        ),
        ("When did you talk about that?", [], ""),
        ("What day did you discuss baseball?", [], None),
        ("Who is your team?", [ConversationMessage("assistant", f"“{QUOTE_A}”")], None),
        (
            "What source supports that?",
            [
                ConversationMessage("assistant", f"“{QUOTE_A}”"),
                ConversationMessage("user", f'Tim: When did you say "{UNKNOWN}"?'),
                ConversationMessage("assistant", "I do not know."),
            ],
            UNKNOWN,
        ),
    ],
)
def test_referent_boundaries(question, history, expected):
    from trubot.recall_reference import recall_quotation

    assert recall_quotation(question, history) == expected


def test_lookback_bound_does_not_resurrect_old_quotes():
    from trubot.recall_reference import recall_quotation

    history = [ConversationMessage("assistant", f"“{QUOTE_A}”")]
    for _ in range(4):
        history += [
            ConversationMessage("user", "Tim: What exact day?"),
            ConversationMessage("assistant", "I do not know."),
        ]
    assert recall_quotation("What source supports that?", history) == ""


@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_focused_quote_reaches_production_handlers(context, mode):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    from test_discord_client import fake_message, message_for_history

    client, _ = context
    channel = fake_channel()
    rows = [
        message_for_history("Quote a waiver message.", author_id=1),
        message_for_history(f"“{QUOTE_A}”", author_id=999, bot=True),
    ]

    async def history(**_kwargs):
        for row in reversed(rows):
            yield row

    channel.history = history
    message = fake_message(channel)
    message.id = 500
    message.content = message.clean_content = f"What exact day did you say that “{QUOTE_B}”?"
    if mode == "direct":
        message.content = message.clean_content = "🤖 " + message.content
    client._attention.activate(channel.id, NOW)
    try:
        if mode == "reaction":
            channel.fetch_message = AsyncMock(return_value=message)
            with patch.object(client, "get_channel", return_value=channel):
                await client.on_raw_reaction_add(
                    SimpleNamespace(
                        channel_id=channel.id,
                        user_id=1,
                        message_id=message.id,
                        emoji=SimpleNamespace(name="🍆"),
                        member=SimpleNamespace(bot=False),
                    )
                )
        else:
            await client.on_message(message)
        call = client._responder.calls[0]
        memory = next(m.content for m in call[0] if m.content.startswith("RETRIEVED"))
        assert QUOTE_B in memory and QUOTE_A not in memory
        assert "asks about timing" in memory and "unknown; display clock" in memory
        channel.send.assert_awaited_once()
        assert client._learning.store.status()["messages"] == 0
    finally:
        await client.close()
