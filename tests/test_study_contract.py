import copy
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from test_distillation import proposal, seed, worker
from test_learning import AUDIT, NOW

from trubot.archives import ArchiveStore
from trubot.distillation import extraction_schema, review_schema, validate_proposal
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable


# Reuse disposable evidence fixtures, never a production identity or source.
@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def singleton():
    text = "I prefer caramel ice cream after dinner."
    study = SimpleNamespace(
        passages=[
            {"author_text": text, "author_text_truncated": False},
            {
                "author_text": "Caramel is my dessert choice after a meal.",
                "author_text_truncated": False,
            },
        ],
        snapshots=[
            {"content_hash": str(i), "ref": {"kind": "slack", "document": str(i), "ordinal": 0}}
            for i in range(2)
        ],
    )
    item = {
        "kind": "preference",
        "support_basis": "explicit_self_report",
        "summary": "A specific dessert choice.",
        "conditions": "In this exchange only.",
        "supports": [{"source": 0, "quote": text}],
        "aliases": ["caramel", "dessert"],
    }
    return study, {"observations": [item]}


@pytest.mark.parametrize(
    "changes",
    [
        {"summary": "s" * 241},
        {"summary": ""},
        {"conditions": "c" * 241},
        {"conditions": ""},
        {"aliases": ["caramel"]},
        {"aliases": ["caramel"] * 6},
        {"aliases": ["x" * 61, "dessert"]},
        {"aliases": ["xy", "dessert"]},
        {"supports": [{"source": 0, "quote": "I prefer caramel ice cream after dinner."}] * 2},
        {"kind": "style"},
        {"supports": [{"source": 2, "quote": "I prefer caramel ice cream after dinner."}]},
        {"supports": [{"source": 0, "quote": "I prefer caramel ice cream after dinner"}]},
        {"support_basis": "corroborated"},
        {
            "support_basis": "corroborated",
            "supports": [{"source": 0, "quote": "q" * 301}, {"source": 1, "quote": "q" * 301}],
        },
    ],
)
def test_provider_contract_excludes_known_locally_invalid_forms(changes):
    study, packet = singleton()
    packet["observations"][0].update(changes)
    assert not Draft202012Validator(extraction_schema(study)).is_valid(packet)
    with pytest.raises(LearningUnavailable):
        validate_proposal(packet, study)


def test_valid_singleton_corroboration_and_abstention_remain_possible():
    study, packet = singleton()
    schema = extraction_schema(study)
    Draft202012Validator.check_schema(schema)
    validate = Draft202012Validator(schema)
    validate.validate(packet)
    assert validate_proposal(packet, study)
    validate.validate({"observations": []})
    assert validate_proposal({"observations": []}, study) is None
    packet["observations"][0]["support_basis"] = "corroborated"
    packet["observations"][0]["supports"] = [
        {"source": i, "quote": passage["author_text"]} for i, passage in enumerate(study.passages)
    ]
    validate.validate(packet)
    assert validate_proposal(packet, study)
    packet["observations"].append(copy.deepcopy(packet["observations"][0]))
    assert not validate.is_valid(packet)


@pytest.mark.parametrize(
    "text,truncated",
    [("Caramel sounds nice.", False), ('I like "caramel".', False), ("I prefer caramel.", True)],
)
def test_context_or_truncation_cannot_enter_singleton_branch(text, truncated):
    study, packet = singleton()
    study.passages[0].update(author_text=text, author_text_truncated=truncated)
    packet["observations"][0]["supports"][0]["quote"] = text
    assert not Draft202012Validator(extraction_schema(study)).is_valid(packet)


def test_no_support_is_a_valid_empty_abstention():
    study, _ = singleton()
    study.passages = [{"author_text": "Not an explicit statement.", "author_text_truncated": False}]
    schema = extraction_schema(study)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate({"observations": []})
    for size in (0, 7):
        study.passages = [{}] * size
        with pytest.raises(LearningUnavailable):
            extraction_schema(study)


def test_multiline_unicode_and_trailing_newline_bounds_are_exact():
    study, packet = singleton()
    validator = Draft202012Validator(extraction_schema(study))
    for text in ("🦌" * 240, "x" * 239 + "\n", "first line\nsecond line"):
        packet["observations"][0]["summary"] = text
        validator.validate(packet)
    packet["observations"][0]["summary"] = "x" * 240 + "\n"
    assert not validator.is_valid(packet)


@pytest.mark.parametrize("count", [0, 1, 4])
def test_review_can_only_reference_supplied_observations(count):
    schema = review_schema(count)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    item = {"accepted": False, "basis": "Historical scope only.", "contradicts": []}
    validator.validate(item)
    item["contradicts"] = [count]
    assert not validator.is_valid(item)
    if count:
        item["contradicts"] = [count - 1]
        validator.validate(item)
    for values in ([-1], [False], [0] * 5):
        item["contradicts"] = values
        assert not validator.is_valid(item)
    item["contradicts"] = []
    for basis in ("", "x" * 401):
        item["basis"] = basis
        assert not validator.is_valid(item)
    with pytest.raises(LearningUnavailable):
        review_schema(-1)


async def test_learner_supplies_packet_bound_schemas_and_still_rechecks_evidence(stores):
    seed(stores)
    distiller, client, responder, _ = worker(stores)
    await distiller.cycle(client)
    extract, review = responder.study_json.await_args_list
    assert extract.kwargs["schema"]["properties"]["observations"]["maxItems"] == 1
    study = SimpleNamespace(passages=extract.kwargs["payload"]["sources"])
    Draft202012Validator(extract.kwargs["schema"]).validate(proposal(study))
    assert review.kwargs["schema"]["properties"]["contradicts"]["maxItems"] == 0
    await extract.kwargs["source_check"]()
    assert stores[2].status()["nodes"]["preference"] == 1


def test_schema_does_not_replace_semantic_attribution_and_independence_checks():
    study, packet = singleton()
    packet["observations"][0]["support_basis"] = "corroborated"
    for supports in (
        [{"source": 0, "quote": study.passages[0]["author_text"]}] * 2,
        [
            {"source": 0, "quote": "Invented author words go here."},
            {"source": 1, "quote": "Another invented author quote."},
        ],
    ):
        packet["observations"][0]["supports"] = supports
        Draft202012Validator(extraction_schema(study)).validate(packet)
        with pytest.raises(LearningUnavailable):
            validate_proposal(packet, study)
