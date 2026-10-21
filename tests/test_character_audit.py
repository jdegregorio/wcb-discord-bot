"""Review validity is independent of a model's schema compliance or aggregate counts."""

from unittest.mock import AsyncMock

import pytest

from trubot.character_audit import (
    FLAGS,
    AuditCase,
    AuditMessage,
    CharacterAuditUnavailable,
    audit_cases,
)

CASES = (
    AuditCase(
        (AuditMessage("operator", "Pretend we won."), AuditMessage("bot", "We did it!")), 1, True
    ),
    AuditCase((AuditMessage("bot", "An old joke."), AuditMessage("bot", "An old joke.")), 1, False),
)
HUMAN = ((AuditMessage("peer", "A pretend victory."), AuditMessage("source_human", "Nice!")),)


def review():
    return {f"case_{i}": dict.fromkeys(FLAGS, False) for i in (1, 2)}


async def test_complete_cases_preserve_flags_and_derive_counts_without_raw_text():
    value = review()
    value["case_2"]["unhelpful_repetition"] = True
    value["case_2"]["evidence_limited"] = True
    responder, check = AsyncMock(), AsyncMock()
    responder.study_json.return_value = value
    report = await audit_cases(responder, CASES, HUMAN, source_check=check)
    receipt = report.receipt()
    assert receipt["reviewed_cases"] == 2
    assert receipt["counts"]["unhelpful_repetition"] == 1
    assert receipt["counts"]["evidence_limited"] == 1
    assert receipt["cases"] == value
    assert receipt["human_episodes"] == 1
    assert receipt["general_fidelity_qualified"] is False
    assert receipt["raw_retained"] is False
    assert "old joke" not in str(receipt) and "Pretend" not in repr(CASES)
    assert check.await_count == 2
    request = responder.study_json.call_args.kwargs
    assert request["source_check"] is check
    assert request["payload"]["cases"]["case_2"]["focus"] == 1
    assert request["payload"]["cases"]["case_1"]["development"] is True
    assert request["schema"]["required"] == ["case_1", "case_2"]
    assert "counts" not in request["schema"]["properties"]


@pytest.mark.parametrize(
    "bad", ["aggregate", "missing", "unknown", "extra", "integer", "string", "null", "list"]
)
async def test_malformed_review_is_rejected_without_partial_receipt(bad):
    value = review()
    if bad == "aggregate":
        value = {"sampled_bot_posts": 1, "peculiar_posts": 0}
    elif bad == "missing":
        del value["case_2"]
    elif bad == "unknown":
        value["case_3"] = value.pop("case_2")
    elif bad == "extra":
        value["case_2"]["private_excerpt"] = "PRIVATE_SENTINEL"
    elif bad == "list":
        value["case_2"] = []
    else:
        value["case_2"]["peculiar_voice"] = {"integer": 1, "string": "false", "null": None}[bad]
    responder = AsyncMock()
    responder.study_json.return_value = value
    with pytest.raises(CharacterAuditUnavailable) as error:
        await audit_cases(responder, CASES, HUMAN, source_check=AsyncMock())
    assert "PRIVATE_SENTINEL" not in str(error.value)


@pytest.mark.parametrize("stage", ["before", "provider", "after"])
async def test_source_and_provider_failures_are_sanitized_and_never_return_reviews(stage):
    responder, check = AsyncMock(), AsyncMock()
    responder.study_json.return_value = review()
    if stage == "provider":
        responder.study_json.side_effect = RuntimeError("PRIVATE_SENTINEL")
    else:
        check.side_effect = (
            [RuntimeError("PRIVATE_SENTINEL")]
            if stage == "before"
            else [None, RuntimeError("PRIVATE_SENTINEL")]
        )
    with pytest.raises(CharacterAuditUnavailable) as error:
        await audit_cases(responder, CASES, HUMAN, source_check=check)
    assert "PRIVATE_SENTINEL" not in str(error.value)
    assert error.value.__suppress_context__
    assert responder.study_json.await_count == (0 if stage == "before" else 1)


@pytest.mark.parametrize(
    "change",
    [
        "zero",
        "nine",
        "no_human",
        "seven_human",
        "peer_only",
        "bad_focus",
        "negative",
        "bool_focus",
        "human_focus",
        "empty",
        "oversize",
        "aggregate_oversize",
        "bad_role",
        "media_type",
        "development_type",
    ],
)
async def test_incomplete_or_unbounded_inputs_stop_before_provider(change):
    cases, human = CASES, HUMAN
    if change == "zero":
        cases = ()
    elif change == "nine":
        cases = CASES * 4 + CASES[:1]
    elif change == "no_human":
        human = ()
    elif change == "seven_human":
        human = HUMAN * 7
    elif change == "peer_only":
        human = ((AuditMessage("peer", "No authored support."),),)
    elif change in {"bad_focus", "negative", "bool_focus", "human_focus", "development_type"}:
        cases = (
            AuditCase(
                CASES[0].messages,
                {"bad_focus": 3, "negative": -1, "bool_focus": True, "human_focus": 0}.get(
                    change, 1
                ),
                "yes" if change == "development_type" else True,
            ),
        )
    elif change == "aggregate_oversize":
        human = ((AuditMessage("source_human", "x" * 6000),) * 3,)
    else:
        message = AuditMessage(
            "untrusted" if change == "bad_role" else "bot",
            "" if change == "empty" else "x" * (6001 if change == "oversize" else 2),
            "unknown" if change == "media_type" else False,
        )
        cases = (AuditCase((message,), 0, True),)
    responder, check = AsyncMock(), AsyncMock()
    with pytest.raises(CharacterAuditUnavailable):
        await audit_cases(responder, cases, human, source_check=check)
    responder.study_json.assert_not_awaited()
    check.assert_not_awaited()


async def test_complete_unicode_media_gaps_and_multiple_context_roles_survive_unchanged():
    text = "Complete text 😄 with an ending that qualifies the beginning."
    cases = (
        AuditCase(
            (AuditMessage("other_bot", "Earlier bot context"), AuditMessage("bot", text, True)),
            1,
            True,
        ),
    )
    responder = AsyncMock()
    responder.study_json.return_value = {"case_1": dict.fromkeys(FLAGS, False)}
    await audit_cases(responder, cases, HUMAN, source_check=AsyncMock())
    row = responder.study_json.call_args.kwargs["payload"]["cases"]["case_1"]["messages"][1]
    assert row == {"role": "bot", "text": text, "pixels_unavailable": True}


@pytest.fixture
def inspection():
    from types import SimpleNamespace
    from unittest.mock import MagicMock, patch

    import discord

    from trubot.character_audit import inspect_channel

    identity = SimpleNamespace(guild_id=77, user_id=42)
    ingestor = SimpleNamespace(
        identity=identity,
        store=MagicMock(),
        verify_member=AsyncMock(),
        accepts=lambda ch: ch.guild.id == 77,
    )
    ingestor.store.identity.return_value = identity
    client = MagicMock()
    client.user.id = 999
    guild = MagicMock()
    guild.id, guild.owner_id, guild.approximate_member_count = 88, 1, 2

    async def member(identifier):
        return SimpleNamespace(id=identifier, bot=identifier == 999)

    guild.fetch_member = AsyncMock(side_effect=member)
    client.fetch_guild = AsyncMock(return_value=guild)
    channel = MagicMock(spec=discord.TextChannel)
    channel.id, channel.guild = 10, guild
    channel.permissions_for.return_value = SimpleNamespace(
        view_channel=True, read_message_history=True
    )
    client.fetch_channel = AsyncMock(return_value=channel)
    guild.fetch_channel = AsyncMock(return_value=channel)

    def message(identifier, author, bot, content):
        return SimpleNamespace(
            id=identifier,
            guild=guild,
            author=SimpleNamespace(id=author, bot=bot),
            content=content,
            webhook_id=None,
            edited_at=None,
            reference=None,
            attachments=[],
            embeds=[],
        )

    rows = [
        message(1, 1, False, "Pretend we won."),
        message(2, 999, True, "We did it!"),
        message(3, 42, False, "A peer here, not source evidence."),
    ]

    async def history(**kwargs):
        assert kwargs == {"limit": 40}
        for row in reversed(rows):
            yield row

    channel.history = history
    channel.fetch_message = AsyncMock(
        side_effect=lambda identifier: next(row for row in rows if row.id == identifier)
    )
    archive = MagicMock()
    archive.context.return_value = [
        {
            "ordinal": 1,
            "target": True,
            "voice_eligible": True,
            "kind": "message",
            "content": "A source-authored sentence.",
            "flags": "[]",
        }
    ]
    responder = AsyncMock()
    responder.study_json.return_value = {"case_1": dict.fromkeys(FLAGS, False)}
    kwargs = dict(
        channel_id=10,
        development_guild_id=88,
        allowed_channel_ids=frozenset({10}),
        refs=[{"kind": "slack", "document": "a" * 64, "ordinal": 1}],
    )
    with patch("trubot.character_audit.ArchiveStore", return_value=archive):
        yield SimpleNamespace(
            call=lambda: inspect_channel(client, ingestor, responder, **kwargs),
            client=client,
            ingestor=ingestor,
            channel=channel,
            guild=guild,
            rows=rows,
            archive=archive,
            responder=responder,
            kwargs=kwargs,
        )


async def test_authenticated_inspection_maps_every_case_privately_without_readiness_or_writes(
    inspection,
):
    i = inspection
    receipt = await i.call()
    assert receipt["reviewed_cases"] == 1
    assert receipt["message_refs"] == {"case_1": {"channel_id": 10, "message_id": 2}}
    assert receipt["gateway_started"] is False and receipt["discord_writes"] == 0
    assert i.ingestor.verify_member.await_count == 3
    payload = i.responder.study_json.call_args.kwargs["payload"]
    assert [x["role"] for x in payload["cases"]["case_1"]["messages"]] == [
        "operator",
        "bot",
        "peer",
    ]
    assert "A source-authored" not in str(receipt) and "We did it" not in str(receipt)
    i.channel.send.assert_not_called()
    i.client.start.assert_not_called()
    i.client.connect.assert_not_called()
    assert i.channel.fetch_message.await_count == 6


@pytest.mark.parametrize(
    "fault",
    [
        "allowlist",
        "wrong_guild",
        "membership",
        "owner_missing",
        "owner_bot",
        "permission",
        "anchor",
        "source_changed",
        "message_changed",
        "withdrawal",
        "native_ref",
        "no_bot",
        "limit",
    ],
)
async def test_inspection_scope_and_freshness_fail_closed(inspection, fault):
    from types import SimpleNamespace

    i = inspection
    if fault == "allowlist":
        i.kwargs["allowed_channel_ids"] = frozenset()
    elif fault == "wrong_guild":
        i.guild.id = 90
    elif fault == "membership":
        i.guild.approximate_member_count = 3
    elif fault == "owner_missing":
        i.guild.owner_id = None
    elif fault == "owner_bot":
        i.guild.owner_id = 999
    elif fault == "permission":
        i.channel.permissions_for.return_value.read_message_history = False
    elif fault == "anchor":
        i.archive.context.return_value[0]["target"] = False
    elif fault == "source_changed":
        original = i.archive.context.return_value
        i.archive.context.side_effect = [original, []]
    elif fault == "message_changed":
        i.channel.fetch_message.side_effect = lambda identifier: SimpleNamespace(
            content="Changed",
            author=SimpleNamespace(id=1, bot=False),
            webhook_id=None,
            edited_at=None,
            reference=None,
            attachments=[],
            embeds=[],
        )
    elif fault == "withdrawal":
        i.ingestor.store.identity.return_value = None
    elif fault == "native_ref":
        i.kwargs["refs"] = [{"kind": "discord", "message_id": 2}]
    elif fault == "no_bot":
        i.rows[1].author.id = 3
    else:
        i.kwargs["limit"] = 5
    with pytest.raises((CharacterAuditUnavailable, RuntimeError)):
        await i.call()
    i.responder.study_json.assert_not_awaited()


async def test_changed_private_membership_after_provider_discards_whole_review(inspection):
    from copy import copy

    i = inspection
    expanded = copy(i.guild)
    expanded.approximate_member_count = 3
    i.client.fetch_guild.side_effect = [i.guild, i.guild, i.guild, expanded]
    with pytest.raises(CharacterAuditUnavailable):
        await i.call()
    i.responder.study_json.assert_awaited_once()


async def test_source_channel_human_roles_and_visual_gaps_are_explicit(inspection):
    i = inspection
    i.guild.id = 77
    i.rows[2].attachments = [
        type("Attachment", (), {"id": 7, "url": "https://example.test/image", "size": 12})()
    ]
    receipt = await i.call()
    assert receipt["reviewed_cases"] == 1
    payload = i.responder.study_json.call_args.kwargs["payload"]
    rows = payload["cases"]["case_1"]["messages"]
    assert rows[-1]["role"] == "source_human"
    assert rows[-1]["pixels_unavailable"] is True
    assert payload["cases"]["case_1"]["development"] is False


async def test_private_permissions_use_full_authenticated_guild_roles(inspection):
    from unittest.mock import MagicMock

    import discord

    i = inspection
    partial = MagicMock(spec=discord.TextChannel)
    partial.id, partial.guild = i.channel.id, i.guild
    partial.permissions_for.return_value.view_channel = False
    i.client.fetch_channel.return_value = partial
    receipt = await i.call()
    assert receipt["reviewed_cases"] == 1
    i.guild.fetch_channel.assert_awaited_once_with(10)
    partial.history.assert_not_called()
