import json
from datetime import timedelta

import pytest
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory, years


@pytest.fixture
def store(tmp_path):
    return LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)


def test_topic_retrieval_uses_authenticated_source_and_survives_restart(store):
    store.observe(source(content="Go White Sox!"), now=NOW)
    store.observe(source(1, author_id=43, content="I love the Cubs."), now=NOW)
    memory = ContextMemory(store)
    candidates = memory.candidates("Who is your baseball team?", guild_id=77, now=NOW)
    assert len(candidates) == 1
    rendered = ContextMemory(store).render(candidates)
    assert "Go White Sox!" in rendered
    assert ContextMemory(store).render(candidates, verified_after=NOW + timedelta(seconds=1)) == ""
    assert "Cubs" not in rendered
    assert "verified Andrew" in rendered
    assert not memory.candidates("baseball", guild_id=78, now=NOW)
    assert not memory.candidates("Who are you?", guild_id=77, now=NOW)
    assert not memory.candidates("volcano", guild_id=77, now=NOW)


def test_materialization_honors_edits_deletions_and_withdrawal(store):
    store.observe(source(content="I love the Sox."), now=NOW)
    memory = ContextMemory(store)
    candidates = memory.candidates("baseball", guild_id=77, now=NOW)
    store.invalidate(10, [source().id], deleted=False, now=NOW)
    assert memory.render(candidates) == ""
    store.observe(source(content="I love the Cubs.", authoritative=True), now=NOW)
    assert "Cubs" in memory.render(candidates)
    store.invalidate(10, [source().id], deleted=True, now=NOW)
    assert memory.render(candidates) == ""
    store.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        memory.candidates("baseball", guild_id=77, now=NOW)
    with pytest.raises(LearningUnavailable):
        memory.render(candidates)


def test_slack_context_is_separate_and_ambiguous_quotes_are_excluded(store):
    archive = ArchiveStore.initialize(store)
    archive.import_document(
        b"peer\n  8:00 AM\nI love the Cubs.\n"
        b"legacy.target\n  8:01 AM\nSox forever.\n"
        b"legacy.target\n  8:02 AM\nreplied to a thread:\nCubs forever.",
        channel="general",
        target_alias="legacy.target",
        alias_basis="Synthetic operator audit",
        origin={"kind": "synthetic"},
        now=NOW,
    )
    memory = ContextMemory(store)
    candidates = memory.candidates("baseball", guild_id=77, now=NOW)
    assert len(candidates) == 1
    data = json.loads(memory.render(candidates).split("\n", 1)[1])
    assert data[0]["text"] == "Sox forever."
    assert data[0]["adjacent_context_only"][0]["author"] == "peer (not persona evidence)"
    assert data[0]["source"]["start_line"] > 0
    archive.remove_document(candidates[0].source["document"], now=NOW)
    assert memory.render(candidates) == ""


def test_bounded_deduplicated_sources_and_content_free_repr(store):
    for i in range(8):
        store.observe(source(i, content=f"White Sox {i}"), now=NOW)
    store.observe(source(9, content="White Sox 0"), now=NOW)
    memory = ContextMemory(store)
    candidates = memory.candidates("baseball", guild_id=77, now=NOW)
    assert len(candidates) == 5
    assert len({c.content for c in candidates}) == 5
    assert "White Sox" not in repr(candidates)


def test_year_query_retrieves_export_label_without_inventing_message_dates(store):
    archive = ArchiveStore.initialize(store)
    for year, body in [
        ("2020", "I enjoyed that overtime finish and the improbable comeback."),
        ("2019", "I remember something about 2020, but this is another export."),
    ]:
        archive.import_document(
            ("peer\n  8:00 AM\nThis is my own view.\nlegacy.target\n  8:01 AM\n" + body).encode(),
            channel="general",
            target_alias="legacy.target",
            alias_basis="Synthetic operator audit",
            origin={"kind": "synthetic", "year_label": year},
            period_hint=f"general_{year}.txt",
            now=NOW,
        )
    memory = ContextMemory(store)
    candidates = memory.candidates("what was something you said in 2020?", guild_id=77, now=NOW)
    assert len(candidates) == 1
    data = json.loads(memory.render(candidates).split("\n")[-1])[0]
    assert "overtime" in data["text"]
    assert data["source"]["date"].startswith("unknown")
    assert data["source"]["archive_period_hints"] == ["general_2020.txt"]
    assert data["source"]["period_is_message_date"] is False
    assert data["adjacent_context_only"][0]["author"] == "peer (not persona evidence)"
    assert not memory.candidates("What did you say in 2018?", guild_id=77, now=NOW)
    with archive._transaction() as db:
        db.execute("DELETE FROM origins WHERE period_hint='general_2020.txt'")
    assert not memory.render(candidates)


def test_year_query_native_timestamp_and_numeric_boundaries(store):
    store.observe(source(content="I like baseball."), now=NOW)
    memory = ContextMemory(store)
    assert len(memory.candidates(f"What did you say in {NOW.year}?", guild_id=77, now=NOW)) == 1
    assert not memory.candidates("What did you say in 2020?", guild_id=77, now=NOW)
    assert years("general_2020-1.txt 20209 12020") == {"2020"}


@pytest.mark.parametrize(
    ("focused_request", "expected"),
    [
        ("Who is your baseball team?", "content"),
        ("What was something you said in 2020?", "content"),
        ("Quote one thing you said in 2020", "content"),
        ("Tell me about the old league", "content"),
        ("When did you say that?", "timing"),
        ("What day was that?", "timing"),
        ("Do you know the date of that baseball message?", "timing"),
        ("What date did you say that?", "timing"),
        ("Which message date was that?", "timing"),
        ("How long have you liked baseball?", "timing"),
        ("Was that before or after the change?", "timing"),
        ("Are you sure that was in 2020?", "timing"),
        ("Did you actually say that in 2020?", "timing"),
        ("What is the source for that?", "evidence"),
        ("Can you show evidence?", "evidence"),
        ("Quote the archive and give the exact date", "evidence"),
    ],
)
def test_focused_recall_presentation_distinguishes_content_timing_and_evidence(
    focused_request, expected
):
    from trubot.memory import recall_presentation

    assert recall_presentation(focused_request).value == expected


def test_presentation_preserves_identical_grounding_and_unknown_dates(store):
    archive = ArchiveStore.initialize(store)
    archive.import_document(
        b"legacy.target\n  8:01 AM\nI enjoyed the overtime finish.",
        channel="general",
        target_alias="legacy.target",
        alias_basis="Synthetic operator audit",
        origin={"kind": "synthetic"},
        period_hint="general_2020.txt",
        now=NOW,
    )
    memory = ContextMemory(store)
    candidates = memory.candidates("What did you say in 2020?", guild_id=77, now=NOW)
    requests = ["What did you say in 2020?", "When did you say that?", "Show the source"]
    rendered = [memory.render(candidates, request=request) for request in requests]
    data = [json.loads(item.split("\n", 1)[1]) for item in rendered]
    assert data[0] == data[1] == data[2]
    assert data[0][0]["source"]["period_is_message_date"] is False
    assert data[0][0]["source"]["date"].startswith("unknown")
    assert "ordinary recall" in rendered[0]
    assert "asks about timing" in rendered[1]
    assert "asks for evidence" in rendered[2]
    archive.remove_document(candidates[0].source["document"], now=NOW)
    assert not memory.render(candidates, request=requests[2])


def test_bot_quotation_is_only_a_lookup_key_for_current_attributed_sources(store):
    archive = ArchiveStore.initialize(store)
    archive.import_document(
        b"peer\n  8:00 AM\nThe moon league always wins.\n"
        b"legacy.target\n  8:01 AM\nDoes the waiver tool tell us when we are outbid?",
        channel="general",
        target_alias="legacy.target",
        alias_basis="Synthetic operator audit",
        origin={"kind": "synthetic"},
        period_hint="general_2020.txt",
        now=NOW,
    )
    memory = ContextMemory(store)
    quote = "Does the waiver tool tell us when we are outbid?"
    candidates = memory.candidates(
        "What source supports that 2020 memory?", guild_id=77, now=NOW, quotation=quote
    )
    assert len(candidates) == 1
    rendered = memory.render(candidates, request="Show that source", quotation=quote)
    assert quote in rendered
    assert "asks for evidence" in rendered
    assert not memory.candidates("source", guild_id=78, now=NOW, quotation=quote)
    assert not memory.candidates("source", guild_id=77, now=NOW, quotation="An invented bot quote")
    assert not memory.candidates(
        "source", guild_id=77, now=NOW, quotation="The moon league always wins."
    )
    assert not memory.candidates("source in 2019", guild_id=77, now=NOW, quotation=quote)
    with archive._transaction() as db:
        db.execute(
            "UPDATE messages SET content='This corrected source says something different.' "
            "WHERE target=1"
        )
    assert not memory.render(candidates, quotation=quote)
    store.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        memory.candidates("source", guild_id=77, now=NOW, quotation=quote)


def test_native_quotation_requires_current_fresh_source_after_lookup(store):
    text = "That waiver change looks good to me."
    store.observe(source(content=text), now=NOW)
    memory = ContextMemory(store)
    candidates = memory.candidates("source", guild_id=77, now=NOW, quotation=text)
    assert len(candidates) == 1
    assert memory.render(candidates, quotation=text)
    assert not memory.render(candidates, quotation=text, verified_after=NOW + timedelta(seconds=1))
    store.invalidate(10, [source().id], deleted=False, now=NOW)
    store.observe(source(content="I changed my view.", authoritative=True), now=NOW)
    assert not memory.render(candidates, quotation=text)


def test_recent_conversation_uses_dated_native_sources_in_chronological_order(store):
    # Older, verbose lexical hits must not hide a short recent human response.
    store.observe(source(0, content="Yep.", created_at=NOW - timedelta(minutes=2)), now=NOW)
    store.observe(source(1, content="Nope.", created_at=NOW - timedelta(days=1)), now=NOW)
    store.observe(
        source(2, content="Old league example", created_at=NOW - timedelta(days=20)), now=NOW
    )
    archive = ArchiveStore.initialize(store)
    archive.import_document(
        b"legacy.target\n  8:00 AM\nI talked about the league recently. A recent example.",
        channel="general",
        target_alias="legacy.target",
        alias_basis="Synthetic operator audit",
        origin={"kind": "synthetic"},
        now=NOW,
    )
    memory = ContextMemory(store)
    query = (
        "What have you been saying in the league lately? "
        "Give me one recent example and what was going on around it."
    )
    candidates = memory.candidates(query, guild_id=77, now=NOW)
    assert [c.content for c in candidates] == ["Yep.", "Nope."]
    assert all(c.source["kind"] == "discord" for c in candidates)
    assert not memory.candidates(query, guild_id=78, now=NOW)
    assert not memory.candidates(query, guild_id=77, now=NOW + timedelta(days=15))
    assert (
        len(memory.candidates("What did you say about baseball recently?", guild_id=77, now=NOW))
        == 0
    )
    # A year request continues using historical scope rather than recent native scope.
    assert (
        len(memory.candidates("What was a recent conversation in 2020?", guild_id=77, now=NOW)) == 0
    )


def test_native_episode_binding_drops_context_after_source_edit_or_deletion(store):
    from trubot.native_context import NativeEpisode

    store.observe(source(content="Yep."), now=NOW)
    memory = ContextMemory(store)
    candidates = memory.candidates("What did you say lately?", guild_id=77, now=NOW)
    episode = NativeEpisode("Yep.", None, ({"author": "peer", "text": "Keep the current rule?"},))
    rendered = memory.render(candidates, native_episodes={source().id: episode})
    assert "Keep the current rule?" in rendered
    assert "Keep the current rule?" not in repr(episode)
    store.observe(source(content="Nope.", authoritative=True), now=NOW)
    rendered = memory.render(candidates, native_episodes={source().id: episode})
    assert "Nope." in rendered
    assert "Keep the current rule?" not in rendered
    store.invalidate(10, [source().id], deleted=True, now=NOW)
    assert memory.render(candidates, native_episodes={source().id: episode}) == ""


@pytest.mark.parametrize(
    ("query", "hours"),
    [
        ("Quote something you said in the past week.", 168),
        ("What did you say in the last two days?", 48),
        ("Quote a message from the past hour.", 1),
    ],
)
def test_rolling_recall_uses_timestamp_boundaries_and_never_undated_fallback(store, query, hours):
    from trubot.memory import MemoryCandidate

    boundary = NOW - timedelta(hours=hours)
    store.observe(source(0, content="In range.", created_at=boundary), now=NOW)
    store.observe(
        source(1, content="Outside.", created_at=boundary - timedelta(microseconds=1)), now=NOW
    )
    archive = ArchiveStore.initialize(store)
    imported = archive.import_document(
        b"legacy.target\n  8:01 AM\nI said something in the past week.",
        channel="synthetic",
        target_alias="legacy.target",
        alias_basis="Synthetic operator audit",
        origin={"kind": "synthetic"},
        now=NOW,
    )
    memory = ContextMemory(store)
    selected = memory.candidates(query, guild_id=77, now=NOW)
    assert [c.content for c in selected] == ["In range."]
    rendered = memory.render(selected, request=query, now=NOW)
    assert "In range." in rendered and "Outside." not in rendered
    # Rendering rechecks the requested interval independently of candidate selection.
    old = memory.candidates("Outside", guild_id=77, now=NOW)
    assert "Outside." not in memory.render(old, request=query, now=NOW)
    assert "no verified recent human source" in memory.render(
        [MemoryCandidate({"kind": "slack", "document": imported}, "Invented", 1)],
        request=query,
        now=NOW,
    )
    store.invalidate(10, [source().id], deleted=True, now=NOW)
    assert memory.candidates(query, guild_id=77, now=NOW) == []
    assert "no verified recent human source" in memory.render(selected, request=query, now=NOW)


def test_rolling_recall_intersects_retention_and_rejects_unknown_or_zero_amounts(store):
    store.observe(source(content="Current", created_at=NOW), now=NOW)
    store.observe(source(1, content="Earlier", created_at=NOW - timedelta(days=5)), now=NOW)
    constrained = LearningStore(store.path, retention_days=2)
    memory = ContextMemory(constrained)
    query = "Quote a message from the past thirty days."
    selected = memory.candidates(query, guild_id=77, now=NOW)
    assert [c.content for c in selected] == ["Current"]
    assert memory.render(selected, request=query, now=NOW + timedelta(days=3)).startswith(
        "RECENT CONVERSATION RECALL"
    )
    for query in (
        "Quote messages from the last 0 hours",
        "Quote messages from the past few days",
    ):
        assert memory.candidates(query, guild_id=77, now=NOW) == []
        assert "no verified recent human source" in memory.render(selected, request=query, now=NOW)
    store.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        memory.candidates("Quote messages from the past week", guild_id=77, now=NOW)
