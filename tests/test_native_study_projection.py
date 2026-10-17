"""Fresh study setup remains complete, anonymous and subject to the existing gate."""

import json
from dataclasses import replace

import pytest
from test_learning import BASE, NOW, source
from test_native_study_context import setup, stores  # noqa: F401

from trubot.distillation import (
    _CONTEXT_ENVELOPE,
    _EXTRACT,
    Study,
    _fit_context,
    _native_study_passage,
    extraction_schema,
)
from trubot.learning import LearningUnavailable
from trubot.native_context import NativeEpisode
from trubot.openai_responder import StudyContextExceeded, study_request_size


def episode(*, count=5, body="Complete synthetic setup."):
    rows = tuple(
        {
            "message_id": BASE - i,
            "speaker_id": 88 if i != 2 else 42,
            "position": "before",
            "created_at": NOW.isoformat(),
            "reply_to_message_id": BASE if i == 1 else BASE - 1 if i == 2 else 123,
            "focus_replies_to_this": i == 1,
            "visual_context": "pixels not retrieved" if i == 3 else "no captured media",
            "text": body,
        }
        for i in range(1, count + 1)
    )
    return NativeEpisode(
        source_text="I prefer caramel ice cream.",
        source_edited_at=None,
        neighbors=rows,
        gaps=("source media pixels not retrieved",),
        source=source(content="I prefer caramel ice cream."),
    )


def passage():
    return {
        "source_index": 0,
        "author_text": "I prefer caramel ice cream.",
        "author_text_truncated": False,
        "context_scope": "native_target_only_peer_setup_missing",
        "source_time": NOW.isoformat(),
        "unknown_date": False,
        "adjacent_context": [],
        "context_omitted": 0,
    }


def packet(ep):
    return Study(
        "synthetic",
        [{"ref": {"kind": "discord"}}],
        [_native_study_passage(passage(), ep)],
    )


def test_anonymous_links_positions_speakers_and_media_are_preserved():
    ep = episode()
    # The source fixture's pinned human author is 42.
    assert ep.source.author_id == 42
    p = _native_study_passage(passage(), ep)
    rows = p["adjacent_context"]
    assert [r["offset"] for r in rows] == [-5, -4, -3, -2, -1]
    assert rows[-1]["reply_to_context"] == "focus"
    assert rows[-2]["reply_to_context"] == "neighbor:-1"
    assert rows[0]["reply_to_context"] == "outside_captured_context"
    assert rows[-1]["focus_replies_to_this"]
    assert rows[-2]["speaker_key"] == "target"
    assert rows[-2]["author_role"] == "verified_target_context_only"
    assert rows[0]["speaker_key"] == rows[-1]["speaker_key"] == "peer:1"
    assert rows[2]["flags"] == ["pixels not retrieved"]
    assert p["context_gaps"] == list(ep.gaps)
    serialized = json.dumps(p)
    for key in ("message_id", "speaker_id", "guild_id", "channel_id"):
        assert f'"{key}"' not in serialized
    assert str(BASE) not in serialized


def test_after_context_and_unlinked_rows_are_distinct():
    ep = episode(count=1)
    row = ep.neighbors[0] | {
        "message_id": BASE + 1,
        "position": "after",
        "reply_to_message_id": None,
        "focus_replies_to_this": False,
    }
    p = _native_study_passage(passage(), replace(ep, neighbors=(row,)))
    assert p["adjacent_context"][0]["offset"] == 1
    assert p["adjacent_context"][0]["reply_to_context"] is None


@pytest.mark.parametrize("text", ["x" * 600, "🦆" * 150, "x" * 601, "🦆" * 151])
def test_five_context_rows_are_whole_or_explicitly_omitted(text):
    study = packet(episode(body=text))
    result = _fit_context(study, require_all_sources=True)
    p = result.passages[0]
    if len(text.encode()) <= 600:
        assert len(p["adjacent_context"]) == 5
        assert all(r["text"] == text for r in p["adjacent_context"])
        assert p["context_omitted"] == 0
    else:
        assert not p["adjacent_context"]
        assert p["context_omitted"] == 5
        assert text[:350] not in json.dumps(result.passages, ensure_ascii=False)
    assert (
        study_request_size(_EXTRACT, {"sources": result.passages}, extraction_schema(result))
        <= _CONTEXT_ENVELOPE
    )


def test_reprojection_preserves_prior_omissions_and_original_cohort():
    study = packet(episode(body="x" * 601))
    once = _fit_context(study, require_all_sources=True)
    twice = _fit_context(once, require_all_sources=True)
    assert twice.passages == once.passages
    assert twice.snapshots == study.snapshots
    assert twice.passages[0]["context_omitted"] == 5
    oversized = replace(study, passages=[passage() | {"author_text": "x" * 20000}])
    with pytest.raises(StudyContextExceeded):
        _fit_context(oversized, require_all_sources=True)


def test_context_does_not_open_native_automatic_pattern_schema():
    study = packet(episode())
    study = replace(study, snapshots=study.snapshots * 2, passages=study.passages * 2)
    schema = json.dumps(extraction_schema(study))
    for kind in ("humor", "style", "value", "emotion", "relationship"):
        assert f'"{kind}"' not in schema


def test_no_fresh_source_cannot_supply_setup():
    with pytest.raises(LearningUnavailable):
        _native_study_passage(passage(), replace(episode(), source=None))


async def test_contextual_reviewer_can_reject_fiction_without_learning(stores):  # noqa: F811
    distiller, client, responder, _, _, peer = await setup(stores)
    original = responder.study_json.side_effect

    async def contextual_review(**kwargs):
        result = await original(**kwargs)
        if kwargs["name"] == "memory_review":
            assert kwargs["payload"]["sources"][0]["adjacent_context"][0]["text"] == peer.content
            return {
                "accepted": False,
                "basis": "Fictional premise, not a human preference.",
                "contradicts": [],
            }
        return result

    responder.study_json.side_effect = contextual_review
    assert await distiller.cycle(client) == "rejected"
    assert responder.study_json.await_count == 2
    assert not stores[1].lookup("dessert", guild_id=77, now=NOW)
