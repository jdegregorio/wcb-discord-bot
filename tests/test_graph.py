import json
import sqlite3
from datetime import timedelta
from unittest.mock import patch

import pytest
from test_learning import AUDIT, NOW, source

from trubot.archives import ArchiveStore
from trubot.graph import GraphStore, main
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    archive = ArchiveStore.initialize(learning)
    graph = GraphStore.initialize(learning)
    return learning, archive, graph


def observation(ref, **overrides):
    return {
        "id": "dessert",
        "kind": "preference",
        "summary": "A caramel dessert is supported, without claiming a permanent preference.",
        "status": "tentative",
        "confidence_basis": "One explicit first-person statement, synthetic source",
        "extraction_provenance": "Synthetic contextual review v1",
        "reviewed_by_operator": True,
        "supports": [ref],
        "entities": [{"id": "dessert", "kind": "concept", "aliases": ["sweet tooth", "dessert"]}],
        **overrides,
    }


def test_connected_recall_before_after_and_restart(stores):
    learning, _, graph = stores
    learning.observe(source(content="I order salted caramel after dinner."), now=NOW)
    memory = ContextMemory(learning)
    assert memory.candidates("Tell me about your sweet tooth", guild_id=77, now=NOW) == []
    ref = {"kind": "discord", "message_id": source().id}
    graph.import_observation(observation(ref), now=NOW)
    candidates = memory.candidates("Tell me about your sweet tooth", guild_id=77, now=NOW)
    assert len(candidates) == 1
    text = ContextMemory(learning).render(candidates, now=NOW, verified_after=NOW)
    assert "salted caramel" in text and "CONNECTED REVIEWED MEMORY" in text
    assert "tentative" in text
    assert not graph.lookup("sweet tooth", guild_id=78, now=NOW)
    assert graph.lookup("unrelated", guild_id=77, now=NOW) == []
    assert graph.lookup("sweet toothed", guild_id=77, now=NOW) == []
    assert memory.render(candidates, now=NOW, verified_after=NOW + timedelta(seconds=1)) == ""


def test_changes_erase_derived_data_and_backups_without_resurrecting(stores):
    learning, _, graph = stores
    learning.observe(source(content="salted caramel"), now=NOW)
    ref = {"kind": "discord", "message_id": source().id}
    graph.import_observation(observation(ref), now=NOW)
    candidates = ContextMemory(learning).candidates("dessert", guild_id=77, now=NOW)
    backups = learning.path.parent / "backups"
    backups.mkdir(mode=0o700)
    backup = backups / "memory-graph-old.sqlite3"
    backup.write_bytes(graph.path.read_bytes())
    backup.chmod(0o600)
    learning.invalidate(10, [source().id], deleted=False, now=NOW)
    assert not backup.exists()
    assert graph.status()["nodes"].get("preference", 0) == 0
    assert ContextMemory(learning).render(candidates, now=NOW) == ""
    learning.observe(source(content="I now prefer vanilla.", authoritative=True), now=NOW)
    assert not graph.lookup("dessert", guild_id=77, now=NOW)
    graph.import_observation(observation(ref), now=NOW)
    learning.observe(source(content="A corrected statement", authoritative=True), now=NOW)
    assert not graph.lookup("dessert", guild_id=77, now=NOW)
    graph.import_observation(observation(ref), now=NOW)
    learning.invalidate(10, [source().id], deleted=True, now=NOW)
    assert not graph.lookup("dessert", guild_id=77, now=NOW)


def test_slack_unknown_dates_peer_exclusion_and_suppression(stores):
    learning, archive, graph = stores
    raw = b"peer\n  8:00 AM\nI love vanilla.\nlegacy.target\n  8:01 AM\nSalted caramel for me."
    archive.import_document(
        raw,
        channel="general",
        target_alias="legacy.target",
        alias_basis="synthetic audit",
        origin={"kind": "synthetic"},
        now=NOW,
    )
    with archive._transaction() as db:
        digest = db.execute("SELECT digest FROM documents").fetchone()[0]
    ref = {"kind": "slack", "document": digest, "ordinal": 1}
    graph.import_observation(observation(ref), now=NOW)
    with pytest.raises(LearningUnavailable):
        graph.import_observation(observation(ref | {"ordinal": 0}), now=NOW)
    result = graph.lookup("sweet tooth", guild_id=77, now=NOW)
    assert result[0]["unknown_date"] and result[0]["source_times"] == [None]
    candidates = ContextMemory(learning).candidates("sweet tooth", guild_id=77, now=NOW)
    assert "peer (not persona evidence)" in ContextMemory(learning).render(candidates, now=NOW)
    archive.remove_document(digest, now=NOW)
    assert not graph.lookup("sweet tooth", guild_id=77, now=NOW)
    assert graph.status()["nodes"].get("preference", 0) == 0


def test_contradiction_neighborhood_and_expiry(stores):
    learning, _, graph = stores
    for i, text in enumerate(["I like caramel.", "I no longer like caramel."]):
        learning.observe(source(i, content=text), now=NOW)
    graph.import_observation(observation({"kind": "discord", "message_id": source().id}), now=NOW)
    graph.import_observation(
        observation(
            {"kind": "discord", "message_id": source(1).id},
            id="changed",
            contradicts=["dessert"],
            summary="Explicit later disagreement.",
            entities=[{"id": "change", "kind": "entity", "aliases": ["vanilla"]}],
        ),
        now=NOW,
    )
    items = graph.lookup("sweet tooth", guild_id=77, now=NOW)
    assert len(items) == 2 and all(i["status"] == "contested" for i in items)
    candidates = ContextMemory(learning).candidates("sweet tooth", guild_id=77, now=NOW)
    text = ContextMemory(learning).render(candidates, now=NOW)
    assert "I like caramel." in text and "I no longer like caramel." in text
    graph.import_observation(
        observation(
            {"kind": "discord", "message_id": source().id},
            id="expiring",
            expires_at=(NOW + timedelta(seconds=1)).isoformat(),
        ),
        now=NOW,
    )
    assert len(graph.lookup("dessert", guild_id=77, now=NOW + timedelta(seconds=2))) == 2
    graph.remove("observation:changed")
    assert len(graph.lookup("dessert", guild_id=77, now=NOW + timedelta(seconds=2))) == 1


def test_population_checkpoints_rollback_and_withdrawal(stores):
    learning, _, graph = stores
    for i in range(3):
        learning.observe(source(i, content=f"source {i}"), now=NOW)
    assert graph.populate(now=NOW, limit=1)["remaining"] == 2
    with (
        patch.object(GraphStore, "_bound", side_effect=LearningUnavailable("interrupted")),
        pytest.raises(LearningUnavailable),
    ):
        graph.populate(now=NOW, limit=1)
    assert GraphStore(learning).populate(now=NOW, limit=1)["remaining"] == 1
    assert graph.populate(now=NOW, limit=1)["remaining"] == 0
    assert graph.populate(now=NOW, limit=1)["processed"] == 0
    assert graph.status()["nodes"]["human_source"] == 3
    snapshot = graph.path.read_bytes()
    learning.forget(now=NOW)
    assert not graph.path.exists()
    graph.path.write_bytes(snapshot)
    graph.path.chmod(0o600)
    with pytest.raises(LearningUnavailable):
        graph.lookup("dessert", guild_id=77, now=NOW)
    with pytest.raises(LearningUnavailable):
        GraphStore.initialize(learning)


@pytest.mark.parametrize(
    "change",
    [
        {"kind": "invalid"},
        {"status": "unknown"},
        {"reviewed_by_operator": False},
        {"supports": []},
        {"summary": ""},
        {"expires_at": NOW.isoformat()},
        {"contradicts": ["missing"]},
        {"entities": [{"id": "a", "kind": "person", "aliases": ["alias"]}]},
        {"entities": [{"id": "a", "kind": "entity", "aliases": ["a"]}]},
    ],
)
def test_invalid_operator_inputs_are_atomic(stores, change):
    learning, _, graph = stores
    learning.observe(source(), now=NOW)
    before = graph.status()
    with pytest.raises(LearningUnavailable):
        graph.import_observation(
            observation({"kind": "discord", "message_id": source().id}, **change), now=NOW
        )
    assert graph.status() == before


def test_bounds_corrupt_state_and_unsupported_sources(stores):
    learning, _, graph = stores
    learning.observe(source(), now=NOW)
    for ref in [{"kind": "bot"}, {"kind": "discord", "message_id": 12}]:
        with pytest.raises(LearningUnavailable):
            graph.import_observation(observation(ref), now=NOW)
    ref = {"kind": "discord", "message_id": source().id}
    with pytest.raises(LearningUnavailable):
        graph.import_observation(observation(ref, supports=[ref, ref]), now=NOW)
    for limit in [0, 201]:
        with pytest.raises(LearningUnavailable):
            graph.populate(now=NOW, limit=limit)
    with patch("trubot.graph.MAX_NODES", 0), pytest.raises(LearningUnavailable):
        graph.populate(now=NOW)
    graph.path.chmod(0o644)
    with pytest.raises(LearningUnavailable):
        graph.status()
    graph.path.chmod(0o600)
    with sqlite3.connect(graph.path) as db:
        db.execute("PRAGMA user_version=999")
    with pytest.raises(LearningUnavailable):
        graph.status()
    assert not ContextMemory(learning).candidates("unknown", guild_id=77, now=NOW)


def test_content_free_cli(stores, monkeypatch, capsys, tmp_path):
    learning, _, _graph = stores
    learning.observe(source(), now=NOW)
    ref = {"kind": "discord", "message_id": source().id}
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"schema": 1, "observations": [observation(ref)]}))
    manifest.chmod(0o600)
    for command, extra in [
        ("populate", []),
        ("import", ["--manifest", str(manifest)]),
        ("status", []),
        ("remove", ["--id", "dessert"]),
        ("sweep", []),
    ]:
        with patch("trubot.graph.datetime") as clock:
            clock.now.return_value = NOW
            clock.fromisoformat.side_effect = __import__("datetime").datetime.fromisoformat
            monkeypatch.setattr(
                "sys.argv", ["trubot-graph", command, "--learning-path", str(learning.path), *extra]
            )
            main()
    assert "caramel" not in capsys.readouterr().out
    for command, extra in [("import", []), ("remove", []), ("populate", ["--limit", "201"])]:
        monkeypatch.setattr(
            "sys.argv", ["trubot-graph", command, "--learning-path", str(learning.path), *extra]
        )
        with pytest.raises(SystemExit) as error:
            main()
        assert error.value.code == 2


def test_visual_topology_is_lossless_and_does_not_establish_beliefs(stores):
    import hashlib
    import io

    from PIL import Image

    _learning, archive, graph = stores
    pixels = io.BytesIO()
    Image.new("RGB", (20, 20), "red").save(pixels, format="PNG")
    raw = pixels.getvalue()
    digest = hashlib.sha256(raw).hexdigest()
    episode = {
        "source": {"guild_id": 77, "channel_id": 10, "message_id": 123},
        "context": [
            {
                "id": "123",
                "author_id": "42",
                "bot": False,
                "webhook": False,
                "created_at": NOW.isoformat(),
                "content": "An image-dependent response",
            }
        ],
        "images": [{"digest": digest, "content_type": "image/png"}, {"status": "reference_only"}],
    }
    key = archive.import_visual_episode(episode, {digest: raw}, now=NOW)
    assert graph.populate(now=NOW)["visual_processed"] == 1
    assert graph.populate(now=NOW)["visual_processed"] == 0
    status = graph.status()
    assert status["nodes"]["visual"] == 1 and status["nodes"]["captured_human"] == 1
    assert archive.read_asset(digest) == raw
    assert graph.lookup("image", guild_id=77, now=NOW) == []
    with pytest.raises(LearningUnavailable):
        graph.import_observation(
            observation({"kind": "visual", "document": key, "ordinal": 0}), now=NOW
        )
    another = {
        **episode,
        "source": {**episode["source"], "message_id": 124},
        "context": episode["context"]
        + [
            {
                "id": "124",
                "author_id": "43",
                "bot": False,
                "webhook": False,
                "created_at": NOW.isoformat(),
                "content": "peer context",
            }
        ],
    }
    second = archive.import_visual_episode(another, {digest: raw}, now=NOW)
    with graph._transaction() as (db, _source):
        db.execute("DELETE FROM checkpoints WHERE stream='visuals'")
    graph.populate(now=NOW)
    archive.remove_visual_episode(key, now=NOW)
    assert graph.status()["nodes"]["visual"] == 1
    assert graph.status()["nodes"]["captured_human"] == 1
    archive.remove_visual_episode(second, now=NOW)
    assert graph.status()["nodes"].get("visual", 0) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["direct", "reaction", "followup"])
async def test_connected_memory_flows_through_discord_handlers(stores, mode):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    from test_discord_client import fake_channel, fake_message, make_client

    from trubot.conversation import ReplyMode
    from trubot.ingestion import MessageIngestor

    learning, _, graph = stores
    learning.observe(source(content="I order salted caramel after dinner."), now=NOW)
    graph.import_observation(observation({"kind": "discord", "message_id": source().id}), now=NOW)
    client, responder, _, _ = make_client(clock=lambda: NOW)
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning = ingestor
    client._memory = ContextMemory(learning)
    channel = fake_channel()

    async def history(**_kwargs):
        for message in []:
            yield message

    channel.history = history
    message = fake_message(channel, direct=mode == "direct")
    message.id = 123
    message.guild = channel.guild
    message.reference = None
    message.attachments, message.embeds = [], []
    message.content = message.clean_content = (
        "🤖 " if mode == "direct" else ""
    ) + "Tell me about your sweet tooth"
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
                        message_id=message.id,
                        emoji=SimpleNamespace(name="ThomasJones"),
                        member=SimpleNamespace(bot=False),
                    )
                )
            else:
                if mode == "followup":
                    client._attention.activate(10, NOW)
                await client.on_message(message)
        context, reply_mode, _, _ = responder.calls[0]
        assert (
            reply_mode
            == {
                "direct": ReplyMode.DIRECT,
                "reaction": ReplyMode.REACTION,
                "followup": ReplyMode.FOLLOW_UP,
            }[mode]
        )
        assert any(
            "CONNECTED REVIEWED MEMORY" in m.content and "salted caramel" in m.content
            for m in context
        )
        channel.send.assert_awaited_once()
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_operator_acceptance_captures_actual_generation_memory(stores, tmp_path, capsys):
    import importlib.util
    from pathlib import Path
    from unittest.mock import AsyncMock

    from test_discord_client import make_client

    from trubot.ingestion import MessageIngestor

    learning, _, graph = stores
    learning.observe(source(content="I order salted caramel after dinner."), now=NOW)
    graph.import_observation(observation({"kind": "discord", "message_id": source().id}), now=NOW)
    spec = importlib.util.spec_from_file_location(
        "graph_acceptance", Path(__file__).parents[1] / "scripts/evaluate_graph.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client, responder, _, _ = make_client(clock=lambda: NOW)
    responder.output = "Caramel."
    ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: NOW)
    client._learning = ingestor
    client._memory = ContextMemory(learning)
    expected = tmp_path / "expectations.json"
    expected.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "question": "Tell me about your sweet tooth",
                        "mode": mode,
                        "required_any": ["caramel"],
                    }
                    for mode in ["direct", "reaction", "followup"]
                ]
            }
        )
    )
    expected.chmod(0o600)
    row = {
        "id": str(source().id),
        "author": {"id": "42", "bot": False},
        "timestamp": source().created_at.isoformat(),
        "content": source(content="I order salted caramel after dinner.").content,
    }
    with (
        patch.object(module.Settings, "from_env", return_value=client._settings),
        patch.object(module, "build_client", return_value=client),
        patch.object(client, "login", new_callable=AsyncMock),
        patch.object(
            client.http,
            "get_member",
            new_callable=AsyncMock,
            return_value={"user": {"id": "42", "bot": False}},
        ),
        patch.object(client.http, "get_message", new_callable=AsyncMock, return_value=row) as fetch,
    ):
        await module.evaluate(expected, phase="installed")
    report = json.loads(capsys.readouterr().out)
    assert all(case["passed"] and case["graph_used"] for case in report["cases"])
    assert len(responder.calls) == 3
    # Every mode refetches its real native support. Reaction target interception
    # must not return the synthetic target when older evidence is requested.
    assert fetch.await_count == 3
    assert (tmp_path / "responses-installed.json").stat().st_mode & 0o777 == 0o600
