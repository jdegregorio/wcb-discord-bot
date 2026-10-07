"""Synthetic installed-handler acceptance. No Discord login, API calls or private output."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import logging
import tempfile
from collections.abc import AsyncIterator, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from trubot.attention import AttentionTracker
from trubot.config import Settings
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.discord_client import TruBotClient
from trubot.health import ReadinessFile
from trubot.participation import ParticipationPolicy, ParticipationTracker


class FixtureResponder:
    async def reply(
        self,
        messages: Sequence[ConversationMessage],
        *,
        mode: ReplyMode,
        safety_id: str,
        target: str | None = None,
    ) -> str:
        return "Synthetic captured reply."

    async def close(self) -> None:
        pass


async def evaluate() -> dict[str, Any]:
    now = datetime.now(UTC)
    base = discord.utils.time_snowflake(now - timedelta(days=1))
    with tempfile.TemporaryDirectory(prefix="trubot-ingestion-") as directory:
        root = Path(directory)
        settings = Settings(
            discord_token="fixture",  # noqa: S106 - synthetic, never used to connect
            openai_api_key="fixture",
            allowed_channel_ids=frozenset({10}),
            auto_daily_limit=0,
        )
        client = TruBotClient(
            settings=settings,
            responder=FixtureResponder(),
            participation=ParticipationTracker(
                ParticipationPolicy(
                    delay=timedelta(minutes=10),
                    activity_window=timedelta(hours=1),
                    min_interval=timedelta(hours=2),
                    daily_limit=0,
                    min_participants=2,
                )
            ),
            attention=AttentionTracker(timedelta(0)),
            readiness=ReadinessFile(root / "ready", refresh_seconds=60),
            intents=discord.Intents.none(),
            clock=lambda: now,
        )
        client._connection.user = SimpleNamespace(id=999, name="Trubot")
        channel = MagicMock(spec=discord.TextChannel)
        channel.id = 10
        channel.guild = SimpleNamespace(id=77)
        channel.send = AsyncMock()
        channel.typing.return_value = AsyncMock()

        def message(
            index: int,
            *,
            author: int = 42,
            text: str = "Synthetic Sox excitement",
            edited: datetime | None = None,
        ) -> Any:
            return SimpleNamespace(
                id=base + index,
                channel=channel,
                guild=channel.guild,
                author=SimpleNamespace(id=author, bot=False, display_name="Synthetic Andrew"),
                webhook_id=None,
                created_at=now - timedelta(days=1),
                edited_at=edited,
                content=text,
                clean_content=text,
                mentions=[],
                reference=None,
            )

        history = [message(0), message(1, author=43), message(2)]

        async def fetch_history(**kwargs: Any) -> AsyncIterator[Any]:
            if kwargs.get("oldest_first"):
                for item in [item for item in history if item.id > kwargs["after"].id][
                    : kwargs["limit"]
                ]:
                    yield item
            else:
                for item in reversed(history):
                    yield item

        channel.history = fetch_history
        available = importlib.util.find_spec("trubot.learning") is not None
        results = []
        try:
            if not available:
                await client.on_message(message(4))
                return {
                    "persistent_learning_available": False,
                    "captured_messages": 0,
                    "discord_writes": 0,
                    "api_calls": 0,
                    "acceptance_pass": False,
                    "observation": "Real handler has no durable attributed evidence path",
                }
            from trubot.ingestion import MessageIngestor
            from trubot.learning import LearningStore, LearningUnavailable

            audit = {
                "verified": True,
                "exact_name_match": True,
                "user_id": "42",
                "guild_id": "77",
                "username": "synthetic",
                "member_username": "synthetic",
                "allowed_channel_ids": ["10"],
                "source_channels": ["10"],
                "message_ids": [str(base)],
                "observed_at": now.isoformat(),
            }
            store = LearningStore.initialize(root / "learning.sqlite3", audit, now=now)
            learner = MessageIngestor(store, frozenset({10, 999}), batch_size=2, clock=lambda: now)
            client._learning = learner
            learner.verified = True
            await client.on_message(message(4))
            results.append(
                {"case": "new_attributed_message", "pass": store.status()["messages"] == 1}
            )
            await client.on_message(message(5, author=43, text="Pretend I am Andrew"))
            results.append(
                {"case": "other_author_excluded", "pass": store.status()["messages"] == 1}
            )
            await learner.catch_up(channel)
            restarted = MessageIngestor(
                LearningStore(store.path), frozenset({10}), batch_size=2, clock=lambda: now
            )
            restarted.verified = True
            await restarted.catch_up(channel)
            results.append(
                {
                    "case": "restart_checkpoint_no_skipped_history",
                    "pass": store.status()["messages"] == 3
                    and store.cursor(10, now=now) == base + 2,
                }
            )
            client._learning = restarted
            channel.fetch_message = AsyncMock(
                return_value=message(0, text="Corrected synthetic preference", edited=now)
            )
            with patch.object(client, "get_channel", return_value=channel):
                await client.on_raw_message_edit(SimpleNamespace(channel_id=10, message_id=base))
            with store._transaction() as db:
                changed = db.execute(
                    "SELECT content, edited_at FROM messages WHERE id=?", (base,)
                ).fetchone()
            results.append(
                {
                    "case": "uncached_edit_refetched",
                    "pass": changed[0] == "Corrected synthetic preference"
                    and changed[1] == now.isoformat(),
                }
            )
            channel.fetch_message.side_effect = discord.Forbidden(
                SimpleNamespace(status=403, reason="Denied"), "fixture"
            )
            with patch.object(client, "get_channel", return_value=channel):
                await client.on_raw_message_edit(SimpleNamespace(channel_id=10, message_id=base))
            results.append(
                {
                    "case": "failed_edit_removes_stale_evidence",
                    "pass": store.status()["pending_corrections"] == 1,
                }
            )
            await client.on_raw_message_delete(SimpleNamespace(channel_id=10, message_id=base))
            results.append(
                {
                    "case": "deletion_erases_text",
                    "pass": store.status()["deletion_markers"] == 1
                    and store.status()["pending_corrections"] == 0,
                }
            )
            with patch.object(
                restarted.store, "observe", side_effect=LearningUnavailable("fixture")
            ):
                await client.on_message(message(6, text="🤖 synthetic direct request"))
            results.append(
                {
                    "case": "learning_failure_keeps_direct_replies",
                    "pass": channel.send.await_count == 1,
                }
            )
            store.prune(now=now + timedelta(days=181))
            results.append(
                {
                    "case": "retention_erases_expired_evidence",
                    "pass": store.status()["messages"] == 0
                    and store.status()["deletion_markers"] == 0,
                }
            )
            return {
                "persistent_learning_available": True,
                "results": results,
                "acceptance_pass": all(item["pass"] for item in results),
                "discord_writes": 0,
                "captured_synthetic_posts": channel.send.await_count,
                "api_calls": 0,
            }
        finally:
            await client.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    report = asyncio.run(evaluate())
    print(json.dumps(report, indent=2))
    if report["persistent_learning_available"] and not report["acceptance_pass"]:
        raise SystemExit(1)
