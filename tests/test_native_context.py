from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from test_learning import NOW

from trubot.learning import Identity
from trubot.native_context import collect_native_episode

IDENTITY = Identity(42, 77, frozenset({10}))


def message(channel, message_id=100, *, text="Yep.", author=42, **kwargs):
    values = dict(
        id=message_id,
        channel=channel,
        guild=channel.guild,
        author=SimpleNamespace(id=author, bot=False),
        webhook_id=None,
        created_at=kwargs.get("created_at", NOW - timedelta(minutes=5)),
        edited_at=None,
        content=text,
        reference=None,
        attachments=[],
        embeds=[],
    )
    values.update(kwargs)
    return SimpleNamespace(**values)


def channel_with(*, rows=(), reference=None):
    channel = MagicMock(spec=discord.TextChannel)
    channel.id, channel.guild = 10, SimpleNamespace(id=77)
    focus = message(channel, reference=reference)
    channel.fetch_message = AsyncMock(return_value=focus)
    channel.reads = []

    async def history(**kwargs):
        channel.reads.append(kwargs)
        for row in rows:
            yield row

    channel.history = history
    return channel, focus


async def collect(channel):
    return await collect_native_episode(
        channel, 100, identity=IDENTITY, now=NOW, retention_days=180
    )


async def test_native_context_preserves_setup_roles_links_and_media_gaps():
    channel, focus = channel_with()
    focus.reference = discord.MessageReference(message_id=99, channel_id=10, guild_id=77)
    before = message(channel, 99, author=9, text="Keep the current rule?", attachments=[object()])
    after = message(channel, 101, author=8, text="Agreed.")

    async def history(**kwargs):
        assert kwargs["limit"] == 5
        assert kwargs["around"].id == 100
        for row in [after, focus, before]:
            yield row

    channel.history = history
    episode = await collect(channel)
    assert episode.matches("Yep.", None)
    assert [r["position"] for r in episode.neighbors] == ["before", "after"]
    assert episode.neighbors[0]["focus_replies_to_this"] is True
    assert episode.neighbors[0]["author"] == "peer (not persona evidence)"
    assert episode.neighbors[0]["speaker_id"] != IDENTITY.user_id
    assert "pixels not retrieved" in episode.neighbors[0]["visual_context"]
    assert "Keep the current rule?" not in repr(episode)
    assert not episode.matches("Nope.", None)
    assert not episode.matches("Yep.", NOW.isoformat())


async def test_native_context_excludes_bots_webhooks_other_guilds_and_old_neighbors():
    channel, focus = channel_with()
    rows = [
        focus,
        message(channel, 99, author=9, author_override=None),
        message(channel, 98, author=8, webhook_id=1),
        message(channel, 97, guild=SimpleNamespace(id=78)),
        message(channel, 96, created_at=NOW - timedelta(hours=2)),
        message(channel, 95, created_at=NOW + timedelta(minutes=1)),
        message(channel, 94, text="No problem."),
    ]
    rows[1].author.bot = True

    async def history(**_kwargs):
        for row in rows:
            yield row

    channel.history = history
    episode = await collect(channel)
    assert len(episode.neighbors) == 1
    assert episode.neighbors[0]["author"] == "verified Andrew (context only)"
    assert len(episode.neighbors[0]["text"]) <= 350


async def test_native_reference_is_refreshed_in_same_channel_and_gaps_are_explicit():
    reference = discord.MessageReference(message_id=10, channel_id=10, guild_id=77)
    channel, focus = channel_with(reference=reference)
    setup = message(channel, 10, author=9, text="Earlier human setup.")
    channel.fetch_message = AsyncMock(side_effect=[focus, setup])
    episode = await collect(channel)
    assert len(episode.neighbors) == 1
    assert episode.neighbors[0]["focus_replies_to_this"]
    assert channel.fetch_message.await_count == 2
    channel.fetch_message = AsyncMock(
        side_effect=[
            focus,
            discord.NotFound(SimpleNamespace(status=404, reason="Missing"), "Missing"),
        ]
    )
    episode = await collect(channel)
    assert not episode.neighbors
    assert episode.gaps == ("referenced human context unavailable",)
    focus.reference = discord.MessageReference(message_id=10, channel_id=11, guild_id=77)
    channel.fetch_message = AsyncMock(return_value=focus)
    episode = await collect(channel)
    channel.fetch_message.assert_awaited_once()
    assert episode.gaps == ("cross-channel reference not followed",)


@pytest.mark.parametrize("failure", ["bot", "peer", "guild", "channel", "future", "old", "webhook"])
async def test_native_source_and_scope_are_revalidated_before_neighbor_reads(failure):
    channel, focus = channel_with()
    if failure == "bot":
        focus.author.bot = True
    elif failure == "peer":
        focus.author.id = 99
    elif failure == "guild":
        channel.guild.id = 78
    elif failure == "channel":
        channel.id = 11
    elif failure == "future":
        focus.created_at = NOW + timedelta(days=1)
    elif failure == "old":
        focus.created_at = NOW - timedelta(days=181)
    else:
        focus.webhook_id = 1
    assert await collect(channel) is None
    assert not channel.reads


async def test_denied_neighbor_history_keeps_only_verified_focus_with_gap():
    channel, _ = channel_with()

    async def history(**_kwargs):
        raise discord.Forbidden(SimpleNamespace(status=403, reason="Denied"), "Denied")
        yield  # pragma: no cover

    channel.history = history
    episode = await collect(channel)
    assert not episode.neighbors
    assert episode.gaps == ("nearby human context unavailable",)
