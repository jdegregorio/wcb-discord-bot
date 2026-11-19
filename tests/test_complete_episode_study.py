"""Complete trusted study inputs, using invented evidence and no provider calls."""

from datetime import timedelta

import pytest
from test_distillation import worker
from test_learning import AUDIT, NOW, source
from test_study_context import export

from trubot.archives import ArchiveStore
from trubot.distillation import StudyStore
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.openai_responder import StudyContextExceeded


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def authored(stores, text, number=0):
    return export(stores, [("fixture.target", text)], number=number)


@pytest.mark.parametrize("kind", ["slack", "discord"])
@pytest.mark.parametrize(
    "text", ["x" * 1001, "x" * 4000, "🎂" * 1000], ids=["1001", "4000", "unicode-4000"]
)
def test_trusted_study_keeps_full_authored_block_with_exact_byte_bound(stores, text, kind):
    if kind == "slack":
        ref = authored(stores, text)
    else:
        stores[0].observe(source(content=text), now=NOW)
        stores[2].populate(now=NOW)
        ref = {"kind": "discord", "message_id": source().id}
    study = StudyStore(stores[2]).prepare(now=NOW, channel_ids=frozenset({10}), episode_refs=[ref])
    assert study.passages[0]["author_text"] == text
    assert study.passages[0]["author_text_truncated"] is False


@pytest.mark.parametrize("text", ["x" * 4001, "🎂" * 1001], ids=["ascii", "unicode"])
def test_oversized_exact_source_fails_without_lease_or_partial_text(stores, text):
    ref = authored(stores, text)
    with pytest.raises(LearningUnavailable, match="text exceeds"):
        StudyStore(stores[2]).prepare(now=NOW, channel_ids=frozenset({10}), episode_refs=[ref])
    with stores[2]._transaction() as (db, _):
        assert (
            db.execute("SELECT 1 FROM checkpoints WHERE stream='distillation'").fetchone() is None
        )


@pytest.mark.parametrize("selector", ["automatic", "anchor"])
def test_automatic_sampling_and_single_anchor_keep_existing_bound(stores, selector):
    text = "x" * 1100 + " A final qualification must not be invented."
    ref = authored(stores, text)
    kwargs = {"anchor_ref": ref} if selector == "anchor" else {}
    study = StudyStore(stores[2]).prepare(now=NOW, channel_ids=frozenset({10}), **kwargs)
    assert study.passages[0]["author_text"] == text[:1000]
    assert study.passages[0]["author_text_truncated"] is True


def test_complete_set_exceeding_total_request_bound_is_never_trimmed(stores):
    refs = [authored(stores, str(i) + "x" * 3999, i) for i in range(3)]
    with pytest.raises(StudyContextExceeded):
        StudyStore(stores[2]).prepare(now=NOW, channel_ids=frozenset({10}), episode_refs=refs)
    with stores[2]._transaction() as (db, _):
        assert (
            db.execute("SELECT 1 FROM checkpoints WHERE stream='distillation'").fetchone() is None
        )


async def test_both_passes_keep_late_qualification_and_reviewer_can_reject(stores):
    quote = "Draft a pastry chef for fictional dessert points."
    qualification = "This is playful brainstorming, never a real roster preference."
    quotes = [quote + str(i) for i in range(2)]
    texts = [q + " Invented setup." * 70 + " " + qualification for q in quotes]
    refs = [authored(stores, text, i) for i, text in enumerate(texts)]
    distiller, client, responder, _ = worker(stores)
    packets = []

    async def generate(**kwargs):
        packets.append(kwargs["payload"]["sources"])
        if kwargs["name"] == "memory_review":
            return {
                "accepted": False,
                "basis": "A joke cannot establish a real preference.",
                "contradicts": [],
            }
        return {
            "observations": [
                {
                    "kind": "preference",
                    "support_basis": "corroborated",
                    "summary": "Prefers adding a pastry chef to the roster.",
                    "conditions": "Roster decisions.",
                    "supports": [{"source": i, "quote": q} for i, q in enumerate(quotes)],
                    "aliases": ["pastry chef", "dessert points"],
                }
            ]
        }

    responder.study_json.side_effect = generate
    assert await distiller.cycle(client, episode_refs=refs) == "rejected"
    assert len(packets) == 2 and packets[0] == packets[1]
    assert [p["author_text"] for p in packets[0]] == texts
    assert all(qualification in p["author_text"] for p in packets[0])
    assert not stores[2].lookup("pastry chef", guild_id=77, now=NOW)
    assert (
        StudyStore(stores[2]).prepare(
            now=NOW + timedelta(hours=1), channel_ids=frozenset({10}), episode_refs=refs
        )
        is None
    )


async def test_long_exact_source_change_still_prevents_commit(stores):
    ref = authored(stores, "x" * 1100 + " Original final qualification.")
    other = authored(stores, "Another invented independent source.")
    distiller, client, responder, _ = worker(stores)

    async def changed(**kwargs):
        with stores[1]._transaction() as db:
            db.execute(
                "UPDATE messages SET content='Changed source' WHERE document=?", (ref["document"],)
            )
        return {"observations": []}

    responder.study_json.side_effect = changed
    assert await distiller.cycle(client, episode_refs=[ref, other]) is None
    assert responder.study_json.await_count == 1
    assert stores[2].status()["studies"].get("accepted", 0) == 0
