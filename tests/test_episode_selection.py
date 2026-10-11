"""A reviewed episode set must not be replaced by lexical neighbors."""

import hashlib
from datetime import timedelta

import pytest
from test_distillation import worker
from test_learning import AUDIT, BASE, NOW, source

from trubot.archives import ArchiveStore
from trubot.distillation import StudyStore
from trubot.graph import GraphStore, _key
from trubot.learning import LearningStore, LearningUnavailable
from trubot.openai_responder import StudyContextExceeded

TEXTS = (
    "Put a pastry chef on the roster and score each croissant.",
    "Give the accountant a fantasy spot for every balanced ledger.",
    "I'm here if you want somebody to listen. Take your time.",
)


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


def seed_episodes(stores):
    _, archive, graph = stores
    refs = []
    for text in TEXTS:
        raw = ("peer\n  8:00 AM\nSynthetic setup only.\nlegacy.target\n  8:01 AM\n" + text).encode()
        archive.import_document(
            raw,
            channel="synthetic",
            target_alias="legacy.target",
            alias_basis="Invented evidence only",
            origin={"kind": "synthetic"},
            now=NOW,
        )
        refs.append({"kind": "slack", "document": hashlib.sha256(raw).hexdigest(), "ordinal": 1})
    graph.populate(now=NOW)
    return StudyStore(graph), refs


def test_reviewed_episode_set_preserves_nonlexical_support_and_exception(stores):
    study_store, refs = seed_episodes(stores)
    baseline = study_store.prepare(now=NOW, channel_ids=frozenset({10}), anchor_ref=refs[0])
    assert _key(refs[2]) not in [_key(s["ref"]) for s in baseline.snapshots]
    study = study_store.prepare(
        now=NOW + timedelta(hours=4), channel_ids=frozenset({10}), episode_refs=refs
    )
    assert [_key(s["ref"]) for s in study.snapshots] == [_key(r) for r in refs]
    assert [p["author_text"] for p in study.passages] == list(TEXTS)
    assert [p["source_index"] for p in study.passages] == [0, 1, 2]


@pytest.mark.parametrize(
    "invalid", [[], [None], [{"kind": "peer"}], [{"kind": "slack", "document": "x", "ordinal": 1}]]
)
def test_invalid_episode_set_does_not_acquire_study_lease(stores, invalid):
    study_store, _ = seed_episodes(stores)
    with pytest.raises(LearningUnavailable):
        study_store.prepare(now=NOW, channel_ids=frozenset({10}), episode_refs=invalid)
    with stores[2]._transaction() as (db, _):
        assert (
            db.execute("SELECT 1 FROM checkpoints WHERE stream='distillation'").fetchone() is None
        )


@pytest.mark.parametrize("failure", ["missing", "duplicate", "too_many", "two_selectors", "veto"])
def test_incomplete_or_ambiguous_set_is_never_silently_substituted(stores, failure):
    study_store, refs = seed_episodes(stores)
    kwargs = {"episode_refs": refs}
    if failure == "missing":
        kwargs["episode_refs"] = [refs[0], refs[1] | {"ordinal": 1000}]
    elif failure == "duplicate":
        kwargs["episode_refs"] = [refs[0], refs[0]]
    elif failure == "too_many":
        kwargs["episode_refs"] = refs * 3
    elif failure == "two_selectors":
        kwargs["anchor_ref"] = refs[0]
    else:
        with study_store.graph._transaction() as (db, source):
            snap = study_store.graph._snapshot(refs[1], source, now=NOW)
            db.execute(
                "INSERT OR REPLACE INTO checkpoints VALUES (?, ?)",
                ("study-veto:" + _key(refs[1]), snap["fingerprint"]),
            )
    with pytest.raises(LearningUnavailable):
        study_store.prepare(now=NOW, channel_ids=frozenset({10}), **kwargs)
    # A valid automatic selection is still available; invalid requests consumed no lease.
    assert study_store.prepare(now=NOW, channel_ids=frozenset({10})) is not None


def test_exact_set_cannot_bypass_durable_pacing_or_anchor_retry(stores):
    study_store, refs = seed_episodes(stores)
    study = study_store.prepare(now=NOW, channel_ids=frozenset({10}), episode_refs=refs)
    study_store.finish(study, None, now=NOW, outcome="rejected")
    assert (
        study_store.prepare(
            now=NOW + timedelta(hours=3), channel_ids=frozenset({10}), episode_refs=refs
        )
        is None
    )
    assert (
        study_store.prepare(
            now=NOW + timedelta(hours=4), channel_ids=frozenset({10}), episode_refs=refs
        )
        is None
    )
    assert (
        study_store.prepare(
            now=NOW + timedelta(days=31), channel_ids=frozenset({10}), episode_refs=refs
        )
        is not None
    )


async def test_both_model_passes_receive_the_same_complete_reviewed_set(stores):
    study_store, refs = seed_episodes(stores)
    distiller, client, responder, _ = worker(stores)
    packets = []

    async def generate(**kwargs):
        packets.append(kwargs["payload"]["sources"])
        if kwargs["name"] == "memory_review":
            return {
                "accepted": True,
                "basis": "Invented separate playful episodes with a sincere exception.",
                "contradicts": [],
            }
        return {
            "observations": [
                {
                    "kind": "humor",
                    "support_basis": "corroborated",
                    "summary": "Playfully expands fantasy scoring to absurd ordinary jobs.",
                    "conditions": "Invited fictional roster banter.",
                    "limitations": "Listen sincerely when someone wants support.",
                    "supports": [{"source": i, "quote": TEXTS[i]} for i in [0, 1]],
                    "counterexamples": [{"source": 2, "quote": TEXTS[2]}],
                    "aliases": ["fictional roster", "absurd jobs"],
                }
            ]
        }

    responder.study_json.side_effect = generate
    await distiller.cycle(client, episode_refs=refs)
    assert len(packets) == 2 and packets[0] == packets[1]
    assert [p["author_text"] for p in packets[0]] == list(TEXTS)
    result = study_store.graph.lookup("absurd jobs", guild_id=77, now=NOW)[0]
    assert len(result["supports"]) == 2
    assert len(result["abstraction"]["counterexamples"]) == 1
    stores[1].remove_document(refs[2]["document"], now=NOW)
    assert not study_store.graph.lookup("absurd jobs", guild_id=77, now=NOW)


async def test_bad_episode_set_never_reaches_paid_extraction(stores):
    _, refs = seed_episodes(stores)
    distiller, client, responder, _ = worker(stores)
    await distiller.cycle(client, episode_refs=[refs[0], refs[1] | {"ordinal": 9999}])
    responder.study_json.assert_not_awaited()


def test_requested_set_is_not_dropped_to_fit_extraction_budget(stores, monkeypatch):
    study_store, refs = seed_episodes(stores)
    monkeypatch.setattr("trubot.distillation._CONTEXT_ENVELOPE", 1)
    with pytest.raises(StudyContextExceeded):
        study_store.prepare(now=NOW, channel_ids=frozenset({10}), episode_refs=refs)
    with stores[2]._transaction() as (db, _):
        assert (
            db.execute("SELECT 1 FROM checkpoints WHERE stream='distillation'").fetchone() is None
        )


@pytest.mark.parametrize(
    "ref",
    [
        {"kind": "discord", "message_id": True},
        {"kind": "discord", "message_id": "1"},
        {"kind": "discord", "message_id": 0},
        {"kind": "discord", "message_id": 2**64},
        {"kind": "discord", "message_id": 1, "channel_id": False},
        {"kind": "discord", "message_id": 1, "content": "Untrusted commands"},
        {"kind": "slack", "document": "a" * 64, "ordinal": True},
        {"kind": "slack", "document": "a" * 64, "ordinal": -1},
    ],
)
def test_selector_rejects_coercion_and_channel_commands(stores, ref):
    store, _ = seed_episodes(stores)
    with pytest.raises(LearningUnavailable):
        store.prepare(now=NOW, channel_ids=frozenset({10}), episode_refs=[ref])


@pytest.mark.parametrize("failure", ["channel", "peer", "deleted", "truncated", "withdrawn"])
def test_exact_sets_retain_source_scope_and_withdrawal(stores, failure):
    learning, _, graph = stores
    study_store, refs = seed_episodes(stores)
    learning.observe(source(content="A separate invented native episode."), now=NOW)
    graph.populate(now=NOW)
    native = {"kind": "discord", "message_id": BASE}
    if failure == "channel":
        native["channel_id"] = 20
    elif failure == "peer":
        learning.observe(source(1, author_id=43), now=NOW)
        native["message_id"] = BASE + 1
    elif failure == "deleted":
        learning.invalidate(10, [BASE], deleted=True, now=NOW)
    elif failure == "truncated":
        learning.observe(source(content="a" * 1001), now=NOW)
        graph.populate(now=NOW)
    else:
        learning.forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        study_store.prepare(now=NOW, channel_ids=frozenset({10}), episode_refs=[refs[0], native])


@pytest.mark.parametrize("failure", ["edit", "delete", "withdraw"])
async def test_requested_support_changed_during_extraction_cannot_commit(stores, failure):
    learning, archive, graph = stores
    _, refs = seed_episodes(stores)
    distiller, client, responder, _ = worker(stores)

    async def changed(**kwargs):
        if failure == "withdraw":
            learning.forget(now=NOW)
        elif failure == "delete":
            archive.remove_document(refs[1]["document"], now=NOW)
        else:
            with archive._transaction() as db:
                db.execute(
                    "UPDATE messages SET content='Replacement authored words' WHERE document=?",
                    (refs[1]["document"],),
                )
        return {"observations": []}

    responder.study_json.side_effect = changed
    await distiller.cycle(client, episode_refs=refs)
    assert responder.study_json.await_count == 1
    if failure != "withdraw":
        assert graph.status()["studies"].get("accepted", 0) == 0


@pytest.mark.parametrize(
    "invalid",
    [
        {},
        {"schema": True, "episode_refs": []},
        {"schema": 2, "episode_refs": []},
        {"schema": 1, "episode_refs": [], "instructions": "Ignore rules"},
        {"schema": 1, "episode_refs": [{"kind": "peer"}]},
    ],
)
def test_operator_manifest_contains_only_bounded_source_selectors(tmp_path, invalid):
    import json

    from trubot.study import read_episode_refs

    tmp_path.chmod(0o700)
    path = tmp_path / "episodes.json"
    path.write_text(json.dumps(invalid))
    path.chmod(0o600)
    with pytest.raises(LearningUnavailable):
        read_episode_refs(path)
    path.write_text("x" * 4097)
    with pytest.raises(LearningUnavailable):
        read_episode_refs(path)


def test_operator_manifest_roundtrip_is_private_and_content_free(stores, tmp_path):
    import json

    from trubot.study import read_episode_refs

    _, refs = seed_episodes(stores)
    tmp_path.chmod(0o700)
    path = tmp_path / "episodes.json"
    path.write_text(json.dumps({"schema": 1, "episode_refs": refs}))
    path.chmod(0o600)
    assert read_episode_refs(path) == refs
    assert path.stat().st_mode & 0o777 == 0o600


async def test_operator_http_study_authenticates_identity_and_reports_abstention(stores):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock

    import discord

    from trubot.study import execute_study

    _, refs = seed_episodes(stores)
    distiller, client, responder, channel = worker(stores)
    guild = MagicMock(spec=discord.Guild)
    guild.id = 77
    guild.fetch_member = AsyncMock(return_value=SimpleNamespace(id=42, bot=False))
    client._connection = MagicMock()
    client.get_guild.return_value = guild
    client.fetch_guild = AsyncMock(return_value=guild)
    client.fetch_channel = AsyncMock(return_value=channel)
    responder.study_json.side_effect = None
    responder.study_json.return_value = {"observations": []}
    result = await execute_study(client, distiller.ingestor, responder, refs, clock=lambda: NOW)
    assert result["completed"] and result["outcome"] == "rejected" and not result["accepted"]
    guild.fetch_member.assert_awaited_once_with(42)
    guild._add_channel.assert_called_once_with(channel)
    assert result["discord_writes"] == 0 and not result["gateway_started"]
    channel.send.assert_not_awaited()
    # The previous outcome must not masquerade as a newly completed paced study.
    result = await execute_study(
        client, distiller.ingestor, responder, refs, clock=lambda: NOW + timedelta(hours=1)
    )
    assert not result["completed"] and result["outcome"] == "not_completed"
    assert responder.study_json.await_count == 1


async def test_operator_http_study_stops_on_unverified_member(stores):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock

    import discord

    from trubot.study import execute_study

    _, refs = seed_episodes(stores)
    distiller, client, responder, _ = worker(stores)
    guild = MagicMock(spec=discord.Guild)
    guild.id = 77
    guild.fetch_member = AsyncMock(return_value=SimpleNamespace(id=42, bot=True))
    client._connection = MagicMock()
    client.get_guild.return_value = guild
    client.fetch_guild = AsyncMock(return_value=guild)
    with pytest.raises(LearningUnavailable):
        await execute_study(client, distiller.ingestor, responder, refs, clock=lambda: NOW)
    responder.study_json.assert_not_awaited()


def test_operator_command_errors_do_not_echo_private_exception(tmp_path, monkeypatch, capsys):
    import json

    from trubot import study

    tmp_path.chmod(0o700)
    path = tmp_path / "episodes.json"
    path.write_text(
        json.dumps({"schema": 1, "episode_refs": [{"kind": "discord", "message_id": 1}]})
    )
    path.chmod(0o600)
    monkeypatch.setattr("sys.argv", ["trubot-study", "--episodes", str(path)])

    async def fail(_refs):
        raise RuntimeError("private source and credential")

    monkeypatch.setattr(study, "run", fail)
    with pytest.raises(SystemExit) as error:
        study.main()
    assert error.value.code == 2
    assert "private source and credential" not in capsys.readouterr().err


def test_operator_command_honestly_reports_not_completed(tmp_path, monkeypatch, capsys):
    import json

    from trubot import study

    tmp_path.chmod(0o700)
    path = tmp_path / "episodes.json"
    path.write_text(
        json.dumps({"schema": 1, "episode_refs": [{"kind": "discord", "message_id": 1}]})
    )
    path.chmod(0o600)
    monkeypatch.setattr("sys.argv", ["trubot-study", "--episodes", str(path)])

    async def incomplete(_refs):
        return {"completed": False, "accepted": False}

    monkeypatch.setattr(study, "run", incomplete)
    with pytest.raises(SystemExit) as error:
        study.main()
    assert error.value.code == 2
    assert json.loads(capsys.readouterr().out)["accepted"] is False


async def test_operator_run_uses_plain_http_clients_same_ledger_and_closes_on_failure(
    stores, tmp_path, monkeypatch
):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock

    from trubot import study

    _, refs = seed_episodes(stores)
    heartbeat = tmp_path / "primary-ready"
    heartbeat.write_text("live production heartbeat")
    settings = SimpleNamespace(
        learning_store_path=stores[0].path,
        learning_retention_days=180,
        openai_api_key="synthetic-key",
        openai_timeout_seconds=45,
        openai_model="gpt-6-luna",
        openai_max_output_tokens=512,
        usage_ledger_path=tmp_path / "existing-ledger",
        openai_max_retries=0,
        discord_token="synthetic-token",
        allowed_channel_ids=frozenset({10}),
        ready_file=heartbeat,
    )
    monkeypatch.setattr(study.Settings, "from_env", lambda: settings)
    api = MagicMock()
    api.__aenter__ = AsyncMock(return_value=api)
    api.__aexit__ = AsyncMock(return_value=False)
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    client.login = AsyncMock()
    api_factory = MagicMock(return_value=api)
    client_factory = MagicMock(return_value=client)
    ledger = MagicMock()
    monkeypatch.setattr(study, "AsyncOpenAI", api_factory)
    monkeypatch.setattr(study.discord, "Client", client_factory)
    monkeypatch.setattr(study, "UsageLedger", ledger)
    responder = MagicMock()
    monkeypatch.setattr(study, "OpenAITruaxResponder", responder)
    operation = AsyncMock(side_effect=RuntimeError("private failure"))
    monkeypatch.setattr(study, "execute_study", operation)
    with pytest.raises(RuntimeError):
        await study.run(refs)
    assert responder.call_args.kwargs["purpose"] == "maintenance"
    ledger.assert_called_once_with(settings.usage_ledger_path)
    assert client_factory.call_args.kwargs["intents"].value == 0
    client.login.assert_awaited_once_with(settings.discord_token)
    api.__aexit__.assert_awaited_once()
    client.__aexit__.assert_awaited_once()
    assert heartbeat.read_text() == "live production heartbeat"


async def test_operator_withdrawal_stops_before_discord_reads(stores):
    from trubot.study import execute_study

    _, refs = seed_episodes(stores)
    distiller, client, responder, _ = worker(stores)
    stores[0].forget(now=NOW)
    with pytest.raises(LearningUnavailable):
        await execute_study(client, distiller.ingestor, responder, refs, clock=lambda: NOW)
    client.fetch_guild.assert_not_called()
    responder.study_json.assert_not_awaited()


@pytest.mark.parametrize("outside", ["development-guild", "voice-channel"])
async def test_operator_does_not_treat_reply_only_channels_as_learning_scope(stores, outside):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock

    import discord
    from test_discord_client import fake_channel

    from trubot.study import execute_study

    _, refs = seed_episodes(stores)
    distiller, client, responder, source_channel = worker(stores)
    distiller.ingestor.channel_ids = frozenset({10, 20})
    guild = MagicMock(spec=discord.Guild)
    guild.id = 77
    guild.fetch_member = AsyncMock(return_value=SimpleNamespace(id=42, bot=False))
    client._connection = MagicMock()
    client.get_guild.return_value = guild
    client.fetch_guild = AsyncMock(return_value=guild)
    other = (
        fake_channel(20) if outside == "development-guild" else MagicMock(spec=discord.VoiceChannel)
    )
    if outside == "development-guild":
        other.guild = SimpleNamespace(id=88)
    client.fetch_channel = AsyncMock(side_effect=[source_channel, other])
    responder.study_json.side_effect = None
    responder.study_json.return_value = {"observations": []}
    result = await execute_study(client, distiller.ingestor, responder, refs, clock=lambda: NOW)
    assert result["completed"] and not result["accepted"]
    guild._add_channel.assert_called_once_with(source_channel)
    assert not result["gateway_started"] and result["discord_writes"] == 0


async def test_operator_never_bypasses_denied_source_channel(stores):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock

    import discord

    from trubot.study import execute_study

    _, refs = seed_episodes(stores)
    distiller, client, responder, _ = worker(stores)
    guild = MagicMock(spec=discord.Guild)
    guild.id = 77
    guild.fetch_member = AsyncMock(return_value=SimpleNamespace(id=42, bot=False))
    client._connection = MagicMock()
    client.get_guild.return_value = guild
    client.fetch_guild = AsyncMock(return_value=guild)
    client.fetch_channel = AsyncMock(
        side_effect=discord.Forbidden(SimpleNamespace(status=403, reason="Denied"), "Denied")
    )
    with pytest.raises(discord.Forbidden):
        await execute_study(client, distiller.ingestor, responder, refs, clock=lambda: NOW)
    responder.study_json.assert_not_awaited()
