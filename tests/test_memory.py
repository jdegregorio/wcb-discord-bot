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
