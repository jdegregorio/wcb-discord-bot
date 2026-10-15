"""Invented memory growth cases, never evidence about a real person."""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from test_discord_client import fake_channel, fake_message, make_client
from test_episode_memory import seed_pattern
from test_graph import observation
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def add(stores, number, *, aliases=("sweet tooth",), supports=None, topic=None, **changes):
    learning, _, graph = stores
    refs = []
    for i in supports or [number]:
        learning.observe(source(i, content=f"Invented caramel episode {i}."), now=NOW)
        refs.append({"kind": "discord", "message_id": source(i).id})
    if "contradicts" in changes:
        changes["contradicts"] = [k.removeprefix("observation:") for k in changes["contradicts"]]
    item = observation(
        refs[0],
        id=f"memory-{number:03}",
        supports=refs,
        entities=[
            {"id": topic or f"topic-{number:03}", "kind": "concept", "aliases": list(aliases)}
        ],
        **changes,
    )
    graph.import_observation(item, now=NOW)
    return "observation:" + item["id"]


@pytest.mark.parametrize("count", [5, 13, 40])
def test_growth_keeps_bounded_useful_memories(stores, count):
    for i in range(count):
        add(stores, i)
    result = stores[2].lookup("sweet tooth", guild_id=77, now=NOW)
    assert len(result) == 4
    assert len({s["ref"]["message_id"] for item in result for s in item["supports"]}) <= 5
    assert result == GraphStore(stores[0]).lookup("sweet tooth", guild_id=77, now=NOW)


def test_specific_alias_beats_generic_matches_beyond_old_concept_limit(stores):
    for i in range(9):
        add(stores, i, aliases=("sweet",))
    wanted = add(stores, 99)
    result = stores[2].lookup("sweet tooth", guild_id=77, now=NOW)
    assert result[0]["id"] == wanted


def test_valid_memory_beyond_old_neighbor_limit(stores):
    for i in range(13):
        add(stores, i, topic="shared", expires_at=(NOW + timedelta(seconds=1)).isoformat())
    wanted = add(stores, 99, topic="shared")
    result = stores[2].lookup("sweet tooth", guild_id=77, now=NOW + timedelta(seconds=2))
    assert [r["id"] for r in result] == [wanted]


def test_complete_transitive_conflict_is_retrieved(stores):
    a = add(stores, 0)
    b = add(stores, 1, aliases=("vanilla",), contradicts=[a])
    c = add(stores, 2, aliases=("sorbet",), contradicts=[b])
    result = stores[2].lookup("sweet tooth", guild_id=77, now=NOW)
    assert {r["id"] for r in result} == {a, b, c}
    assert all(r["status"] == "contested" for r in result)


def test_oversized_conflict_skips_whole_component_and_keeps_independent_memory(stores):
    last = add(stores, 0)
    conflicted = [last]
    for i in range(1, 6):
        last = add(stores, i, aliases=("sweet tooth" if i == 5 else "vanilla",), contradicts=[last])
        conflicted.append(last)
    wanted = add(stores, 99)
    result = stores[2].lookup("sweet tooth", guild_id=77, now=NOW)
    assert [r["id"] for r in result] == [wanted]
    assert not {r["id"] for r in result} & set(conflicted)


def test_capacity_does_not_split_a_conflict_to_fill_last_slot(stores):
    for i in range(3):
        add(stores, i, aliases=("very sweet tooth",))
    a = add(stores, 5)
    b = add(stores, 6, aliases=("vanilla",), contradicts=[a])
    result = stores[2].lookup("very sweet tooth", guild_id=77, now=NOW)
    assert len(result) == 3 and not {r["id"] for r in result} & {a, b}


def test_source_limit_skips_independent_component_instead_of_erasing_others(stores):
    a = add(stores, 0, supports=[0, 1, 2])
    add(stores, 3, supports=[3, 4, 5])
    c = add(stores, 9)
    result = stores[2].lookup("sweet tooth", guild_id=77, now=NOW)
    assert {r["id"] for r in result} == {a, c}


@pytest.mark.parametrize("change", ["expired", "deleted", "wrong_guild", "withdrawn"])
def test_growth_retains_source_lifecycle(stores, change):
    keys = [add(stores, i) for i in range(5)]
    learning, _, graph = stores
    guild = 77
    now = NOW
    if change == "expired":
        add(stores, 0, expires_at=(NOW + timedelta(seconds=1)).isoformat())
        now += timedelta(seconds=2)
    elif change == "deleted":
        learning.invalidate(10, [source(0).id], deleted=True, now=NOW)
    elif change == "wrong_guild":
        guild = 78
    else:
        learning.forget(now=NOW)
        with pytest.raises(LearningUnavailable):
            graph.lookup("sweet tooth", guild_id=guild, now=NOW)
        return
    result = graph.lookup("sweet tooth", guild_id=guild, now=now)
    assert len(result) == (0 if change == "wrong_guild" else 4)
    assert keys[0] not in {r["id"] for r in result}


def test_growth_keeps_abstract_projection_and_counterevidence_bound(stores):
    learning, _, refs = seed_pattern(stores)
    for i in range(3, 8):
        add(stores, i, aliases=("roster",))
    memory = ContextMemory(learning)
    candidates = memory.candidates("roster brainstorming", guild_id=77, now=NOW)
    packet = memory.render_packet(
        candidates, now=NOW, verified_after=NOW, request="roster brainstorming"
    )
    assert "ABSTRACT EPISODE MEMORY" in packet.text
    assert "Serious votes need sincere answers" in packet.text
    assert "croissant" not in packet.text and not packet.allow_voice_examples
    assert len(candidates) == 5
    assert {c.source["message_id"] for c in candidates}.issuperset(r["message_id"] for r in refs)


@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_growing_graph_reaches_actual_handlers(stores, mode):
    for i in range(5):
        add(stores, i)
    learning, _, _ = stores
    client, responder, _, _ = make_client(clock=lambda: NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(learning)
    channel = fake_channel()

    async def history(**kwargs):
        for row in []:
            yield row

    channel.history = history
    message = fake_message(channel, direct=mode == "direct")
    message.id, message.guild, message.reference = 123, channel.guild, None
    message.attachments, message.embeds = [], []
    message.content = message.clean_content = ("🤖 " if mode == "direct" else "") + "sweet tooth"
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
        context = "\n".join(m.content for m in responder.calls[0][0])
        assert "CONNECTED REVIEWED MEMORY" in context
        assert refresh.await_count == 8
        assert refresh.await_args_list[:4] == refresh.await_args_list[4:]
        channel.send.assert_awaited_once()
    finally:
        await client.close()


def test_freshness_work_is_bounded_even_when_early_memories_expire(stores):
    for i in range(70):
        add(stores, i, expires_at=(NOW + timedelta(seconds=1)).isoformat())
    graph = stores[2]
    with patch.object(graph, "_valid", wraps=graph._valid) as validate:
        assert graph.lookup("sweet tooth", guild_id=77, now=NOW + timedelta(seconds=2)) == []
    assert validate.call_count <= 64


def test_validation_limit_cannot_emit_half_a_conflict(stores):
    for i in range(63):
        add(stores, i, expires_at=(NOW + timedelta(seconds=1)).isoformat())
    a = add(stores, 80)
    add(stores, 81, aliases=("vanilla",), contradicts=[a])
    assert stores[2].lookup("sweet tooth", guild_id=77, now=NOW + timedelta(seconds=2)) == []


def test_oversized_source_conflict_does_not_starve_independent_memory(stores):
    a = add(stores, 0, supports=[0, 1, 2])
    add(stores, 3, aliases=("vanilla",), supports=[3, 4, 5], contradicts=[a])
    wanted = add(stores, 99)
    assert [r["id"] for r in stores[2].lookup("sweet tooth", guild_id=77, now=NOW)] == [wanted]


def test_shared_sources_do_not_consume_budget_twice_or_change_storage(stores):
    for i in range(6):
        add(stores, i, supports=[0])
    graph = stores[2]
    before = graph.path.read_bytes()
    result = graph.lookup("sweet tooth", guild_id=77, now=NOW)
    assert len(result) == 4
    assert len({s["ref"]["message_id"] for r in result for s in r["supports"]}) == 1
    assert graph.path.read_bytes() == before


def test_more_matching_reviewed_concepts_break_specificity_tie(stores):
    for i in range(4):
        add(stores, i, aliases=("sweet tooth",))
    wanted = add(stores, 99, aliases=("sweet tooth",))
    graph = stores[2]
    from trubot.graph import _json

    with graph._transaction() as (db, _):
        db.execute(
            "INSERT INTO nodes VALUES (?, ?, ?)",
            ("concept:second", "concept", _json({"aliases": ["after dinner"]})),
        )
        db.execute(
            "INSERT INTO edges VALUES (?, ?, ?, ?)", (wanted, "about", "concept:second", "{}")
        )
    assert graph.lookup("sweet tooth after dinner", guild_id=77, now=NOW)[0]["id"] == wanted


def test_cycle_in_conflict_graph_keeps_every_side_once(stores):
    a = add(stores, 0)
    b = add(stores, 1, aliases=("vanilla",), contradicts=[a])
    c = add(stores, 2, aliases=("sorbet",), contradicts=[a, b])
    assert {r["id"] for r in stores[2].lookup("sweet tooth", guild_id=77, now=NOW)} == {a, b, c}
