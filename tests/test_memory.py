import json
from datetime import timedelta

import pytest
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory


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
