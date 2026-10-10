from datetime import timedelta

import pytest
from test_graph import observation
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def seed_pattern(stores, **changes):
    learning, _, graph = stores
    for i, text in enumerate(
        [
            "We should draft a pastry chef for dessert points.",
            "Give the baker a flex spot and count every croissant.",
            "Seriously, I want a fair transition before changing roster rules.",
        ]
    ):
        learning.observe(source(i, content=text, created_at=NOW - timedelta(days=i + 1)), now=NOW)
    refs = [{"kind": "discord", "message_id": source(i).id} for i in range(3)]
    item = observation(
        refs[0],
        kind="humor",
        supports=refs[:2],
        summary="Playfully extends scoring ideas into absurd non-player roles.",
        abstraction={
            "conditions": "Playful roster brainstorming.",
            "limitations": "Serious votes need sincere answers; not a literal preference.",
            "counterexamples": [refs[2]],
        },
        entities=[{"id": "pattern", "kind": "concept", "aliases": ["roster brainstorming"]}],
        **changes,
    )
    graph.import_observation(item, now=NOW)
    return learning, graph, refs


def test_pattern_retains_conditions_and_counterevidence_after_restart(stores):
    learning, _, refs = seed_pattern(stores)
    item = GraphStore(learning).lookup("roster brainstorming", guild_id=77, now=NOW)[0]
    assert item["abstraction"]["conditions"] == "Playful roster brainstorming."
    assert item["abstraction"]["counterexamples"][0]["ref"]["message_id"] == refs[2]["message_id"]
    with GraphStore(learning)._transaction() as (db, _):
        assert (
            db.execute("SELECT COUNT(*) FROM edges WHERE relation='counterexample-of'").fetchone()[
                0
            ]
            == 1
        )


@pytest.mark.parametrize("change", ["edit", "delete", "stale", "withdraw"])
def test_counterexample_lifecycle_invalidates_entire_pattern(stores, change):
    learning, graph, refs = seed_pattern(stores)
    memory = ContextMemory(learning)
    candidates = memory.candidates("roster brainstorming", guild_id=77, now=NOW)
    assert len(candidates) == 3
    if change == "withdraw":
        learning.forget(now=NOW)
        with pytest.raises(LearningUnavailable):
            memory.render(candidates, now=NOW, verified_after=NOW)
        return
    if change == "stale":
        with learning._transaction() as db:
            db.execute(
                "UPDATE messages SET verified_at=? WHERE id=?",
                ((NOW - timedelta(minutes=1)).isoformat(), refs[2]["message_id"]),
            )
        assert "ABSTRACT EPISODE MEMORY" not in memory.render(
            candidates, now=NOW, verified_after=NOW
        )
        return
    learning.invalidate(10, [refs[2]["message_id"]], deleted=change == "delete", now=NOW)
    assert graph.lookup("roster brainstorming", guild_id=77, now=NOW) == []
    assert "ABSTRACT EPISODE MEMORY" not in memory.render(candidates, now=NOW)


def test_ordinary_pattern_context_uses_abstraction_evidence_request_keeps_sources(stores):
    learning, _, _ = seed_pattern(stores)
    memory = ContextMemory(learning)
    candidates = memory.candidates("roster brainstorming", guild_id=77, now=NOW)
    ordinary = memory.render(
        candidates, request="roster brainstorming", now=NOW, verified_after=NOW
    )
    assert "ABSTRACT EPISODE MEMORY" in ordinary
    assert "pastry chef" not in ordinary and "croissant" not in ordinary
    assert "Serious votes need sincere answers" in ordinary
    assert "not an actual quote" in ordinary
    explicit = memory.render(
        candidates, request="Show evidence for roster brainstorming", now=NOW, verified_after=NOW
    )
    assert "pastry chef" in explicit and "croissant" in explicit
    assert "counterexample" in explicit
    assert not memory.candidates("roster brainstorming", guild_id=78, now=NOW)
    assert not memory.candidates("unrelated volcano", guild_id=77, now=NOW)


@pytest.mark.parametrize(
    "abstraction",
    [
        {},
        {"conditions": "x", "limitations": "y", "counterexamples": [{}] * 3},
        {"conditions": "x" * 241, "limitations": "y", "counterexamples": []},
        {
            "conditions": "x",
            "limitations": "y",
            "counterexamples": [{"kind": "discord", "message_id": source().id}],
        },
        {
            "conditions": "x",
            "limitations": "y",
            "counterexamples": [{"kind": "discord", "message_id": 123}],
        },
    ],
)
def test_bad_pattern_contract_rolls_back(stores, abstraction):
    learning, _, graph = stores
    learning.observe(source(content="one"), now=NOW)
    learning.observe(source(1, content="two", created_at=NOW - timedelta(days=2)), now=NOW)
    item = observation(
        {"kind": "discord", "message_id": source().id},
        kind="style",
        supports=[{"kind": "discord", "message_id": source(i).id} for i in range(2)],
        abstraction=abstraction,
    )
    with pytest.raises(LearningUnavailable):
        graph.import_observation(item, now=NOW)
    assert graph.status()["nodes"] == {}


def test_single_and_same_episode_do_not_establish_pattern(stores):
    learning, _, graph = stores
    for i in range(2):
        learning.observe(source(i, content=f"Pastry banter {i}"), now=NOW)
    abstraction = {
        "conditions": "banter",
        "limitations": "no universal trait",
        "counterexamples": [],
    }
    for supports in [
        [{"kind": "discord", "message_id": source().id}],
        [{"kind": "discord", "message_id": source(i).id} for i in range(2)],
    ]:
        with pytest.raises(LearningUnavailable):
            graph.import_observation(
                observation(supports[0], kind="humor", supports=supports, abstraction=abstraction),
                now=NOW,
            )


def test_replacing_pattern_removes_old_counterexample_edges(stores):
    _learning, graph, refs = seed_pattern(stores)
    graph.import_observation(
        observation(
            refs[0],
            kind="humor",
            supports=refs[:2],
            abstraction={"conditions": "banter", "limitations": "qualified", "counterexamples": []},
        ),
        now=NOW,
    )
    with graph._transaction() as (db, _):
        assert (
            db.execute("SELECT COUNT(*) FROM edges WHERE relation='counterexample-of'").fetchone()[
                0
            ]
            == 0
        )


def test_retirement_expiry_and_backup_counterevidence(stores):
    learning, graph, refs = seed_pattern(stores, expires_at=(NOW + timedelta(hours=1)).isoformat())
    assert graph.lookup("roster brainstorming", guild_id=77, now=NOW + timedelta(hours=2)) == []
    backups = learning.path.parent / "backups"
    backups.mkdir(mode=0o700)
    backup = backups / "memory-graph-old.sqlite3"
    backup.write_bytes(graph.path.read_bytes())
    backup.chmod(0o600)
    learning.invalidate(10, [refs[2]["message_id"]], deleted=True, now=NOW)
    assert not backup.exists()
    graph.remove("observation:dessert")
    assert graph.status()["nodes"].get("humor", 0) == 0


@pytest.mark.parametrize(
    "source_change", [{"author_id": 43}, {"bot": True}, {"webhook": True}, {"guild_id": 78}]
)
def test_counterevidence_requires_the_attributed_human(stores, source_change):
    learning, graph, refs = seed_pattern(stores)
    learning.observe(source(9, content="Peer claim is not support.", **source_change), now=NOW)
    with pytest.raises(LearningUnavailable):
        graph.import_observation(
            observation(
                refs[0],
                kind="humor",
                supports=refs[:2],
                abstraction={
                    "conditions": "banter",
                    "limitations": "qualified",
                    "counterexamples": [{"kind": "discord", "message_id": source(9).id}],
                },
            ),
            now=NOW,
        )


@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_patterns_flow_through_real_discord_handlers_with_all_sources_refreshed(stores, mode):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, patch

    from test_discord_client import fake_channel, fake_message, make_client

    from trubot.ingestion import MessageIngestor

    learning, _, _ = seed_pattern(stores)
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
    ) + "roster brainstorming"
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
        assert "ABSTRACT EPISODE MEMORY" in context and "croissant" not in context
        assert "Serious votes need sincere answers" in context
        channel.send.assert_awaited_once()
    finally:
        await client.close()


def test_slack_counterexample_suppression_erases_pattern(stores):
    _learning, archive, graph = stores
    refs = []
    for i, body in enumerate(
        [
            "I nominate a pastry chef.",
            "I would draft a baker.",
            "A serious rule needs a transition.",
        ]
    ):
        archive.import_document(
            ("legacy.target\n  8:00 AM\n" + body).encode(),
            channel="synthetic",
            target_alias="legacy.target",
            alias_basis="synthetic audit",
            origin={"kind": "synthetic", "index": i},
            now=NOW,
        )
        with archive._transaction() as db:
            digest = db.execute(
                "SELECT document FROM messages WHERE content=?", (body,)
            ).fetchone()[0]
        refs.append({"kind": "slack", "document": digest, "ordinal": 0})
    graph.import_observation(
        observation(
            refs[0],
            kind="style",
            supports=refs[:2],
            abstraction={
                "conditions": "banter",
                "limitations": "not every exchange",
                "counterexamples": refs[2:],
            },
        ),
        now=NOW,
    )
    assert graph.lookup("dessert", guild_id=77, now=NOW)
    archive.remove_document(refs[2]["document"], now=NOW)
    assert not graph.lookup("dessert", guild_id=77, now=NOW)


def test_pattern_counterevidence_counts_toward_complete_neighborhood_bound(stores):
    learning, graph, _refs = seed_pattern(stores)
    for i in range(3, 6):
        learning.observe(
            source(i, content=f"Separate source {i}", created_at=NOW - timedelta(days=i + 1)),
            now=NOW,
        )
    extra = [{"kind": "discord", "message_id": source(i).id} for i in range(3, 6)]
    graph.import_observation(
        observation(
            extra[0],
            id="second",
            supports=extra,
            entities=[{"id": "pattern", "kind": "concept", "aliases": ["roster brainstorming"]}],
        ),
        now=NOW,
    )
    assert graph.lookup("roster brainstorming", guild_id=77, now=NOW) == []


def test_pattern_quotes_and_factual_shared_support_stay_available(stores):
    learning, graph, refs = seed_pattern(stores)
    graph.import_observation(
        observation(
            refs[0],
            id="specific",
            summary="A particular pastry suggestion was made.",
            entities=[{"id": "pattern", "kind": "concept", "aliases": ["roster brainstorming"]}],
        ),
        now=NOW,
    )
    memory = ContextMemory(learning)
    candidates = memory.candidates("roster brainstorming", guild_id=77, now=NOW)
    assert "pastry chef" in memory.render(candidates, request="roster brainstorming", now=NOW)
    assert "croissant" in memory.render(
        candidates, request="Quote an example of roster brainstorming", now=NOW
    )
