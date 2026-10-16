"""Selected source pages reduce transport pressure without relaxing publication guards."""

import asyncio
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import discord
import pytest
from test_discord_client import fake_channel, fake_message, make_client
from test_ingestion import message
from test_learning import AUDIT, BASE, NOW, rows, source

from trubot.archives import ArchiveStore
from trubot.conversation import ReplyMode
from trubot.graph import GraphStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable
from trubot.memory import ContextMemory


@pytest.fixture
def setup(tmp_path):
    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    ArchiveStore.initialize(store)
    GraphStore.initialize(store)
    learner = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    learner.verified = True
    channel = fake_channel()
    selected = [message(channel, i, content=f"Baseball mascot proposal {i}.") for i in range(5)]
    for i, row in enumerate(selected):
        store.observe(source(i, content=row.content, created_at=row.created_at), now=NOW)
    requests = []

    async def history(**kwargs):
        requests.append(kwargs)
        for row in selected:
            yield row
        yield message(channel, 20, content="Unselected baseball opinion.")
        yield message(channel, 21, author=9, content="Peer context only.")

    channel.history = history
    channel.fetch_message = AsyncMock(side_effect=lambda identifier: selected[identifier - BASE])
    return store, learner, channel, selected, requests


async def test_real_handler_keeps_selected_packet_under_exact_read_pressure(setup):
    store, learner, channel, selected, requests = setup
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)
    elapsed, exact_reads = [0.0], []

    async def exact(_channel, identifier):
        exact_reads.append(identifier)
        elapsed[0] += 2
        # Five individual reads fit neither first nor final six-second packet.
        if len(exact_reads) > 3:
            raise TimeoutError
        return selected[identifier - BASE]

    async def reply(messages, **kwargs):
        packet = next(row.content for row in messages if row.origin == "memory")
        assert all(row.content in packet for row in selected)
        assert "Unselected baseball opinion" not in packet
        return "Selected-source validation passed."

    responder.reply = reply
    shim = SimpleNamespace(
        to_thread=asyncio.to_thread,
        wait_for=asyncio.wait_for,
        get_running_loop=lambda: SimpleNamespace(time=lambda: elapsed[0]),
    )
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch.object(learner, "refresh", side_effect=exact),
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch("trubot.discord_client.collect_native_episode", AsyncMock(return_value=None)),
        patch("trubot.discord_client.asyncio", shim),
    ):
        assert await client._respond(
            channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=1,
            anchor=fake_message(channel),
            target="Owner: Which baseball club do you support?",
        )
    assert not exact_reads
    assert len(requests) == 2
    assert all(r["limit"] == 100 and r["before"].id == BASE + 5 for r in requests)
    assert len(rows(store)) == 5
    channel.send.assert_awaited_once_with("Selected-source validation passed.")
    await client.close()


@pytest.mark.parametrize(
    "change", ["correction", "deletion", "denied", "unavailable", "withdrawal"]
)
async def test_real_handler_batch_revalidates_sources_before_posting(setup, change):
    store, learner, channel, selected, _ = setup
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)

    async def reply(messages, **kwargs):
        assert any(selected[0].content in row.content for row in messages)
        if change == "correction":
            selected[0].content = "Actually, forget the baseball mascot proposal."
            selected[0].edited_at = NOW
        elif change == "deletion":
            selected.clear()
            channel.fetch_message.side_effect = discord.NotFound(
                SimpleNamespace(status=404, reason="Gone"), "Gone"
            )
        elif change in {"denied", "unavailable"}:

            async def failed(**kwargs):
                if change == "denied":
                    raise discord.Forbidden(SimpleNamespace(status=403, reason="Denied"), "Denied")
                raise TimeoutError
                yield

            channel.history = failed
            channel.fetch_message.side_effect = TimeoutError
        else:
            store.forget(now=NOW)
        return "An obsolete draft."

    responder.reply = reply
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch("trubot.discord_client.collect_native_episode", AsyncMock(return_value=None)),
    ):
        assert not await client._respond(
            channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=1,
            anchor=fake_message(channel),
            target="Owner: Which baseball club do you support?",
        )
    channel.send.assert_not_awaited()
    if change == "denied":
        channel.fetch_message.assert_not_awaited()
    await client.close()


async def test_page_refresh_only_selected_sources_and_never_advances_cursor(setup):
    store, learner, channel, selected, requests = setup
    cursor = store.cursor(10, now=NOW)
    result = await learner.refresh_page(channel, [BASE, BASE + 2])
    assert set(result) == {BASE, BASE + 2}
    assert len(rows(store)) == 5
    assert store.cursor(10, now=NOW) == cursor
    assert requests[0]["before"].id == BASE + 3
    assert requests[0]["oldest_first"] is False
    channel.fetch_message.assert_not_awaited()
    assert selected[1].id not in result


@pytest.mark.parametrize(
    "case", ["unverified", "channel", "guild", "withdrawal", "too_many", "empty"]
)
async def test_page_refresh_scope_bounds_and_withdrawal_before_network(setup, case):
    store, learner, channel, _, requests = setup
    ids = [BASE, BASE + 1]
    if case == "unverified":
        learner.verified = False
    elif case == "channel":
        channel.id = 999
    elif case == "guild":
        channel.guild = SimpleNamespace(id=999)
    elif case == "withdrawal":
        store.forget(now=NOW)
    elif case == "too_many":
        ids = list(range(BASE, BASE + 6))
    else:
        ids = []
    if case in {"withdrawal", "too_many"}:
        with pytest.raises(LearningUnavailable):
            await learner.refresh_page(channel, ids)
    else:
        assert await learner.refresh_page(channel, ids) == {}
    assert not requests


@pytest.mark.parametrize("wrong", ["author", "bot", "webhook", "channel", "guild"])
async def test_selected_page_row_cannot_borrow_authenticated_attribution(setup, wrong):
    _, learner, channel, selected, _ = setup
    row = selected[0]
    if wrong == "author":
        row.author.id = 9
    elif wrong == "bot":
        row.author.bot = True
    elif wrong == "webhook":
        row.webhook_id = 1
    elif wrong == "channel":
        row.channel = SimpleNamespace(id=999)
    else:
        row.guild = SimpleNamespace(id=999)
    with pytest.raises(LearningUnavailable):
        await learner.refresh_page(channel, [BASE, BASE + 1])


@pytest.mark.parametrize("page_failure", [None, "timeout", "transient"])
async def test_missing_page_sources_use_exact_reads_without_losing_the_packet(setup, page_failure):
    store, learner, channel, selected, requests = setup
    client, _, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)

    async def partial(**kwargs):
        requests.append(kwargs)
        if page_failure == "timeout":
            raise TimeoutError
        if page_failure == "transient":
            raise discord.HTTPException(SimpleNamespace(status=503, reason="Unavailable"), "Retry")
        for row in selected[:2]:
            yield row

    channel.history = partial
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch("trubot.discord_client.collect_native_episode", AsyncMock(return_value=None)),
    ):
        packet = await client._memory_context(channel, "Owner: Which baseball club?", [])
    assert all(row.content in packet for row in selected)
    assert channel.fetch_message.await_count == (3 if page_failure is None else 5)
    assert len(rows(store)) == 5
    await client.close()


async def test_selected_page_identity_change_is_rejected_before_reads(setup):
    _, learner, channel, _, requests = setup
    learner.identity = replace(learner.identity, user_id=99)
    with pytest.raises(LearningUnavailable, match="identity changed"):
        await learner.refresh_page(channel, [BASE, BASE + 1])
    assert not requests


@pytest.mark.parametrize("mode", list(ReplyMode))
@pytest.mark.parametrize("empty_first", [True, False])
@pytest.mark.parametrize("quality_check", [True, False])
async def test_empty_native_setup_and_optional_timeout_keep_same_packet(
    setup, mode, empty_first, quality_check
):
    from trubot.native_context import NativeEpisode

    store, learner, channel, _, _ = setup
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)
    calls = 0
    reuse_checks = []

    async def collect(_channel, _identifier, **kwargs):
        nonlocal calls
        calls += 1
        # First source has stable actual setup; only source two has no setup.
        focus = kwargs["focus"]
        if calls % 2:
            return NativeEpisode(focus.content, None, ({"text": "Human setup only."},))
        if (calls <= 2) is empty_first:
            return NativeEpisode(focus.content, None, ())
        raise TimeoutError

    async def reply(messages, **kwargs):
        assert any("Human setup only." in row.content for row in messages)
        # The optional quality-reuse check must use the same publication rule.
        if quality_check:
            reuse_checks.append(await kwargs["refresh_check"]())
        return "A grounded answer."

    responder.reply = reply
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch("trubot.discord_client.collect_native_episode", side_effect=collect),
    ):
        assert await client._respond(
            channel,
            mode=mode,
            requester_user_id=1,
            anchor=fake_message(channel),
            target="Owner: Which baseball club do you support?",
        )
    channel.send.assert_awaited_once_with("A grounded answer.")
    assert reuse_checks == ([True] if quality_check else [])
    await client.close()


@pytest.mark.parametrize("change", ["appears", "removed", "edited", "media", "oversized", "link"])
async def test_substantive_native_context_changes_still_discard(setup, change):
    from trubot.native_context import NativeEpisode

    store, learner, channel, _, _ = setup
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning, client._memory = learner, ContextMemory(store)
    generated = False

    async def collect(_channel, _identifier, **kwargs):
        focus = kwargs["focus"]
        neighbors = ({"text": "Complete human setup.", "focus_replies_to_this": False},)
        gaps = ()
        if (change == "appears" and not generated) or (change == "removed" and generated):
            neighbors = ()
        elif change == "edited" and generated:
            neighbors = ({"text": "Corrected human setup."},)
        elif change in {"media", "oversized"}:
            neighbors = ()
            if generated:
                gaps = (
                    "source media pixels not retrieved"
                    if change == "media"
                    else "1 human context messages omitted for size",
                )
        elif change == "link" and generated:
            neighbors = ({"text": "Complete human setup.", "focus_replies_to_this": True},)
        return NativeEpisode(focus.content, None, neighbors, gaps)

    async def reply(messages, **kwargs):
        nonlocal generated
        generated = True
        return "An obsolete answer."

    responder.reply = reply
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch("trubot.discord_client.collect_native_episode", side_effect=collect),
    ):
        assert not await client._respond(
            channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=1,
            anchor=fake_message(channel),
            target="Owner: Which baseball club do you support?",
        )
    channel.send.assert_not_awaited()
    await client.close()
