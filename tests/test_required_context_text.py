"""Whole captured setup admission, using invented episodes and no provider calls."""

import json
from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from test_distillation import worker
from test_learning import AUDIT, NOW
from test_native_study_context import setup as native_setup
from test_study_context import export

from trubot.archives import ArchiveStore
from trubot.distillation import StudyStore, _fit_context
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.openai_responder import StudyContextExceeded


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def select(stores, refs, **kwargs):
    return StudyStore(stores[2]).prepare(
        now=NOW, channel_ids=frozenset({10}), episode_refs=refs, require_context_text=True, **kwargs
    )


def no_lease(graph):
    with graph._transaction() as (db, _):
        assert (
            db.execute("SELECT 1 FROM checkpoints WHERE stream='distillation'").fetchone() is None
        )


@pytest.mark.parametrize("text", ["x" * 601, "x" * 4000, "🎂" * 1000])
def test_selected_context_keeps_complete_byte_bound_roles_and_speakers(stores, text):
    ref = export(
        stores, [("peer", text), ("fixture.target", "A fictional reply."), ("peer", "After.")]
    )
    study = select(stores, [ref])
    rows = study.passages[0]["adjacent_context"]
    assert [r["text"] for r in rows] == [text, "After."]
    assert rows[0]["speaker_key"] == rows[1]["speaker_key"]
    assert all(r["author_role"] == "other_speaker" and not r["text_truncated"] for r in rows)
    assert study.passages[0]["context_omitted"] == 0


@pytest.mark.parametrize("text", ["x" * 4001, "🎂" * 1001])
async def test_oversized_setup_stops_before_lease_and_provider(stores, text):
    ref = export(
        stores, [("peer", text), ("fixture.target", "I prefer caramel ice cream after dinner.")]
    )
    with pytest.raises(StudyContextExceeded, match="row bound"):
        select(stores, [ref])
    no_lease(stores[2])
    distiller, client, responder, _ = worker(stores)
    assert await distiller.cycle(client, episode_refs=[ref], require_context_text=True) is None
    responder.study_json.assert_not_awaited()
    no_lease(stores[2])


async def test_total_context_overflow_keeps_whole_cohort_and_stops_before_provider(stores):
    refs = [
        export(stores, [("peer", "x" * 4000), ("fixture.target", f"Reply {i}.")], number=i)
        for i in range(3)
    ]
    with pytest.raises(StudyContextExceeded, match="request bound"):
        select(stores, refs)
    no_lease(stores[2])
    distiller, client, responder, _ = worker(stores)
    assert await distiller.cycle(client, episode_refs=refs, require_context_text=True) is None
    responder.study_json.assert_not_awaited()


@pytest.mark.parametrize("selector", ["automatic", "anchor", "default_exact"])
def test_default_paths_keep_optional_context_bound(stores, selector):
    ref = export(stores, [("peer", "x" * 601), ("fixture.target", "A reply.")])
    kwargs = (
        {"anchor_ref": ref}
        if selector == "anchor"
        else {"episode_refs": [ref]}
        if selector == "default_exact"
        else {}
    )
    study = StudyStore(stores[2]).prepare(now=NOW, channel_ids=frozenset({10}), **kwargs)
    assert study.passages[0]["adjacent_context"] == []
    assert study.passages[0]["context_omitted"] == 1


def test_strict_mode_requires_deliberate_exact_selection(stores):
    with pytest.raises(LearningUnavailable, match="exact episode"):
        select(stores, None)
    no_lease(stores[2])


def test_previously_omitted_context_cannot_be_certified_complete(stores):
    ref = export(stores, [("peer", "x" * 601), ("fixture.target", "A reply.")])
    packed = StudyStore(stores[2]).prepare(now=NOW, channel_ids=frozenset({10}), episode_refs=[ref])
    with pytest.raises(StudyContextExceeded):
        _fit_context(packed, require_context_text=True)


async def test_late_roleplay_qualification_reaches_both_passes_and_peer_cannot_support(stores):
    from trubot.distillation import validate_proposal

    setup = "Fictional setup. " * 45 + "This is roleplay, not a real preference."
    text = "I prefer caramel ice cream after dinner."
    ref = export(stores, [("peer", setup), ("fixture.target", text)])
    distiller, client, responder, _ = worker(stores)
    packets = []

    async def generate(**kwargs):
        packets.append(kwargs["payload"]["sources"])
        await kwargs["source_check"]()
        if kwargs["name"] == "memory_extract":
            return {
                "observations": [
                    {
                        "kind": "preference",
                        "support_basis": "explicit_self_report",
                        "summary": "Prefers caramel dessert.",
                        "conditions": "After dinner.",
                        "supports": [{"source": 0, "quote": text}],
                        "aliases": ["caramel", "dessert"],
                    }
                ]
            }
        return {
            "accepted": False,
            "basis": "The supplied setup makes this roleplay.",
            "contradicts": [],
        }

    responder.study_json.side_effect = generate
    assert (
        await distiller.cycle(client, episode_refs=[ref], require_context_text=True) == "rejected"
    )
    assert len(packets) == 2 and packets[0] == packets[1]
    assert packets[0][0]["adjacent_context"][0]["text"] == setup
    assert not stores[2].lookup("caramel", guild_id=77, now=NOW)
    assert await distiller.cycle(client, episode_refs=[ref], require_context_text=True) is None
    assert len(packets) == 2
    study = StudyStore(stores[2]).prepare(
        now=NOW + timedelta(days=31),
        channel_ids=frozenset({10}),
        episode_refs=[ref],
        require_context_text=True,
    )
    bad = {
        "observations": [
            {
                "kind": "preference",
                "support_basis": "explicit_self_report",
                "summary": "A peer claim.",
                "conditions": "Context only.",
                "supports": [{"source": 0, "quote": setup[:200]}],
                "aliases": ["caramel", "dessert"],
            }
        ]
    }
    with pytest.raises(
        LearningUnavailable, match=r"Exact attributed quote|first-person self-report"
    ):
        validate_proposal(bad, study)


@pytest.mark.parametrize("failure", ["remove", "withdraw"])
async def test_source_lifecycle_still_stops_strict_study(stores, failure):
    ref = export(
        stores,
        [("peer", "x" * 700), ("fixture.target", "I prefer caramel ice cream after dinner.")],
    )
    distiller, client, responder, _ = worker(stores)

    async def changed(**kwargs):
        if failure == "withdraw":
            stores[0].forget(now=NOW)
        else:
            stores[1].remove_document(ref["document"], now=NOW)
        return {"observations": []}

    responder.study_json.side_effect = changed
    assert await distiller.cycle(client, episode_refs=[ref], require_context_text=True) is None
    assert responder.study_json.await_count == 1


@pytest.mark.parametrize("event", ["stable", "edit"])
async def test_fresh_native_context_obeys_strict_mode_and_retains_lifecycle(tmp_path, event):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(learning)
    graph = GraphStore.initialize(learning)
    distiller, client, responder, _, focus, peer = await native_setup(
        (learning, graph), text="Fictional setup. " * 30
    )
    original = responder.study_json.side_effect
    original_setup = peer.content

    async def generate(**kwargs):
        assert any(
            r["text"] == original_setup for r in kwargs["payload"]["sources"][0]["adjacent_context"]
        )
        result = await original(**kwargs)
        if event == "edit":
            peer.content = "Changed setup."
        return result

    responder.study_json.side_effect = generate
    outcome = await distiller.cycle(
        client,
        episode_refs=[{"kind": "discord", "message_id": focus.id}],
        require_context_text=True,
    )
    assert outcome == ("accepted" if event == "stable" else None)
    assert responder.study_json.await_count == 2


def test_command_propagates_strict_mode(tmp_path, monkeypatch, capsys):
    from trubot import study

    tmp_path.chmod(0o700)
    path = tmp_path / "episodes.json"
    refs = [{"kind": "discord", "message_id": 1}]
    path.write_text(json.dumps({"schema": 1, "episode_refs": refs}))
    path.chmod(0o600)
    runner = AsyncMock(return_value={"completed": True})
    monkeypatch.setattr(study, "run", runner)
    monkeypatch.setattr(
        "sys.argv", ["trubot-study", "--episodes", str(path), "--require-context-text"]
    )
    study.main()
    runner.assert_awaited_once_with(refs, require_context_text=True)
    assert json.loads(capsys.readouterr().out)["completed"]


async def test_native_collector_size_gap_stops_strict_mode_before_provider(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(learning)
    graph = GraphStore.initialize(learning)
    distiller, client, responder, _, focus, _ = await native_setup(
        (learning, graph), text="Fictional setup. " * 45
    )
    assert (
        await distiller.cycle(
            client,
            episode_refs=[{"kind": "discord", "message_id": focus.id}],
            require_context_text=True,
        )
        is None
    )
    responder.study_json.assert_not_awaited()


def test_truncated_captured_row_cannot_be_certified_complete(stores):
    ref = export(stores, [("peer", "A setup."), ("fixture.target", "A reply.")])
    packed = select(stores, [ref])
    packed.passages[0]["adjacent_context"][0]["text_truncated"] = True
    with pytest.raises(StudyContextExceeded):
        _fit_context(packed, require_context_text=True)
