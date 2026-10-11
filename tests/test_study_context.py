"""Invented exchanges exercise admitted evidence, attribution and request headroom."""

import hashlib
import json
from datetime import timedelta
from types import SimpleNamespace

import pytest
from test_distillation import proposal, worker
from test_learning import AUDIT, NOW

from trubot.archives import ArchiveStore
from trubot.distillation import _EXTRACT, StudyStore, extraction_schema, validate_proposal
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def export(stores, texts, *, number=0):
    _, archive, graph = stores
    raw = "\n".join(
        f"{speaker}\n  8:{i:02} AM\n{text}" for i, (speaker, text) in enumerate(texts)
    ).encode()
    archive.import_document(
        raw,
        channel="invented",
        target_alias="fixture.target",
        alias_basis="Invented contextual study fixture",
        origin={"kind": "synthetic", "episode": number},
        now=NOW,
    )
    graph.populate(now=NOW)
    with archive._transaction() as db:
        row = db.execute(
            "SELECT document,ordinal FROM messages WHERE target=1 AND document=?",
            (hashlib.sha256(raw).hexdigest(),),
        ).fetchone()
    return {"kind": "slack", "document": row[0], "ordinal": row[1]}


def select(stores, ref):
    return StudyStore(stores[2]).prepare(now=NOW, channel_ids=frozenset({10}), anchor_ref=ref)


def test_distant_setup_and_long_qualification_and_reaction_reach_both_passes(stores):
    setup = "Let's invent ridiculous roster jobs, strictly playful brainstorming."
    qualification = (
        "We talked about logistics first. " * 5 + "This is a joke, not a real job offer."
    )
    reaction = "That is funny because the pastry chef cannot play football."
    ref = export(
        stores,
        [
            ("peer-a", setup),
            ("peer-b", qualification),
            ("fixture.target", "Draft a pastry chef for the roster dessert points."),
            ("peer-a", reaction),
            ("peer-b", "We are still kidding, no actual roster change."),
        ],
    )
    study = select(stores, ref)
    rows = study.passages[0]["adjacent_context"]
    assert [r["offset"] for r in rows] == [-2, -1, 1, 2]
    assert rows[1]["text"] == qualification
    assert not any(r["text_truncated"] for r in rows)
    assert study.passages[0]["context_omitted"] == 0
    assert rows[0]["speaker_key"] == rows[2]["speaker_key"]
    assert "peer-a" not in json.dumps(study.passages)
    assert all(r["author_role"] == "other_speaker" for r in rows)


def test_oversized_context_is_a_gap_not_a_misleading_fragment(stores):
    ref = export(
        stores,
        [
            ("peer", "Pretend I said: " + "x" * 700 + " That was only a quotation."),
            ("fixture.target", "We can draft a pastry chef for the roster dessert points."),
            ("peer", "Image from iOS"),
        ],
    )
    passage = select(stores, ref).passages[0]
    assert passage["context_omitted"] == 1
    assert [r["offset"] for r in passage["adjacent_context"]] == [1]
    assert "visual_context_missing" in passage["adjacent_context"][0]["flags"]


@pytest.mark.parametrize(
    "body", ["roster " * 140, "roster " + "🤖" * 245], ids=["ascii", "unicode"]
)
def test_full_packet_fits_exact_provider_envelope_with_review_headroom(stores, body):
    for i in range(6):
        ref = export(
            stores,
            [
                ("peer", "roster setup " * 35),
                ("fixture.target", body + str(i)),
                ("peer", "roster response " * 30),
            ],
            number=i,
        )
    study = select(stores, ref)
    size = len(
        json.dumps(
            [
                _EXTRACT,
                json.dumps({"sources": study.passages}, ensure_ascii=False),
                extraction_schema(study),
            ],
            ensure_ascii=False,
        ).encode()
    )
    assert size <= 14_000
    assert 2 <= len(study.passages) <= 6
    assert [p["source_index"] for p in study.passages] == list(range(len(study.snapshots)))
    assert len(study.passages) == len(study.snapshots)
    assert study.snapshots[0]["ref"]["document"] == ref["document"]
    assert any(p["context_omitted"] for p in study.passages)
    assert all(not r["text_truncated"] for p in study.passages for r in p["adjacent_context"])


async def test_full_context_cannot_supply_authored_support_and_is_identical_at_review(stores):
    for i in range(2):
        ref = export(
            stores,
            [
                ("peer", "Let's invent absurd roster jobs, this is a playful invitation."),
                ("peer", "We have already excluded any real roster rule change."),
                ("fixture.target", f"Draft pastry chef {i} for the roster dessert points."),
                ("peer", "That is funny, we are still only kidding about the roster."),
            ],
            number=i,
        )
    distiller, client, responder, _ = worker(stores)
    packets = []

    async def generate(**kwargs):
        packets.append(kwargs["payload"]["sources"])
        if kwargs["name"] == "memory_extract":
            study = SimpleNamespace(passages=packets[0])
            return proposal(study, kind="humor")
        assert packets[1] == packets[0]
        return {"accepted": True, "basis": "Invented separate episodes only.", "contradicts": []}

    responder.study_json.side_effect = generate
    await distiller.cycle(client, anchor_ref=ref)
    assert len(packets) == 2
    assert len(packets[0][0]["adjacent_context"]) == 3
    assert stores[2].lookup("dessert", guild_id=77, now=NOW)
    study = StudyStore(stores[2]).prepare(now=NOW + timedelta(days=31), channel_ids=frozenset({10}))
    bad = proposal(study)
    bad["observations"][0]["supports"][0]["quote"] = packets[0][0]["adjacent_context"][0]["text"]
    with pytest.raises(LearningUnavailable, match="Exact attributed quote"):
        validate_proposal(bad, study)
    stores[1].remove_document(ref["document"], now=NOW)
    assert not stores[2].lookup("dessert", guild_id=77, now=NOW)
