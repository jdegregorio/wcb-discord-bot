"""Reply setup must be linked explicitly and remain within current audit scope."""

from copy import copy
from types import SimpleNamespace
from unittest.mock import AsyncMock

import discord
import pytest
from test_character_audit import HUMAN

from trubot.character_audit import (
    AuditCase,
    AuditMessage,
    CharacterAuditUnavailable,
    audit_cases,
)

pytest_plugins = ["test_character_audit"]


def prepare(i):
    for row in i.rows:
        row.id += 10
    target = copy(i.rows[0])
    target.id, target.content = 1, "Complete distant fictional question."
    target.author = SimpleNamespace(id=7, bot=False)
    i.rows[1].reference = discord.MessageReference(
        message_id=1, channel_id=i.channel.id, guild_id=i.guild.id
    )
    i.channel.fetch_message.side_effect = lambda identifier: next(
        row for row in [target, *i.rows] if row.id == identifier
    )
    return target


def payload(i):
    return i.responder.study_json.call_args.kwargs["payload"]["cases"]["case_1"]


async def test_distant_target_is_retained_once_with_anonymous_explicit_link(inspection):
    i = inspection
    target = prepare(i)
    receipt = await i.call()
    case = payload(i)
    assert [row["text"] for row in case["messages"]] == [
        target.content,
        *[row.content for row in i.rows],
    ]
    assert case["focus"] == 2
    assert case["messages"][2]["reply_to"] == 0
    assert case["messages"][0]["role"] == "peer"
    assert receipt["reply_context_counts"] == {"case_1": {"linked": 1, "gaps": 0}}
    assert target.content not in str(receipt)
    assert "guild_id" not in str(case) and "message_id" not in str(case)
    i.channel.send.assert_not_called()


async def test_already_present_target_is_linked_without_duplicate_or_extra_initial_read(inspection):
    i = inspection
    prepare(i)
    i.rows[1].reference.message_id = i.rows[0].id
    await i.call()
    case = payload(i)
    assert len(case["messages"]) == 3 and case["messages"][1]["reply_to"] == 0
    assert i.channel.fetch_message.await_count == 6


@pytest.mark.parametrize("fault", ["channel", "guild", "missing_channel", "forward"])
async def test_foreign_or_forwarded_reference_never_fetches_target(inspection, fault):
    i = inspection
    prepare(i)
    ref = i.rows[1].reference
    if fault == "channel":
        ref.channel_id = 999
    elif fault == "guild":
        ref.guild_id = 999
    elif fault == "missing_channel":
        ref.channel_id = None
    else:
        ref.type = discord.MessageReferenceType.forward
    await i.call()
    case = payload(i)
    assert len(case["messages"]) == 3
    assert case["messages"][1]["reply_gap"] in {"outside_scope", "unsupported_reference"}
    assert all(call.args != (1,) for call in i.channel.fetch_message.await_args_list)


@pytest.mark.parametrize("error", [discord.NotFound, discord.Forbidden])
async def test_unavailable_target_is_an_explicit_gap_without_retry(inspection, error):
    i = inspection
    prepare(i)
    original = i.channel.fetch_message.side_effect

    def read(identifier):
        if identifier == 1:
            raise error(SimpleNamespace(status=404, reason="Unavailable"), "PRIVATE_SENTINEL")
        return original(identifier)

    i.channel.fetch_message.side_effect = read
    receipt = await i.call()
    assert payload(i)["messages"][1]["reply_gap"] == "unavailable"
    assert receipt["reply_context_counts"]["case_1"]["gaps"] == 1
    assert sum(call.args == (1,) for call in i.channel.fetch_message.await_args_list) == 1
    assert "PRIVATE_SENTINEL" not in str(receipt)


async def test_added_target_does_not_recursively_fetch_its_own_reference(inspection):
    i = inspection
    target = prepare(i)
    target.reference = discord.MessageReference(message_id=9, channel_id=10, guild_id=88)
    await i.call()
    assert payload(i)["messages"][0]["reply_gap"] == "not_expanded"
    assert all(call.args != (9,) for call in i.channel.fetch_message.await_args_list)


@pytest.mark.parametrize("fault", ["wrong_id", "wrong_channel", "wrong_guild", "oversize"])
async def test_incomplete_or_foreign_target_stops_before_provider(inspection, fault):
    i = inspection
    target = prepare(i)
    if fault == "oversize":
        target.content = "x" * 6001
    elif fault == "wrong_id":
        target.id = 9
        original = i.channel.fetch_message.side_effect
        i.channel.fetch_message.side_effect = lambda n: target if n == 1 else original(n)
    else:
        name = "channel" if fault == "wrong_channel" else "guild"
        value = copy(getattr(target, name))
        value.id = 999
        setattr(target, name, value)
    with pytest.raises(CharacterAuditUnavailable):
        await i.call()
    i.responder.study_json.assert_not_awaited()


@pytest.mark.parametrize("stage", ["before", "after"])
@pytest.mark.parametrize("fault", ["text", "deleted", "reference_channel", "reference_guild"])
async def test_linked_context_is_fresh_at_both_provider_boundaries(inspection, stage, fault):
    i = inspection
    prepare(i)
    original = i.channel.fetch_message.side_effect
    calls = 0

    def read(identifier):
        nonlocal calls
        row = original(identifier)
        if identifier == 1:
            calls += 1
            if calls == (2 if stage == "before" else 3):
                if fault == "deleted":
                    raise discord.NotFound(SimpleNamespace(status=404, reason="Deleted"), "private")
                if fault == "text":
                    row = copy(row)
                    row.content += " edited"
        if (
            identifier == 12
            and fault.startswith("reference_")
            and calls >= (2 if stage == "before" else 3)
        ):
            row = copy(row)
            row.reference = copy(row.reference)
            setattr(row.reference, fault.removeprefix("reference_") + "_id", 999)
        return row

    i.channel.fetch_message.side_effect = read
    with pytest.raises(CharacterAuditUnavailable):
        await i.call()
    assert i.responder.study_json.await_count == (0 if stage == "before" else 1)


@pytest.mark.parametrize(
    "link,gap", [(True, None), (2, None), (0, None), (None, "invented"), (1, "unavailable")]
)
async def test_invalid_anonymous_link_metadata_stops_before_provider(link, gap):
    responder = AsyncMock()
    with pytest.raises(CharacterAuditUnavailable):
        await audit_cases(
            responder,
            (AuditCase((AuditMessage("bot", "Hi", reply_to=link, reply_gap=gap),), 0, True),),
            HUMAN,
            source_check=AsyncMock(),
        )
    responder.study_json.assert_not_awaited()


async def test_four_original_rows_allow_at_most_four_distinct_one_hop_reads(inspection):
    from trubot.character_audit import _reply_context

    i = inspection
    originals, targets = [], []
    for n in range(4):
        source, target = copy(i.rows[1]), copy(i.rows[0])
        source.id, target.id = 100 + n, 1 + n
        source.reference = discord.MessageReference(
            message_id=target.id, channel_id=10, guild_id=88
        )
        target.reference = discord.MessageReference(message_id=90 + n, channel_id=10, guild_id=88)
        originals.append(source)
        targets.append(target)
    i.channel.fetch_message.side_effect = lambda identifier: next(
        row for row in targets if row.id == identifier
    )
    rows, links = await _reply_context(i.channel, originals)
    assert len(rows) == 8 and i.channel.fetch_message.await_count == 4
    assert sum(isinstance(value, int) for value in links.values()) == 4
    assert sum(value == "not_expanded" for value in links.values()) == 4


async def test_shared_unavailable_target_is_fetched_only_once(inspection):
    from trubot.character_audit import _reply_context

    i = inspection
    prepare(i)
    i.rows[2].reference = i.rows[1].reference
    original = i.channel.fetch_message.side_effect

    def read(identifier):
        if identifier == 1:
            raise discord.Forbidden(SimpleNamespace(status=403, reason="Denied"), "private")
        return original(identifier)

    i.channel.fetch_message.side_effect = read
    _, links = await _reply_context(i.channel, i.rows)
    assert links == {12: "unavailable", 13: "unavailable"}
    i.channel.fetch_message.assert_awaited_once_with(1)


async def test_explicit_focus_selection_includes_linked_setup(inspection):
    i = inspection
    prepare(i)
    i.kwargs["focus_message_ids"] = (12,)

    async def history(**kwargs):
        assert kwargs["limit"] == 5 and kwargs["around"].id == 12
        for row in reversed(i.rows):
            yield row

    i.channel.history = history
    receipt = await i.call()
    assert receipt["selection"] == "explicit_bot_turns"
    assert payload(i)["messages"][payload(i)["focus"]]["reply_to"] == 0


async def test_ordinary_no_reference_payload_remains_compatible(inspection):
    i = inspection
    receipt = await i.call()
    assert receipt["reply_context_counts"] == {"case_1": {"linked": 0, "gaps": 0}}
    assert all(set(row) == {"role", "text", "pixels_unavailable"} for row in payload(i)["messages"])


async def test_target_transport_error_is_sanitized_without_provider(inspection):
    i = inspection
    prepare(i)
    i.channel.fetch_message.side_effect = RuntimeError("PRIVATE_SENTINEL")
    with pytest.raises(CharacterAuditUnavailable, match="Audit reply target unavailable") as error:
        await i.call()
    assert "PRIVATE_SENTINEL" not in str(error.value) and error.value.__suppress_context__
    i.responder.study_json.assert_not_awaited()
