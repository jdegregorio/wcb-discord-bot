import asyncio
from collections.abc import AsyncIterator, Sequence
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from trubot.config import Settings
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.discord_client import Responder, TruBotClient
from trubot.health import ReadinessFile
from trubot.participation import ParticipationPolicy, ParticipationTracker

NOW = datetime(2026, 8, 30, 12, tzinfo=UTC)


class FakeResponder:
    def __init__(self, output: str = "Hot", error: Exception | None = None) -> None:
        self.output = output
        self.error = error
        self.calls: list[tuple[Sequence[ConversationMessage], ReplyMode, str, str | None]] = []
        self.closed = False

    async def reply(
        self,
        messages: Sequence[ConversationMessage],
        *,
        mode: ReplyMode,
        safety_id: str,
        target: str | None = None,
    ) -> str:
        self.calls.append((messages, mode, safety_id, target))
        if self.error is not None:
            raise self.error
        return self.output

    async def close(self) -> None:
        self.closed = True


class FakeReadiness:
    def __init__(self) -> None:
        self.started = 0
        self.stopped = 0

    async def start(self) -> None:
        self.started += 1

    async def stop(self) -> None:
        self.stopped += 1


class TypingContext:
    async def __aenter__(self) -> None:
        return None

    async def __aexit__(self, *_args: object) -> None:
        return None


def message_for_history(
    content: str,
    *,
    author_id: int,
    bot: bool = False,
    name: str = "Tim",
) -> discord.Message:
    return cast(
        discord.Message,
        SimpleNamespace(
            clean_content=content,
            author=SimpleNamespace(id=author_id, bot=bot, display_name=name),
        ),
    )


def fake_channel(channel_id: int = 10) -> MagicMock:
    channel = MagicMock(spec=discord.TextChannel)
    channel.id = channel_id
    channel.guild = SimpleNamespace(id=77)
    channel.send = AsyncMock()
    channel.fetch_message = AsyncMock()
    channel.typing.return_value = TypingContext()
    history_messages = [message_for_history("🤖 hello", author_id=1)]

    async def history(*, limit: int, oldest_first: bool) -> AsyncIterator[discord.Message]:
        assert limit == 15
        assert oldest_first
        for item in history_messages:
            yield item

    channel.history = history
    channel.history_messages = history_messages
    return channel


def fake_message(channel: MagicMock, *, user_id: int = 1, direct: bool = True) -> MagicMock:
    message = MagicMock(spec=discord.Message)
    message.channel = channel
    message.author = SimpleNamespace(id=user_id, bot=False, display_name="Tim")
    message.content = "🤖 hello" if direct else "hello"
    message.clean_content = message.content
    message.mentions = []
    message.reply = AsyncMock()
    return message


def make_client(
    *,
    responder: FakeResponder | None = None,
    readiness: FakeReadiness | None = None,
    sleeper: object = asyncio.sleep,
) -> tuple[TruBotClient, FakeResponder, FakeReadiness, ParticipationTracker]:
    settings = Settings(
        discord_token="discord-secret",
        openai_api_key="openai-secret",
        allowed_channel_ids=frozenset({10}),
        auto_delay_seconds=0,
    )
    actual_responder = responder or FakeResponder()
    actual_readiness = readiness or FakeReadiness()
    participation = ParticipationTracker(
        ParticipationPolicy(
            delay=timedelta(0),
            activity_window=timedelta(hours=1),
            min_interval=timedelta(hours=2),
            daily_limit=3,
            min_participants=2,
        )
    )
    client = TruBotClient(
        settings=settings,
        responder=cast(Responder, actual_responder),
        participation=participation,
        readiness=cast(ReadinessFile, actual_readiness),
        intents=discord.Intents.default(),
        clock=lambda: NOW,
        sleeper=cast("object", sleeper),
    )
    client._connection.user = cast(
        discord.ClientUser,
        SimpleNamespace(id=999, name="Trubot", display_name="Trubot"),
    )
    return client, actual_responder, actual_readiness, participation


@pytest.mark.asyncio
async def test_direct_trigger_replies_with_context_and_records_cooldown() -> None:
    client, responder, _readiness, participation = make_client()
    channel = fake_channel()
    message = fake_message(channel)

    await client.on_message(message)

    assert len(responder.calls) == 1
    context, mode, safety_id, target = responder.calls[0]
    assert [item.content for item in context] == ["Tim: 🤖 hello"]
    assert mode is ReplyMode.DIRECT
    assert len(safety_id) == 64
    assert target == "Tim: 🤖 hello"
    message.reply.assert_awaited_once_with("Hot", mention_author=False)
    assert participation.snapshot(10, NOW).last_reply_at == NOW


@pytest.mark.asyncio
async def test_model_failure_gets_a_safe_in_character_visible_error() -> None:
    client, _responder, _readiness, _participation = make_client(
        responder=FakeResponder(error=RuntimeError("provider down"))
    )
    channel = fake_channel()
    message = fake_message(channel)

    await client.on_message(message)

    message.reply.assert_awaited_once_with(
        "Something broke. Probably Tim's fault.",
        mention_author=False,
    )


@pytest.mark.asyncio
async def test_ambient_task_posts_only_for_the_current_eligible_revision() -> None:
    async def no_sleep(_seconds: float) -> None:
        return None

    client, responder, _readiness, participation = make_client(sleeper=no_sleep)
    channel = fake_channel()
    channel.history_messages[:] = [
        message_for_history("first", author_id=1, name="Tim"),
        message_for_history("second", author_id=2, name="Jim"),
    ]
    participation.observe(10, 1, NOW, allow_ambient=True)
    observation = participation.observe(10, 2, NOW, allow_ambient=True)

    with patch.object(client, "get_channel", return_value=channel):
        await client._run_ambient(10, observation.revision)

    channel.send.assert_awaited_once_with("Hot")
    assert responder.calls[0][1] is ReplyMode.AMBIENT
    assert participation.snapshot(10, NOW).ambient_replies_today == 1

    participation.invalidate(10)
    channel.send.reset_mock()
    with patch.object(client, "get_channel", return_value=channel):
        await client._run_ambient(10, observation.revision)
    channel.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_reaction_trigger_replies_to_the_reacted_message() -> None:
    client, responder, _readiness, _participation = make_client()
    channel = fake_channel()
    source = fake_message(channel, direct=False)
    source.clean_content = "Thomas Jones for a third"
    source.author = SimpleNamespace(id=2, bot=False, display_name="Jim")
    channel.fetch_message.return_value = source
    payload = cast(
        discord.RawReactionActionEvent,
        SimpleNamespace(
            user_id=5,
            channel_id=10,
            message_id=123,
            emoji=SimpleNamespace(name="ThomasJones"),
            member=None,
        ),
    )

    with patch.object(client, "get_channel", return_value=channel):
        await client.on_raw_reaction_add(payload)

    source.reply.assert_awaited_once_with("Hot", mention_author=False)
    assert responder.calls[0][1] is ReplyMode.REACTION
    assert responder.calls[0][3] == "Jim: Thomas Jones for a third"


@pytest.mark.asyncio
async def test_irrelevant_events_are_ignored() -> None:
    client, responder, _readiness, _participation = make_client()
    channel = fake_channel(channel_id=11)
    await client.on_message(fake_message(channel))

    own_reaction = cast(
        discord.RawReactionActionEvent,
        SimpleNamespace(
            user_id=999,
            channel_id=10,
            emoji=SimpleNamespace(name="ThomasJones"),
        ),
    )
    await client.on_raw_reaction_add(own_reaction)

    assert responder.calls == []


@pytest.mark.asyncio
async def test_connection_health_lifecycle_and_close() -> None:
    client, responder, readiness, _participation = make_client()

    await client.on_ready()
    await client.on_disconnect()
    await client.on_resumed()
    await client.close()
    await client.close()

    assert readiness.started == 2
    assert readiness.stopped >= 2
    assert responder.closed
