"""A reply cannot publish private memory after its source scope changes in flight."""

from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from test_authored_completeness import archived
from test_discord_client import fake_channel, fake_message, make_client
from test_learning import NOW

from trubot.conversation import ReplyMode
from trubot.ingestion import MessageIngestor
from trubot.memory import ContextMemory


@pytest.mark.parametrize("change", ["correction", "removal", "withdrawal"])
async def test_inflight_archived_source_change_discards_generated_reply(tmp_path, change):
    store, archive, _ = archived(tmp_path, "I support mascot reserve slots.")
    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._settings = replace(client._settings, development_guild_id=78)
    ingestor = MessageIngestor(store, frozenset({10}), clock=lambda: NOW)
    ingestor.verified = True
    client._learning, client._memory = ingestor, ContextMemory(store)
    channel = fake_channel()
    channel.guild = SimpleNamespace(id=78, owner_id=1)
    message = fake_message(channel)
    message.content = message.clean_content = "What did Andrew say about mascot reserve slots?"
    calls = []

    async def reply(messages, **kwargs):
        assert any("I support mascot reserve slots." in m.content for m in messages)
        calls.append(kwargs)
        if change == "correction":
            with archive._transaction() as db:
                db.execute("UPDATE messages SET content=? WHERE target=1", ("Keep mascots.",))
        elif change == "removal":
            ref = client._memory.candidates("mascot", guild_id=77, now=NOW)[0].source
            archive.remove_document(ref["document"], now=NOW)
        else:
            store.forget(now=NOW)
        return "I support mascot reserve slots."

    responder.reply = reply
    with patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])):
        result = await client._respond(
            channel,
            mode=ReplyMode.DIRECT,
            requester_user_id=1,
            anchor=message,
            target=message.content,
        )
    assert len(calls) == 1
    channel.send.assert_not_awaited()
    assert not result
    if change == "withdrawal":
        assert store.is_withdrawn()
    else:
        assert store.status()["messages"] == 0
    await client.close()


@pytest.mark.parametrize("mode", list(ReplyMode))
@pytest.mark.parametrize("state", ["changed", "unavailable", "closing", "current"])
async def test_final_memory_recheck_guards_every_reply_mode(mode, state):
    client, responder, _, _ = make_client(clock=lambda: NOW)
    channel = fake_channel()
    anchor = fake_message(channel)
    target = "A current question"
    responder.reply = AsyncMock(return_value="A supported answer")
    memory = AsyncMock(side_effect=["private source packet", "private source packet"])
    if state == "changed":
        memory.side_effect = ["private source packet", "different source packet"]
    elif state == "unavailable":
        memory.side_effect = ["private source packet", TimeoutError()]
    elif state == "closing":

        async def close_during_generation(*args, **kwargs):
            client._closing = True
            return "A supported answer"

        responder.reply.side_effect = close_during_generation
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "_memory_context", memory),
    ):
        result = await client._respond(
            channel, mode=mode, requester_user_id=1, anchor=anchor, target=target
        )
    responder.reply.assert_awaited_once()
    if state == "current":
        assert result
        channel.send.assert_awaited_once_with("A supported answer")
        assert memory.await_count == 2
    else:
        assert not result
        channel.send.assert_not_awaited()
    await client.close()


@pytest.mark.parametrize("reply", [None, "A fresh comic turn"])
async def test_abstention_and_no_memory_reply_need_no_extra_source_check(reply):
    client, responder, _, _ = make_client(clock=lambda: NOW)
    channel = fake_channel()
    responder.reply = AsyncMock(return_value=reply)
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "_memory_context", AsyncMock(return_value="")) as memory,
    ):
        result = await client._respond(
            channel, mode=ReplyMode.FOLLOW_UP, requester_user_id=1, target="A new setup"
        )
    assert memory.await_count == 1
    responder.reply.assert_awaited_once()
    assert result is (reply is not None)
    if reply:
        channel.send.assert_awaited_once_with(reply)
    else:
        channel.send.assert_not_awaited()
    await client.close()


async def test_same_source_packet_cannot_publish_under_a_changed_author_binding():
    from trubot.conversation import MemoryAuthorScope

    client, responder, _, _ = make_client(clock=lambda: NOW)
    client._learning = object()
    channel = fake_channel()
    responder.reply = AsyncMock(return_value="A source-attributed answer")
    with (
        patch("trubot.discord_client.collect_history", AsyncMock(return_value=[])),
        patch.object(client, "_memory_context", AsyncMock(return_value="same private packet")),
        patch.object(
            client,
            "_memory_author_scope",
            AsyncMock(
                side_effect=[MemoryAuthorScope.OTHER_AUTHOR, MemoryAuthorScope.SOURCE_AUTHOR]
            ),
        ),
    ):
        assert not await client._respond(
            channel, mode=ReplyMode.DIRECT, requester_user_id=1, target="A source question"
        )
    channel.send.assert_not_awaited()
    responder.reply.assert_awaited_once()
    client._learning = None
    await client.close()
