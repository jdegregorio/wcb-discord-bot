"""Invented behavioral episodes, never a profile of a real participant."""

from datetime import timedelta
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from test_abstract_distillation import pattern_worker
from test_graph import observation
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.distillation import StudyStore, extraction_schema, validate_proposal
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory

DOMAINS = ("value", "emotion", "relationship")
TEXTS = (
    "You kept training for months. That effort deserves recognition.",
    "You worked hard at training even when it was rough. Proud of you.",
    "Training is not what you need right now. I can just listen.",
)


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    archive = ArchiveStore.initialize(learning)
    graph = GraphStore.initialize(learning)
    for i, text in enumerate(TEXTS):
        learning.observe(source(i, content=text, created_at=NOW - timedelta(days=i + 1)), now=NOW)
    graph.populate(now=NOW)
    return learning, archive, graph


def proposal(study, kind):
    return {
        "observations": [
            {
                "kind": kind,
                "support_basis": "corroborated",
                "summary": "Recognizes sustained effort when a friend shares training progress.",
                "conditions": "A friend invites a response to hard-earned training progress.",
                "limitations": (
                    "Listen when support is requested; no hidden motives or universal trait."
                ),
                "supports": [
                    {"source": i, "quote": study.passages[i]["author_text"]} for i in (0, 1)
                ],
                "counterexamples": [{"source": 2, "quote": study.passages[2]["author_text"]}],
                "aliases": ["training progress", "hard-earned effort"],
            }
        ],
    }


def imported(stores, kind, **changes):
    learning, _, graph = stores
    refs = [{"kind": "discord", "message_id": source(i).id} for i in range(3)]
    item = observation(
        refs[0],
        kind=kind,
        supports=refs[:2],
        summary="Recognizes sustained effort in training progress.",
        abstraction={
            "conditions": "A friend shares training progress.",
            "limitations": "Listen during setbacks; no permanent trait or hidden motives.",
            "counterexamples": refs[2:],
        },
        entities=[{"id": "effort", "kind": "concept", "aliases": ["training progress"]}],
        **changes,
    )
    graph.import_observation(item, now=NOW)
    return learning, graph, refs


@pytest.mark.parametrize("kind", DOMAINS)
def test_behavioral_domain_schema_and_local_contract(stores, kind):
    study = StudyStore(stores[2]).prepare(now=NOW, channel_ids=frozenset({10}))
    packet = proposal(study, kind)
    Draft202012Validator(extraction_schema(study)).validate(packet)
    assert validate_proposal(packet, study) == packet["observations"][0]


@pytest.mark.parametrize("kind", DOMAINS)
def test_behavioral_graph_roundtrip_uses_summaries_with_limits(stores, kind):
    learning, _, _ = imported(stores, kind)
    graph = GraphStore(learning)
    item = graph.lookup("training progress", guild_id=77, now=NOW)[0]
    assert item["kind"] == kind
    assert len(item["abstraction"]["counterexamples"]) == 1
    memory = ContextMemory(learning)
    candidates = memory.candidates("training progress", guild_id=77, now=NOW)
    rendered = memory.render(candidates, request="training progress", now=NOW, verified_after=NOW)
    assert "ABSTRACT EPISODE MEMORY" in rendered
    assert "Listen during setbacks" in rendered
    assert all(text not in rendered for text in TEXTS)
    evidence = memory.render(candidates, request="Show evidence for training progress", now=NOW)
    assert TEXTS[0] in evidence
    assert not graph.lookup("training progress", guild_id=78, now=NOW)


@pytest.mark.parametrize("kind", DOMAINS)
async def test_two_pass_behavioral_domain_commits_and_stays_paced(stores, kind):
    learning, _, graph = stores
    distiller, client, responder, _ = pattern_worker(stores)

    async def generate(**kwargs):
        if kwargs["name"] == "memory_extract":
            return proposal(SimpleNamespace(passages=kwargs["payload"]["sources"]), kind)
        assert kwargs["payload"]["proposal"]["limitations"]
        return {
            "accepted": True,
            "basis": "Separated invented episodes plus contrary case.",
            "contradicts": [],
        }

    responder.study_json.side_effect = generate
    await distiller.cycle(client)
    assert responder.study_json.await_count == 2
    item = GraphStore(learning).lookup("training progress", guild_id=77, now=NOW)[0]
    assert item["kind"] == kind and item["status"] == "tentative"
    assert item["expires_at"] == (NOW + timedelta(days=30)).isoformat()
    assert "abstraction" in item
    assert "Conditions:" not in item["summary"]
    await distiller.cycle(client)
    assert responder.study_json.await_count == 2
    graph.remove(item["id"])
    assert not graph.lookup("training progress", guild_id=77, now=NOW)
    with graph._transaction() as (db, _):
        assert (
            db.execute(
                "SELECT COUNT(*) FROM checkpoints WHERE stream LIKE 'study-veto:%'"
            ).fetchone()[0]
            == 3
        )


@pytest.mark.parametrize("kind", DOMAINS)
@pytest.mark.parametrize(
    "change", ["support_edit", "contrary_delete", "expiry", "withdrawal", "retirement"]
)
def test_behavioral_lifecycle_erases_or_blocks_stale_pattern(stores, kind, change):
    learning, graph, refs = imported(
        stores, kind, expires_at=(NOW + timedelta(days=30)).isoformat()
    )
    if change == "withdrawal":
        learning.forget(now=NOW)
        with pytest.raises(LearningUnavailable):
            graph.lookup("training progress", guild_id=77, now=NOW)
        return
    if change == "retirement":
        graph.remove("observation:dessert")
    elif change == "expiry":
        graph.sweep(now=NOW + timedelta(days=31))
    else:
        index = 0 if change == "support_edit" else 2
        learning.invalidate(10, [refs[index]["message_id"]], deleted=index == 2, now=NOW)
    assert not graph.lookup("training progress", guild_id=77, now=NOW)
    assert graph.status()["nodes"].get(kind, 0) == 0


@pytest.mark.parametrize("kind", DOMAINS)
@pytest.mark.parametrize(
    "invalid", ["flat", "single", "same_episode", "peer", "truncated", "missing_limits"]
)
def test_new_domains_cannot_bypass_pattern_contract(stores, kind, invalid):
    _learning, _, graph = stores
    study = StudyStore(graph).prepare(now=NOW, channel_ids=frozenset({10}))
    packet = proposal(study, kind)
    item = packet["observations"][0]
    if invalid == "flat":
        del item["limitations"], item["counterexamples"]
    elif invalid == "single":
        item["support_basis"] = "explicit_self_report"
        item["supports"] = item["supports"][:1]
    elif invalid == "same_episode":
        study.snapshots[1]["source_time"] = study.snapshots[0]["source_time"]
    elif invalid == "peer":
        item["supports"][0]["quote"] = "A peer says the fictional person loves every sport."
    elif invalid == "truncated":
        study.passages[2]["author_text_truncated"] = True
    else:
        item["limitations"] = ""
    with pytest.raises(LearningUnavailable):
        validate_proposal(packet, study)
    # Operator imports also cannot submit a flat new-domain observation.
    if invalid == "flat":
        with pytest.raises(LearningUnavailable):
            graph.import_observation(
                observation({"kind": "discord", "message_id": source().id}, kind=kind), now=NOW
            )
    assert graph.status()["nodes"].get(kind, 0) == 0


@pytest.mark.parametrize("kind", DOMAINS)
@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_behavioral_memories_reach_production_handlers(stores, kind, mode):
    from unittest.mock import AsyncMock, patch

    from test_discord_client import fake_channel, fake_message, make_client

    from trubot.ingestion import MessageIngestor

    learning, _, _ = imported(stores, kind)
    client, responder, _, _ = make_client(clock=lambda: NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning = ingestor
    client._memory = ContextMemory(learning)
    channel = fake_channel()

    async def history(**kwargs):
        for row in []:
            yield row

    channel.history = history
    message = fake_message(channel, direct=mode == "direct")
    message.id = 123
    message.guild = channel.guild
    message.reference = None
    message.attachments = []
    message.embeds = []
    message.content = message.clean_content = (
        "🤖 " if mode == "direct" else ""
    ) + "training progress"
    try:
        with (
            patch.object(client, "get_channel", return_value=channel),
            patch.object(ingestor, "refresh", new_callable=AsyncMock) as refresh,
        ):
            if mode == "reaction":
                channel.fetch_message.return_value = message
                await client.on_raw_reaction_add(
                    SimpleNamespace(
                        user_id=1,
                        channel_id=10,
                        message_id=123,
                        emoji=SimpleNamespace(name="ThomasJones"),
                        member=SimpleNamespace(bot=False),
                    )
                )
            else:
                if mode == "followup":
                    client._attention.activate(10, NOW)
                await client.on_message(message)
        assert refresh.await_count == 3
        context = "\n".join(m.content for m in responder.calls[0][0])
        assert "ABSTRACT EPISODE MEMORY" in context
        assert f'"domain": "{kind}"' in context
        assert "Listen during setbacks" in context
        assert all(text not in context for text in TEXTS)
        channel.send.assert_awaited_once()
    finally:
        await client.close()


@pytest.mark.parametrize("kind", DOMAINS)
async def test_changed_contrary_source_during_review_cannot_commit(stores, kind):
    learning, _, graph = stores
    distiller, client, responder, _ = pattern_worker(stores)

    async def generate(**kwargs):
        if kwargs["name"] == "memory_extract":
            return proposal(SimpleNamespace(passages=kwargs["payload"]["sources"]), kind)
        learning.invalidate(10, [source(2).id], deleted=True, now=NOW)
        return {
            "accepted": True,
            "basis": "Late review must not override deletion.",
            "contradicts": [],
        }

    responder.study_json.side_effect = generate
    await distiller.cycle(client)
    assert responder.study_json.await_count == 2
    assert not graph.lookup("training progress", guild_id=77, now=NOW)
    assert graph.status()["nodes"].get(kind, 0) == 0


def test_legacy_pattern_without_domain_metadata_remains_readable(stores):
    import json

    learning, graph, _ = imported(stores, "humor")
    with graph._transaction() as (db, _):
        data = json.loads(
            db.execute("SELECT data FROM nodes WHERE id='observation:dessert'").fetchone()[0]
        )
        del data["kind"]
        db.execute("UPDATE nodes SET data=? WHERE id='observation:dessert'", (json.dumps(data),))
    memory = ContextMemory(learning)
    candidates = memory.candidates("training progress", guild_id=77, now=NOW)
    assert '"domain": "pattern"' in memory.render(candidates, request="training progress", now=NOW)
    graph.remove("person:target")
    assert graph.status()["nodes"]["person"] == 1
