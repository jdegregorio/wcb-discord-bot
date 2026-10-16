"""Shared concept growth keeps reviewed aliases attached to their current evidence."""

import json
from datetime import timedelta
from unittest.mock import patch

import pytest
from test_graph_selection import add
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def ids(graph, query, now=NOW):
    return {item["id"] for item in graph.lookup(query, guild_id=77, now=now)}


def test_shared_concept_keeps_both_aliases_and_neighbors_after_restart(stores):
    a = add(stores, 0, topic="shared", aliases=("glacier picnic",))
    assert ids(stores[2], "glacier picnic") == {a}
    b = add(stores, 1, topic="shared", aliases=("orbital picnic",))
    graph = GraphStore(stores[0])
    assert ids(graph, "glacier picnic") == {a, b}
    assert ids(graph, "orbital picnic") == {a, b}
    assert ids(graph, "orbital picnics") == set()


@pytest.mark.parametrize("change", ["replace", "retire", "delete", "edit", "expire"])
def test_alias_lifecycle_preserves_other_shared_concept_memories(stores, change):
    learning, _, graph = stores
    a = add(
        stores,
        0,
        topic="shared",
        aliases=("glacier picnic",),
        expires_at=(NOW + timedelta(seconds=1)).isoformat(),
    )
    b = add(stores, 1, topic="shared", aliases=("orbital picnic",))
    if change == "replace":
        add(stores, 0, topic="shared", aliases=("garden picnic",))
    elif change == "retire":
        graph.remove(a)
    elif change in {"delete", "edit"}:
        learning.invalidate(10, [source(0).id], deleted=change == "delete", now=NOW)
    when = NOW + timedelta(seconds=2) if change == "expire" else NOW
    assert ids(graph, "glacier picnic", when) == set()
    assert b in ids(graph, "orbital picnic", when)
    if change == "replace":
        assert ids(graph, "garden picnic", when) == {a, b}


def test_legacy_aliases_survive_new_relationship_without_rewriting_old_edges(stores):
    a = add(stores, 0, topic="shared", aliases=("glacier picnic",))
    graph = stores[2]
    with graph._transaction() as (db, _):
        row = db.execute(
            "SELECT evidence FROM edges WHERE origin=? AND relation='about'", (a,)
        ).fetchone()
        data = json.loads(row[0])
        data.pop("aliases", None)
        db.execute(
            "UPDATE edges SET evidence=? WHERE origin=? AND relation='about'", (json.dumps(data), a)
        )
        db.execute(
            "UPDATE nodes SET data=? WHERE id='concept:shared'",
            (json.dumps({"aliases": ["glacier picnic"]}),),
        )
    b = add(stores, 1, topic="shared", aliases=("orbital picnic",))
    assert ids(GraphStore(stores[0]), "glacier picnic") == {a, b}
    assert ids(graph, "orbital picnic") == {a, b}


def test_preview_and_rejected_rollout_cannot_remove_aliases(stores):
    from test_graph import observation

    a = add(stores, 0, topic="shared", aliases=("glacier picnic",))
    graph = stores[2]
    item = observation(
        {"kind": "discord", "message_id": source(0).id},
        id="new",
        entities=[{"kind": "concept", "id": "shared", "aliases": ["orbital picnic"]}],
    )
    graph.import_observations([item], now=NOW, dry_run=True)
    assert ids(graph, "glacier picnic") == {a}
    assert not ids(graph, "orbital picnic")
    with pytest.raises(LearningUnavailable):
        graph.import_observations(
            [item, item | {"id": "bad", "reviewed_by_operator": False}], now=NOW
        )
    assert ids(graph, "glacier picnic") == {a}
    assert not ids(graph, "orbital picnic")


def test_shared_concept_retains_complete_disagreement(stores):
    a = add(stores, 0, topic="shared", aliases=("glacier picnic",))
    b = add(stores, 1, topic="shared", aliases=("orbital picnic",), contradicts=[a])
    c = add(stores, 2, aliases=("garden picnic",), contradicts=[b])
    assert ids(stores[2], "glacier picnic") == {a, b, c}


def test_unavailable_alias_evidence_never_activates_current_neighbors(stores):
    a = add(stores, 0, topic="shared", aliases=("glacier picnic",))
    b = add(stores, 1, topic="shared", aliases=("orbital picnic",))
    graph = stores[2]
    validate = graph._valid
    with patch.object(
        graph,
        "_valid",
        side_effect=lambda data, *args, **kwargs: (
            False if data["summary"] == "alias source" else validate(data, *args, **kwargs)
        ),
    ):
        # Invalidate without sweep to exercise lookup's own source boundary.
        with graph._transaction() as (db, _):
            row = db.execute("SELECT data FROM nodes WHERE id=?", (a,)).fetchone()
            data = json.loads(row[0])
            data["summary"] = "alias source"
            db.execute("UPDATE nodes SET data=? WHERE id=?", (json.dumps(data), a))
        assert not ids(graph, "glacier picnic")
        assert b in ids(graph, "orbital picnic")


def test_shared_alias_freshness_work_stays_bounded(stores):
    for i in range(70):
        add(
            stores,
            i,
            topic="shared",
            aliases=("glacier picnic",),
            expires_at=(NOW + timedelta(seconds=1)).isoformat(),
        )
    graph = stores[2]
    with patch.object(graph, "_valid", wraps=graph._valid) as validate:
        assert not ids(graph, "glacier picnic", NOW + timedelta(seconds=2))
        assert validate.call_count <= 64


def test_expired_alias_owner_does_not_hide_another_current_owner(stores):
    a = add(
        stores,
        0,
        topic="shared",
        aliases=("glacier picnic",),
        expires_at=(NOW + timedelta(seconds=1)).isoformat(),
    )
    b = add(stores, 1, topic="shared", aliases=("glacier picnic",))
    assert ids(stores[2], "glacier picnic", NOW + timedelta(seconds=2)) == {b}
    assert a != b


@pytest.mark.parametrize("scope", ["wrong_guild", "withdrawn"])
def test_shared_concept_aliases_preserve_private_scope(stores, scope):
    add(stores, 0, topic="shared", aliases=("glacier picnic",))
    add(stores, 1, topic="shared", aliases=("orbital picnic",))
    if scope == "withdrawn":
        stores[0].forget(now=NOW)
        with pytest.raises(LearningUnavailable):
            ids(stores[2], "glacier picnic")
    else:
        assert stores[2].lookup("glacier picnic", guild_id=78, now=NOW) == []


@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_shared_concept_growth_reaches_handlers(stores, mode):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    from test_discord_client import fake_channel, fake_message, make_client

    from trubot.ingestion import MessageIngestor
    from trubot.memory import ContextMemory

    a = add(stores, 0, topic="shared", aliases=("glacier picnic",))
    b = add(stores, 1, topic="shared", aliases=("orbital picnic",))
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
    message.content = message.clean_content = ("🤖 " if mode == "direct" else "") + "glacier picnic"
    try:
        with (
            patch.object(client, "get_channel", return_value=channel),
            patch.object(ingestor, "refresh", new_callable=AsyncMock),
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
        assert a in context and b in context
        channel.send.assert_awaited_once()
    finally:
        await client.close()


def test_duplicate_concept_entries_cannot_silently_replace_aliases(stores):
    from test_graph import observation

    a = add(stores, 0, topic="shared", aliases=("glacier picnic",))
    graph = stores[2]
    item = observation(
        {"kind": "discord", "message_id": source(0).id},
        id="new",
        entities=[
            {"kind": "concept", "id": "shared", "aliases": ["orbital picnic"]},
            {"kind": "concept", "id": "shared", "aliases": ["garden picnic"]},
        ],
    )
    with pytest.raises(LearningUnavailable, match="Distinct observation concept"):
        graph.import_observations([item], now=NOW)
    assert ids(graph, "glacier picnic") == {a}
    assert not ids(graph, "orbital picnic")


@pytest.mark.parametrize("change", ["retire", "delete", "edit", "expire", "replace"])
def test_retired_alias_metadata_is_erased_from_a_shared_index(stores, change):
    a = add(
        stores,
        0,
        topic="shared",
        aliases=("SYNTHETIC_RETIRED_ALIAS",),
        expires_at=(NOW + timedelta(seconds=1)).isoformat(),
    )
    # Restore the exact old node/edge shape before adding a new relationship.
    graph = stores[2]
    with graph._transaction() as (db, _):
        row = db.execute(
            "SELECT evidence FROM edges WHERE origin=? AND relation='about'", (a,)
        ).fetchone()
        data = json.loads(row[0])
        data.pop("aliases", None)
        db.execute(
            "UPDATE edges SET evidence=? WHERE origin=? AND relation='about'", (json.dumps(data), a)
        )
        db.execute(
            "UPDATE nodes SET data=? WHERE id='concept:shared'",
            (
                json.dumps(
                    {"aliases": ["SYNTHETIC_RETIRED_ALIAS"], "source_times": ["SYNTHETIC_OLD_TIME"]}
                ),
            ),
        )
    b = add(stores, 1, topic="shared", aliases=("orbital picnic",))
    assert ids(graph, "SYNTHETIC_RETIRED_ALIAS") == {a, b}
    if change == "retire":
        graph.remove(a)
    elif change in {"delete", "edit"}:
        stores[0].invalidate(10, [source(0).id], deleted=change == "delete", now=NOW)
    elif change == "expire":
        graph.sweep(now=NOW + timedelta(seconds=2))
    else:
        add(stores, 0, topic="shared", aliases=("garden picnic",))
    with graph._transaction() as (db, _):
        data = db.execute("SELECT data FROM nodes WHERE id='concept:shared'").fetchone()[0]
    assert "SYNTHETIC_RETIRED_ALIAS" not in data
    assert "SYNTHETIC_OLD_TIME" not in data
    assert b in ids(graph, "orbital picnic")
