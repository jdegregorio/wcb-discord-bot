"""Detached invented native remarks cannot automatically establish character patterns."""

import json
from datetime import timedelta
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from test_abstract_distillation import pattern, pattern_worker
from test_graph import observation
from test_learning import AUDIT, BASE, NOW, source

from trubot.archives import ArchiveStore
from trubot.distillation import extraction_schema, validate_proposal
from trubot.episode_memory import PATTERN_KINDS
from trubot.graph import GraphStore, _json
from trubot.learning import LearningStore, LearningUnavailable


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def packet_study(kinds=("discord", "discord", "discord")):
    texts = (
        "Give the baker a roster spot and count every croissant.",
        "We should draft a pastry chef for roster dessert points.",
        "Seriously, dessert jokes aside, I want a fair roster vote.",
    )
    return SimpleNamespace(
        passages=[{"author_text": t, "author_text_truncated": False} for t in texts],
        snapshots=[
            {
                "ref": {"kind": kind, "message_id": BASE + i, "channel_id": 10}
                if kind == "discord"
                else {"kind": "slack", "document": str(i) * 64, "ordinal": 0},
                "source_time": (NOW - timedelta(days=i + 1)).isoformat(),
                "content_hash": str(i),
            }
            for i, kind in enumerate(kinds)
        ],
    )


@pytest.mark.parametrize("kind", PATTERN_KINDS)
@pytest.mark.parametrize("native_index", [0, 1, 2])
def test_native_support_or_contrary_source_is_excluded_at_both_boundaries(kind, native_index):
    kinds = ["slack"] * 3
    kinds[native_index] = "discord"
    study = packet_study(kinds)
    packet = pattern(study, kind)
    assert not Draft202012Validator(extraction_schema(study)).is_valid(packet)
    with pytest.raises(LearningUnavailable, match="Native pattern context"):
        validate_proposal(packet, study)


def test_unused_native_source_does_not_suppress_contextual_archive_pattern():
    study = packet_study(("slack", "slack", "discord"))
    packet = pattern(study)
    packet["observations"][0]["counterexamples"] = []
    Draft202012Validator(extraction_schema(study)).validate(packet)
    assert validate_proposal(packet, study)


def test_native_literals_and_abstention_keep_existing_contract():
    study = packet_study()
    study.passages[0]["author_text"] = "I prefer caramel after dinner."
    packet = pattern(study)
    item = packet["observations"][0]
    item["kind"] = "preference"
    del item["limitations"], item["counterexamples"]
    item["supports"] = [{"source": i, "quote": study.passages[i]["author_text"]} for i in (0, 1)]
    validator = Draft202012Validator(extraction_schema(study))
    validator.validate(packet)
    assert validate_proposal(packet, study)
    item["support_basis"] = "explicit_self_report"
    item["supports"] = item["supports"][:1]
    validator.validate(packet)
    assert validate_proposal(packet, study)
    validator.validate({"observations": []})


def seed_native(stores):
    learning, _, graph = stores
    study = packet_study()
    for i, p in enumerate(study.passages):
        learning.observe(
            source(i, content=p["author_text"], created_at=NOW - timedelta(days=i + 1)), now=NOW
        )
    graph.populate(now=NOW)
    return study


async def test_full_learner_rejects_native_pattern_before_review_and_persists_pacing(stores):
    seed_native(stores)
    distiller, client, responder, _ = pattern_worker(stores)

    async def generate(**kwargs):
        if kwargs["name"] == "memory_extract":
            return pattern(SimpleNamespace(passages=kwargs["payload"]["sources"]))
        return {"accepted": True, "basis": "Invented positive reviewer.", "contradicts": []}

    responder.study_json.side_effect = generate
    assert await distiller.cycle(client) == "rejected"
    assert responder.study_json.await_count == 1
    assert not stores[2].lookup("roster brainstorming", guild_id=77, now=NOW)
    await distiller.cycle(client)
    assert responder.study_json.await_count == 1


@pytest.mark.parametrize("kind", PATTERN_KINDS)
def test_storage_rejects_automated_native_pattern_but_operator_review_stays_available(stores, kind):
    seed_native(stores)
    learning, _, graph = stores
    refs = [{"kind": "discord", "message_id": BASE + i} for i in range(3)]
    item = observation(
        refs[0],
        kind=kind,
        supports=refs[:2],
        abstraction={
            "conditions": "Invented invited roster play.",
            "limitations": "Answer serious questions sincerely.",
            "counterexamples": refs[2:],
        },
        status="tentative",
        support_basis="corroborated",
        expires_at=(NOW + timedelta(days=30)).isoformat(),
    )
    with (
        pytest.raises(LearningUnavailable, match="Native pattern context"),
        graph._transaction() as (db, sources),
    ):
        graph._write_observation(db, sources, item, now=NOW, automated=True)
    graph.import_observation(item, now=NOW)
    assert GraphStore(learning).lookup("sweet tooth", guild_id=77, now=NOW)


@pytest.mark.parametrize("kind", PATTERN_KINDS)
def test_restored_legacy_automatic_pattern_is_blocked_and_swept_with_backups(stores, kind):
    seed_native(stores)
    learning, _, graph = stores
    refs = [{"kind": "discord", "message_id": BASE + i} for i in range(3)]
    item = observation(
        refs[0],
        kind=kind,
        supports=refs[:2],
        abstraction={
            "conditions": "Invented invited roster play.",
            "limitations": "Answer serious questions sincerely.",
            "counterexamples": refs[2:],
        },
    )
    graph.import_observation(item, now=NOW)
    with graph._transaction() as (db, _):
        row = db.execute("SELECT id,data FROM nodes WHERE kind=?", (kind,)).fetchone()
        data = json.loads(row["data"])
        data["review_kind"] = "automated-two-pass"
        db.execute("UPDATE nodes SET data=? WHERE id=?", (_json(data), row["id"]))
        key = row["id"]
    backups = graph.path.parent / "backups"
    backups.mkdir(mode=0o700)
    old = backups / "memory-graph-synthetic.sqlite3"
    old.write_bytes(graph.path.read_bytes())
    old.chmod(0o600)
    assert not GraphStore(learning).lookup("sweet tooth", guild_id=77, now=NOW)
    assert not graph.describe([key], now=NOW, verified_after=None)
    assert graph.sweep(now=NOW) >= 1
    assert not old.exists()


@pytest.mark.parametrize("kind", PATTERN_KINDS)
def test_model_context_labels_cannot_authorize_native_patterns(kind):
    study = packet_study()
    for passage in study.passages:
        passage["context_scope"] = "export_adjacency_only"
        passage["adjacent_context"] = [{"author_role": "other_speaker", "text": "Invented setup."}]
    assert not Draft202012Validator(extraction_schema(study)).is_valid(pattern(study, kind))
    with pytest.raises(LearningUnavailable, match="Native pattern context"):
        validate_proposal(pattern(study, kind), study)
