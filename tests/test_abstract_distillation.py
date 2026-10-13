"""Synthetic conditional patterns, never learned claims about a real participant."""

import copy
import json
from datetime import timedelta
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from test_distillation import worker
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.distillation import StudyStore, extraction_schema, validate_proposal
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def seed(stores, *, native=False, texts=None):
    learning, _, graph = stores
    texts = texts or [
        "Give the baker a roster spot and count every croissant.",
        "We should draft a pastry chef for roster dessert points.",
        "Seriously, dessert jokes aside, I want a fair roster vote.",
    ]
    refs = []
    for i, text in enumerate(texts):
        if native:
            learning.observe(
                source(i, content=text, created_at=NOW - timedelta(days=i + 1)), now=NOW
            )
            refs.append({"kind": "discord", "message_id": source(i).id})
        else:
            from test_study_context import export

            refs.append(
                export(
                    stores,
                    [
                        ("peer", "Invented episode setup " + str(i)),
                        ("fixture.target", text),
                        ("peer", "Invented distinct episode reaction " + str(i)),
                    ],
                    number=i,
                )
            )
    graph.populate(now=NOW)
    return StudyStore(graph).prepare(now=NOW, channel_ids=frozenset({10}), episode_refs=refs)


def episode_refs(study):
    return [
        {k: v for k, v in s["ref"].items() if k not in {"start_line", "end_line"}}
        for s in study.snapshots
    ]


def pattern(study, kind="humor"):
    return {
        "observations": [
            {
                "kind": kind,
                "support_basis": "corroborated",
                "summary": "Extends playful roster ideas into absurd non-player jobs.",
                "conditions": "Invited playful roster brainstorming.",
                "limitations": "Answer serious votes sincerely; no real preference inferred.",
                "supports": [
                    {"source": i, "quote": study.passages[i]["author_text"]} for i in (0, 1)
                ],
                "counterexamples": [{"source": 2, "quote": study.passages[2]["author_text"]}],
                "aliases": ["roster brainstorming", "absurd roster jobs"],
            }
        ]
    }


def pattern_worker(stores):
    distiller, client, responder, channel = worker(stores)
    learning = stores[0]
    with learning._transaction() as db:
        dates = dict(db.execute("SELECT id,created_at FROM messages"))
    fetch = channel.fetch_message.side_effect

    def original_source(identifier):
        from datetime import datetime

        message = fetch(identifier)
        message.created_at = datetime.fromisoformat(dates[identifier])
        return message

    channel.fetch_message.side_effect = original_source
    return distiller, client, responder, channel


@pytest.mark.parametrize("kind", ["humor", "style"])
def test_conditional_pattern_is_representable_and_locally_valid(stores, kind):
    study = seed(stores)
    packet = pattern(study, kind)
    Draft202012Validator(extraction_schema(study)).validate(packet)
    assert validate_proposal(packet, study) == packet["observations"][0]


async def test_two_pass_pattern_reaches_summary_recall_and_invalidates_contrary_source(stores):
    learning, _, graph = stores
    study = seed(stores)
    # Release only the disposable fixture's lease, never reset production pacing.
    with graph._transaction() as (db, _):
        db.execute("DELETE FROM checkpoints WHERE stream='distillation'")
    distiller, client, responder, _ = pattern_worker(stores)

    async def generate(**kwargs):
        if kwargs["name"] == "memory_extract":
            return pattern(SimpleNamespace(passages=kwargs["payload"]["sources"]))
        assert kwargs["payload"]["proposal"]["counterexamples"]
        return {
            "accepted": True,
            "basis": "Synthetic separated cases and sincere exception.",
            "contradicts": [],
        }

    responder.study_json.side_effect = generate
    await distiller.cycle(client, episode_refs=episode_refs(study))
    assert responder.study_json.await_count == 2
    items = GraphStore(learning).lookup("roster brainstorming", guild_id=77, now=NOW)
    assert len(items) == 1 and "abstraction" in items[0]
    assert items[0]["summary"] == pattern(study)["observations"][0]["summary"]
    assert len(items[0]["abstraction"]["counterexamples"]) == 1
    memory = ContextMemory(learning)
    candidates = memory.candidates("roster brainstorming", guild_id=77, now=NOW)
    rendered = memory.render(candidates, now=NOW, verified_after=NOW)
    assert "ABSTRACT EPISODE MEMORY" in rendered
    assert "serious votes sincerely" in rendered
    assert "croissant" not in rendered and "pastry chef" not in rendered
    await distiller.cycle(client, episode_refs=episode_refs(study))
    assert responder.study_json.await_count == 2
    stores[1].remove_document(study.snapshots[2]["ref"]["document"], now=NOW)
    assert not graph.lookup("roster brainstorming", guild_id=77, now=NOW)


@pytest.mark.parametrize(
    "changes",
    [
        {"limitations": ""},
        {"limitations": "x" * 241},
        {"counterexamples": [{}] * 3},
        {"counterexamples": [{"source": True, "quote": "Invented words"}]},
        {"counterexamples": [{"source": 3, "quote": "Invented words"}]},
        {
            "counterexamples": [
                {"source": 0, "quote": "Give the baker a roster spot and count every croissant."}
            ]
        },
        {"counterexamples": [{"source": 2, "quote": "Peer claims cannot establish a pattern."}]},
        {"kind": "preference"},
        {"kind": []},
        {"support_basis": "explicit_self_report"},
    ],
)
def test_pattern_rejects_invalid_limits_and_attribution(stores, changes):
    study = seed(stores)
    packet = pattern(study)
    packet["observations"][0].update(changes)
    with pytest.raises(LearningUnavailable):
        validate_proposal(packet, study)


def test_no_counterexample_can_be_invented_or_required(stores):
    study = seed(stores)
    packet = pattern(study)
    packet["observations"][0]["counterexamples"] = []
    Draft202012Validator(extraction_schema(study)).validate(packet)
    assert validate_proposal(packet, study)
    duplicate = copy.deepcopy(packet)
    duplicate["observations"][0]["counterexamples"] = [
        pattern(study)["observations"][0]["counterexamples"][0]
    ] * 2
    with pytest.raises(LearningUnavailable):
        validate_proposal(duplicate, study)


@pytest.mark.parametrize("index", [0, 1, 2])
def test_truncated_support_or_counterexample_cannot_establish_a_pattern(stores, index):
    study = seed(stores)
    study.passages[index]["author_text_truncated"] = True
    with pytest.raises(LearningUnavailable, match="Complete pattern"):
        validate_proposal(pattern(study), study)


@pytest.mark.parametrize("mutation", ["overlapping_episode", "duplicate_hash", "duplicate_quote"])
def test_pattern_cannot_relabel_duplicate_support_or_contrary_evidence(stores, mutation):
    study = seed(stores)
    packet = pattern(study)
    if mutation == "overlapping_episode":
        study.snapshots[1]["ref"] = dict(
            study.snapshots[0]["ref"], ordinal=study.snapshots[0]["ref"]["ordinal"] + 1
        )
    elif mutation == "duplicate_hash":
        study.snapshots[2]["content_hash"] = study.snapshots[1]["content_hash"]
    else:
        study.passages[2]["author_text"] = study.passages[1]["author_text"]
        packet["observations"][0]["counterexamples"][0]["quote"] = study.passages[1]["author_text"]
    with pytest.raises(LearningUnavailable):
        validate_proposal(packet, study)


@pytest.mark.parametrize("change", ["edit", "delete", "withdraw", "retire", "reject"])
async def test_contrary_lifecycle_or_reviewer_rejection_prevents_commit(stores, change):
    learning, _, graph = stores
    study = seed(stores)
    with graph._transaction() as (db, _):
        db.execute("DELETE FROM checkpoints WHERE stream='distillation'")
    distiller, client, responder, _ = pattern_worker(stores)

    async def generate(**kwargs):
        if kwargs["name"] == "memory_extract":
            return pattern(SimpleNamespace(passages=kwargs["payload"]["sources"]))
        ref = study.snapshots[2]["ref"]
        if change in {"edit", "delete"}:
            stores[1].remove_document(ref["document"], now=NOW)
        elif change == "withdraw":
            learning.forget(now=NOW)
        elif change == "retire":
            from trubot.graph import _key

            with graph._transaction() as (db, _):
                db.execute(
                    "INSERT INTO checkpoints VALUES (?, ?)",
                    ("study-veto:" + _key(ref), study.snapshots[2]["fingerprint"]),
                )
        return {
            "accepted": change != "reject",
            "basis": "Synthetic negative control.",
            "contradicts": [],
        }

    responder.study_json.side_effect = generate
    await distiller.cycle(client, episode_refs=episode_refs(study))
    if change == "withdraw":
        assert learning.is_withdrawn() and not graph.path.exists()
    else:
        assert not graph.status()["nodes"].get("humor", 0)


@pytest.mark.parametrize("change", ["peer", "bot"])
async def test_refreshed_counterevidence_cannot_belong_to_peer_or_bot(stores, change):
    _, _, graph = stores
    study = seed(stores, native=True)
    with graph._transaction() as (db, _):
        db.execute("DELETE FROM checkpoints WHERE stream='distillation'")
    distiller, client, responder, channel = pattern_worker(stores)
    distiller.clock = distiller.ingestor.clock = lambda: NOW + timedelta(seconds=1)
    original = channel.fetch_message.side_effect

    def changed_source(identifier):
        message = original(identifier)
        if identifier == study.snapshots[2]["ref"]["message_id"]:
            message.author = SimpleNamespace(id=43 if change == "peer" else 42, bot=change == "bot")
        return message

    channel.fetch_message.side_effect = changed_source
    await distiller.cycle(client, episode_refs=episode_refs(study))
    responder.study_json.assert_not_awaited()
    assert not graph.status()["nodes"].get("humor", 0)


def test_schema_requires_conditional_fields_only_for_patterns(stores):
    study = seed(stores)
    item = pattern(study)["observations"][0]
    validator = Draft202012Validator(extraction_schema(study))
    for field in ("limitations", "counterexamples"):
        invalid = copy.deepcopy(item)
        del invalid[field]
        assert not validator.is_valid({"observations": [invalid]})
    item["kind"] = "preference"
    del item["limitations"], item["counterexamples"]
    validator.validate({"observations": [item]})
    assert validate_proposal({"observations": [item]}, study)


def test_new_pattern_provenance_does_not_force_replay_of_completed_checkpoint(stores):
    from trubot.distillation import VERSION

    study = seed(stores)
    store = StudyStore(stores[2])
    store.finish(study, None, now=NOW, outcome="rejected")
    with stores[2]._transaction() as (db, _):
        row = db.execute("SELECT cursor FROM checkpoints WHERE stream LIKE 'study:%'").fetchone()
        assert json.loads(row[0])["version"] == VERSION == "contextual-two-pass-v3"
    assert store.prepare(now=NOW + timedelta(hours=3), channel_ids=frozenset({10})) is None
    # No individual studied anchor can reappear before its original retry date.
    other = store.prepare(now=NOW + timedelta(hours=4), channel_ids=frozenset({10}))
    assert other.snapshots[0]["ref"] != study.snapshots[0]["ref"]
