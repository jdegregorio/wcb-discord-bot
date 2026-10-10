import asyncio
from collections.abc import AsyncIterator, Sequence
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from trubot.attention import AttentionTracker
from trubot.config import Settings
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.discord_client import Responder, TruBotClient
from trubot.health import ReadinessFile
from trubot.participation import ParticipationPolicy, ParticipationTracker

NOW = datetime(2026, 8, 30, 12, tzinfo=UTC)


class FakeResponder:
    def __init__(self, output: str | None = "Hot", error: Exception | None = None) -> None:
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
    ) -> str | None:
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
    history_messages = [message_for_history("Code 12346633", author_id=1, name="Joe")]

    async def history(
        *,
        limit: int,
        oldest_first: bool,
        before: discord.Message | None,
        after: datetime,
    ) -> AsyncIterator[discord.Message]:
        assert limit == 30
        assert not oldest_first
        assert after == NOW - timedelta(hours=6)
        channel.history_request = (before, after)
        for item in reversed(history_messages):
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
    clock: object | None = None,
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
    attention = AttentionTracker(timedelta(minutes=10))
    client = TruBotClient(
        settings=settings,
        responder=cast(Responder, actual_responder),
        participation=participation,
        attention=attention,
        readiness=cast(ReadinessFile, actual_readiness),
        intents=discord.Intents.default(),
        clock=cast("object", clock or (lambda: NOW)),
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
    assert [item.content for item in context] == ["Joe: Code 12346633"]
    assert mode is ReplyMode.DIRECT
    assert len(safety_id) == 64
    assert target == "Tim: 🤖 hello"
    assert channel.history_request[0] is message
    channel.send.assert_awaited_once_with("Hot")
    message.reply.assert_not_awaited()
    assert participation.snapshot(10, NOW).last_reply_at == NOW


@pytest.mark.asyncio
async def test_model_failure_gets_a_safe_in_character_visible_error() -> None:
    client, _responder, _readiness, _participation = make_client(
        responder=FakeResponder(error=RuntimeError("provider down"))
    )
    channel = fake_channel()
    message = fake_message(channel)

    await client.on_message(message)

    channel.send.assert_awaited_once_with("Something broke. Probably Tim's fault.")
    message.reply.assert_not_awaited()


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
async def test_reaction_trigger_posts_to_the_channel_without_a_reply_reference() -> None:
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

    channel.send.assert_awaited_once_with("Hot")
    source.reply.assert_not_awaited()
    assert responder.calls[0][1] is ReplyMode.REACTION
    assert responder.calls[0][3] == "Jim: Thomas Jones for a third"


@pytest.mark.asyncio
async def test_recent_summon_allows_an_inferred_follow_up_from_someone_else() -> None:
    client, responder, _readiness, _participation = make_client()
    channel = fake_channel()
    direct = fake_message(channel)

    await client.on_message(direct)
    channel.history_messages[:] = [
        message_for_history("🤖 hello", author_id=1, name="Tim"),
        message_for_history("Hot", author_id=999, bot=True, name="Trubot"),
    ]
    followup = fake_message(channel, user_id=2, direct=False)
    followup.content = "What do you mean by that?"
    followup.clean_content = followup.content

    await client.on_message(followup)

    assert len(responder.calls) == 2
    context, mode, _safety_id, target = responder.calls[1]
    assert [item.content for item in context] == ["Tim: 🤖 hello", "Hot"]
    assert mode is ReplyMode.FOLLOW_UP
    assert target == "Tim: What do you mean by that?"
    assert channel.send.await_count == 2
    followup.reply.assert_not_awaited()


@pytest.mark.asyncio
async def test_inferred_follow_up_can_abstain_without_posting() -> None:
    client, responder, _readiness, _participation = make_client()
    channel = fake_channel()

    await client.on_message(fake_message(channel))
    responder.output = None
    unrelated = fake_message(channel, user_id=2, direct=False)
    unrelated.content = "Jim, did you make that trade?"
    unrelated.clean_content = unrelated.content

    await client.on_message(unrelated)

    assert responder.calls[-1][1] is ReplyMode.FOLLOW_UP
    channel.send.assert_awaited_once_with("Hot")
    unrelated.reply.assert_not_awaited()


@pytest.mark.asyncio
async def test_follow_up_attention_expires() -> None:
    current = [NOW]
    client, responder, _readiness, _participation = make_client(clock=lambda: current[0])
    channel = fake_channel()

    await client.on_message(fake_message(channel))
    current[0] += timedelta(minutes=10)
    later = fake_message(channel, user_id=1, direct=False)
    later.content = "What about now?"
    later.clean_content = later.content
    await client.on_message(later)

    assert len(responder.calls) == 1


@pytest.mark.asyncio
async def test_replying_to_a_trubot_message_is_an_explicit_trigger() -> None:
    client, responder, _readiness, _participation = make_client()
    channel = fake_channel()
    message = fake_message(channel, direct=False)
    message.content = "What did you mean?"
    message.clean_content = message.content
    message.reference = SimpleNamespace(
        resolved=SimpleNamespace(author=SimpleNamespace(id=999, bot=True))
    )

    await client.on_message(message)

    assert responder.calls[0][1] is ReplyMode.DIRECT
    channel.send.assert_awaited_once_with("Hot")


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


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", list(ReplyMode))
async def test_spending_guard_explains_explicit_pause_and_keeps_unsolicited_modes_silent(mode):
    from trubot.budget import BudgetExceeded

    client, _responder, _ready, tracker = make_client(
        responder=FakeResponder(error=BudgetExceeded("Monthly API allowance exhausted"))
    )
    channel = fake_channel()
    try:
        assert not await client._respond(channel, mode=mode, requester_user_id=1, target="Go Sox.")
        if mode in {ReplyMode.DIRECT, ReplyMode.REACTION}:
            channel.send.assert_awaited_once_with("I'm taking a breather. Try me again later.")
        else:
            channel.send.assert_not_awaited()
        assert not tracker._channels
    finally:
        await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("memory", ["", "RETRIEVED HISTORICAL EVIDENCE: source checked"])
async def test_live_images_from_focus_and_reference_keep_authorship_and_focus(memory):
    import io

    from PIL import Image

    from trubot.vision import ImageCollector

    output = io.BytesIO()
    Image.new("RGB", (80, 60), "red").save(output, format="PNG")
    fetch = AsyncMock(return_value=output.getvalue())
    client, responder, _, _ = make_client()
    client._memory_context = AsyncMock(return_value=memory)
    channel = fake_channel()
    message = fake_message(channel)
    message.attachments = [
        SimpleNamespace(
            url="https://cdn.discordapp.com/focus.png", size=100, content_type="image/png"
        )
    ]
    message.embeds = []
    message.reference = discord.MessageReference(message_id=123, channel_id=10)
    referenced = message_for_history("", author_id=2, name="Jim")
    referenced.attachments = [
        SimpleNamespace(
            url="https://cdn.discordapp.com/reference.png", size=100, content_type="image/png"
        )
    ]
    referenced.embeds = []
    channel.fetch_message.return_value = referenced
    with patch("trubot.discord_client.ImageCollector", side_effect=lambda: ImageCollector(fetch)):
        await client.on_message(message)
    context, mode, _, target = responder.calls[0]
    assert mode is ReplyMode.DIRECT
    assert context[-1].content == target
    assert len(context[-1].images) == 1
    reference_position = -3 if memory else -2
    assert "Jim: [image attached]" in context[reference_position].content
    assert len(context[reference_position].images) == 1
    if memory:
        assert context[-2].content == memory
        assert not context[-2].images
    assert fetch.await_count == 2


@pytest.mark.asyncio
async def test_memory_is_verified_refreshed_and_attached_to_real_handler(tmp_path):
    from test_learning import AUDIT, source
    from test_learning import NOW as EVIDENCE_NOW

    from trubot.ingestion import MessageIngestor
    from trubot.learning import LearningStore
    from trubot.memory import ContextMemory
    from trubot.vision import ImageCollector

    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=EVIDENCE_NOW)
    store.observe(source(content="White Sox forever"), now=EVIDENCE_NOW)
    client, _responder, _, _ = make_client(clock=lambda: EVIDENCE_NOW)
    learning = MessageIngestor(store, frozenset({10}), clock=lambda: EVIDENCE_NOW)
    client._learning = learning
    client._memory = ContextMemory(store)
    channel = fake_channel()
    query = "Tim: Who is your baseball team?"
    assert await client._memory_context(channel, query, []) == ""
    learning.verified = True
    with (
        patch.object(client, "get_channel", return_value=channel),
        patch.object(learning, "refresh", new_callable=AsyncMock) as refresh,
        patch("trubot.discord_client.collect_native_episode", new=AsyncMock(return_value=None)),
    ):
        memory = await client._memory_context(channel, query, [])
        assert "White Sox forever" in memory
        refresh.assert_awaited_once()
        refresh.side_effect = discord.Forbidden(
            SimpleNamespace(status=403, reason="Denied"), "Denied"
        )
        assert await client._memory_context(channel, query, []) == ""
        refresh.side_effect = None
        store.forget(now=EVIDENCE_NOW)
        assert await client._memory_context(channel, query, []) == ""
    assert await client._reference_context(None, ImageCollector()) is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("guild_id", "owner_id", "requester_id", "configured", "allowed", "expected"),
    [
        (78, 1, 1, 78, True, True),
        (78, 1, 2, 78, True, False),
        (78, 1, None, 78, True, False),
        (79, 1, 1, 78, True, False),
        (78, None, 1, 78, True, False),
        (78, 1, 1, 0, True, False),
        (78, 1, 1, 78, False, False),
    ],
)
async def test_development_recall_requires_configured_guild_allowed_channel_and_owner(
    tmp_path, guild_id, owner_id, requester_id, configured, allowed, expected
):
    from dataclasses import replace

    from test_learning import AUDIT, source
    from test_learning import NOW as EVIDENCE_NOW

    from trubot.ingestion import MessageIngestor
    from trubot.learning import LearningStore
    from trubot.memory import ContextMemory

    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=EVIDENCE_NOW)
    store.observe(source(content="White Sox forever"), now=EVIDENCE_NOW)
    client, responder, _, _ = make_client(clock=lambda: EVIDENCE_NOW)
    client._settings = replace(
        client._settings,
        development_guild_id=configured,
        allowed_channel_ids=frozenset({10}) if allowed else frozenset({11}),
    )
    learning = MessageIngestor(store, frozenset({10}), clock=lambda: EVIDENCE_NOW)
    learning.verified = True
    client._learning, client._memory = learning, ContextMemory(store)
    development, source_channel = fake_channel(), fake_channel()
    development.guild = SimpleNamespace(id=guild_id, owner_id=owner_id)
    assert not learning.accepts(development)
    with (
        patch.object(client, "get_channel", return_value=source_channel),
        patch.object(learning, "refresh", new_callable=AsyncMock),
        patch("trubot.discord_client.collect_native_episode", new=AsyncMock(return_value=None)),
    ):
        result = await client._memory_context(
            development, "Who is your baseball team?", [], requester_user_id=requester_id
        )
    assert bool(result) is expected
    assert not responder.calls
    assert store.status()["messages"] == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
async def test_development_owner_recall_reaches_discord_handlers_without_learning_tests(
    tmp_path, mode
):
    from dataclasses import replace

    from test_learning import AUDIT, source
    from test_learning import NOW as EVIDENCE_NOW

    from trubot.ingestion import MessageIngestor
    from trubot.learning import LearningStore
    from trubot.memory import ContextMemory

    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=EVIDENCE_NOW)
    store.observe(source(content="White Sox forever"), now=EVIDENCE_NOW)
    client, responder, _, _ = make_client(clock=lambda: EVIDENCE_NOW)
    client._settings = replace(
        client._settings, development_guild_id=78, allowed_channel_ids=frozenset({10, 20})
    )
    learning = MessageIngestor(store, frozenset({10}), clock=lambda: EVIDENCE_NOW)
    learning.verified = True
    client._learning, client._memory = learning, ContextMemory(store)
    development, source_channel = fake_channel(20), fake_channel()
    development.guild = SimpleNamespace(id=78, owner_id=1)

    async def empty_history(**_kwargs):
        for item in []:
            yield item

    development.history = empty_history
    message = fake_message(development, direct=mode == "direct")
    message.content = message.clean_content = "🤖 Who is your baseball team?"
    development.fetch_message.return_value = message
    client._attention.activate(20, EVIDENCE_NOW)
    with (
        patch.object(client, "get_channel", side_effect={10: source_channel, 20: development}.get),
        patch.object(learning, "refresh", new_callable=AsyncMock),
        patch("trubot.discord_client.collect_native_episode", new=AsyncMock(return_value=None)),
    ):
        if mode == "reaction":
            await client.on_raw_reaction_add(
                SimpleNamespace(
                    channel_id=20,
                    user_id=1,
                    message_id=message.id,
                    emoji=SimpleNamespace(name="🍆"),
                    member=SimpleNamespace(bot=False),
                )
            )
        else:
            if mode == "followup":
                message.content = message.clean_content = "Who is your baseball team?"
                message.mentions = []
            await client.on_message(message)
    assert len(responder.calls) == 1
    assert "White Sox forever" in responder.calls[0][0][-1].content
    development.send.assert_awaited_once_with("Hot")
    assert store.status()["messages"] == 1


@pytest.mark.asyncio
async def test_memory_presentation_uses_current_request_not_previous_date_disclaimers(tmp_path):
    from test_learning import AUDIT
    from test_learning import NOW as EVIDENCE_NOW

    from trubot.archives import ArchiveStore
    from trubot.ingestion import MessageIngestor
    from trubot.learning import LearningStore
    from trubot.memory import ContextMemory

    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=EVIDENCE_NOW)
    archive = ArchiveStore.initialize(store)
    archive.import_document(
        b"legacy.target\n  8:01 AM\nI enjoy baseball.",
        channel="general",
        target_alias="legacy.target",
        alias_basis="Synthetic operator audit",
        origin={"kind": "synthetic"},
        period_hint="general_2020.txt",
        now=EVIDENCE_NOW,
    )
    client, _, _, _ = make_client(clock=lambda: EVIDENCE_NOW)
    learning = MessageIngestor(store, frozenset({10}), clock=lambda: EVIDENCE_NOW)
    learning.verified = True
    client._learning, client._memory = learning, ContextMemory(store)
    history = [
        ConversationMessage("user", "Tim: What is the exact date?"),
        ConversationMessage("assistant", "The archive message date is unknown."),
    ]
    try:
        ordinary = await client._memory_context(
            fake_channel(), "Tim: What did you say in 2020?", history
        )
        assert "ordinary recall" in ordinary
        assert "asks about timing" not in ordinary
        exact = await client._memory_context(
            fake_channel(), "Tim: When did you say that about baseball?", history
        )
        assert "asks about timing" in exact
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_source_followup_recovers_quote_from_current_human_evidence_only(tmp_path):
    from test_learning import AUDIT
    from test_learning import NOW as EVIDENCE_NOW

    from trubot.archives import ArchiveStore
    from trubot.ingestion import MessageIngestor
    from trubot.learning import LearningStore
    from trubot.memory import ContextMemory

    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=EVIDENCE_NOW)
    archive = ArchiveStore.initialize(store)
    quote = "Does the waiver tool tell us when we are outbid?"
    archive.import_document(
        ("legacy.target\n  8:01 AM\n" + quote).encode(),
        channel="general",
        target_alias="legacy.target",
        alias_basis="Synthetic operator audit",
        origin={"kind": "synthetic"},
        period_hint="general_2020.txt",
        now=EVIDENCE_NOW,
    )
    client, _, _, _ = make_client(clock=lambda: EVIDENCE_NOW)
    learning = MessageIngestor(store, frozenset({10}), clock=lambda: EVIDENCE_NOW)
    learning.verified = True
    client._learning, client._memory = learning, ContextMemory(store)
    history = [
        ConversationMessage("user", "Tim: Quote one thing from 2020"),
        ConversationMessage("assistant", f"“{quote}”"),
        ConversationMessage("user", "Tim: What exact day?"),
        ConversationMessage("assistant", "I don't know the day."),
    ]
    try:
        result = await client._memory_context(
            fake_channel(), "Tim: What source supports that 2020 memory?", history
        )
        assert quote in result
        assert "asks for evidence" in result
        fabricated = await client._memory_context(
            fake_channel(),
            "Tim: What source supports that 2020 memory?",
            [ConversationMessage("assistant", "“This bot quote is completely invented.”")],
        )
        assert "QUOTATION RECALL" in fabricated
        assert quote not in fabricated
    finally:
        await client.close()


@pytest.mark.parametrize("mode", ["direct", "followup", "reaction"])
@pytest.mark.parametrize("window", ["latest", "from the past week"])
async def test_recent_native_episode_reaches_production_handlers_without_learning_peers(
    tmp_path, mode, window
):
    from test_learning import AUDIT, source
    from test_learning import NOW as EVIDENCE_NOW
    from test_native_context import message as native_message

    from trubot.ingestion import MessageIngestor
    from trubot.learning import LearningStore
    from trubot.memory import ContextMemory

    store = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=EVIDENCE_NOW)
    item = source(
        content="Maybe, if everyone gets a vote.", created_at=EVIDENCE_NOW - timedelta(minutes=1)
    )
    store.observe(item, now=EVIDENCE_NOW)
    learning = MessageIngestor(store, frozenset({10}), clock=lambda: EVIDENCE_NOW)
    learning.verified = True
    client, responder, _, _ = make_client(clock=lambda: EVIDENCE_NOW)
    client._learning, client._memory = learning, ContextMemory(store)
    channel = fake_channel()
    focus = native_message(channel, item.id, text=item.content, created_at=item.created_at)
    setup = native_message(
        channel,
        item.id - 1,
        author=9,
        text="Cut the draft clock to thirty seconds?",
        created_at=item.created_at - timedelta(seconds=1),
    )

    async def history(**kwargs):
        if "around" in kwargs:
            for row in [focus, setup]:
                yield row
        else:
            for row in []:
                yield row

    channel.history = history
    question = fake_message(channel, direct=mode == "direct")
    question.id = item.id + 2
    question.content = question.clean_content = (
        f"🤖 Quote your league message {window} and explain the setup."
    )
    channel.fetch_message = AsyncMock(
        side_effect=lambda message_id: question if message_id == question.id else focus
    )
    client._attention.activate(10, EVIDENCE_NOW)
    with patch.object(client, "get_channel", return_value=channel):
        if mode == "reaction":
            await client.on_raw_reaction_add(
                SimpleNamespace(
                    channel_id=10,
                    user_id=1,
                    message_id=question.id,
                    emoji=SimpleNamespace(name="🍆"),
                    member=SimpleNamespace(bot=False),
                )
            )
        else:
            if mode == "followup":
                question.mentions = []
                question.content = question.clean_content = (
                    f"Quote your league message {window} and explain the setup."
                )
            await client.on_message(question)
    assert len(responder.calls) == 1
    memory = responder.calls[0][0][-1].content
    assert "Maybe, if everyone gets a vote." in memory
    assert "thirty seconds" in memory
    assert "peer (not persona evidence)" in memory
    assert '"position": "before"' in memory
    assert store.status()["messages"] == 1
    channel.send.assert_awaited_once_with("Hot")
    # Every second collector is disposed locally; no peer rows or graph claims were added.
    store.forget(now=EVIDENCE_NOW)
    unavailable = await client._memory_context(channel, question.content, [])
    assert "no verified recent human source" in unavailable
    assert "thirty seconds" not in unavailable


@pytest.mark.parametrize("mode", list(ReplyMode))
async def test_fresh_memory_follows_stale_bot_history_before_current_focus(mode):
    client, responder, _, _ = make_client()
    channel = fake_channel()
    prior = message_for_history("I do not have a verified quote.", author_id=999, bot=True)

    async def history(**kwargs):
        yield prior

    channel.history = history
    packet = "RETRIEVED HISTORICAL EVIDENCE: a freshly verified human quote"
    client._memory_context = AsyncMock(return_value=packet)
    try:
        assert await client._respond(
            channel, mode=mode, requester_user_id=1, target="Joe: Quote last week's message."
        )
        context, actual_mode, _, focus = responder.calls[0]
        assert actual_mode is mode
        assert [m.content for m in context] == [prior.clean_content, packet]
        assert focus == "Joe: Quote last week's message."
    finally:
        await client.close()
