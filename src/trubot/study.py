"""Trusted, read-only Discord maintenance entry point for complete episode studies."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Callable
from contextlib import AsyncExitStack
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import discord
from openai import AsyncOpenAI

from trubot.budget import UsageLedger
from trubot.config import Settings
from trubot.distillation import GraphDistiller, _episode_keys
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable, _private
from trubot.openai_responder import OpenAITruaxResponder


def read_episode_refs(path: Path) -> list[dict[str, Any]]:
    """Accept source selectors only. This file does not supply new human evidence."""
    _private(path)
    if path.stat().st_size > 4096:
        raise LearningUnavailable("Bounded private episode manifest required")
    data = json.loads(path.read_text())
    if (
        not isinstance(data, dict)
        or set(data) != {"schema", "episode_refs"}
        or type(data["schema"]) is not int
        or data["schema"] != 1
    ):
        raise LearningUnavailable("Unsupported episode manifest")
    refs: list[dict[str, Any]] = data["episode_refs"]
    _episode_keys(refs)
    return refs


async def execute_study(
    client: discord.Client,
    ingestor: MessageIngestor,
    responder: OpenAITruaxResponder,
    refs: list[dict[str, Any]],
    *,
    clock: Callable[[], datetime],
) -> dict[str, Any]:
    """Authenticate the pinned source member, without a gateway or Discord writes."""
    _episode_keys(refs)
    _ensure_identity(ingestor)
    guild = await client.fetch_guild(ingestor.identity.guild_id)
    client._connection._add_guild(guild)
    _ensure_identity(ingestor)
    await ingestor.verify_member(client)
    # Source channels remain the runtime intake intersection, never development scope.
    for channel_id in sorted(ingestor.channel_ids):
        _ensure_identity(ingestor)
        channel = await client.fetch_channel(channel_id)
        # The configured reply allowlist also contains the private development
        # guild. A configured channel is not necessarily a source-guild channel.
        # Never cache it as learning context. Denied HTTP reads still propagate.
        if not isinstance(channel, (discord.TextChannel, discord.Thread)) or not ingestor.accepts(
            channel
        ):
            continue
        if isinstance(channel, discord.Thread):
            guild._add_thread(channel)
        else:
            guild._add_channel(channel)
    _ensure_identity(ingestor)
    distiller = GraphDistiller(ingestor, responder, clock=clock)
    outcome = await distiller.cycle(client, episode_refs=refs)
    # Use this cycle's receipt, never another process's recent checkpoint.
    return {
        "selected_sources": len(refs),
        "completed": outcome is not None,
        "outcome": outcome or "not_completed",
        "accepted": outcome == "accepted",
        "gateway_started": False,
        "discord_writes": 0,
        "human_review": False,
    }


def _ensure_identity(ingestor: MessageIngestor) -> None:
    # identity() checks withdrawal under the source lock before each HTTP stage.
    if ingestor.store.identity() != ingestor.identity:
        raise LearningUnavailable("Source identity changed during study")


async def run(refs: list[dict[str, Any]]) -> dict[str, Any]:
    settings = Settings.from_env()
    learning = LearningStore(
        settings.learning_store_path, retention_days=settings.learning_retention_days
    )
    ingestor = MessageIngestor(
        learning, settings.allowed_channel_ids, clock=lambda: datetime.now(UTC)
    )
    # Plain HTTP clients own no application heartbeat and never start a gateway.
    async with AsyncExitStack() as stack:
        api = await stack.enter_async_context(
            AsyncOpenAI(
                api_key=settings.openai_api_key,
                max_retries=0,
                timeout=settings.openai_timeout_seconds,
            )
        )
        client = await stack.enter_async_context(discord.Client(intents=discord.Intents.none()))
        responder = OpenAITruaxResponder(
            api,
            model=settings.openai_model,
            max_output_tokens=settings.openai_max_output_tokens,
            budget=UsageLedger(settings.usage_ledger_path),
            purpose="maintenance",
            max_retries=settings.openai_max_retries,
        )
        _ensure_identity(ingestor)
        await client.login(settings.discord_token)
        return await execute_study(
            client, ingestor, responder, refs, clock=lambda: datetime.now(UTC)
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Study a complete private reviewed episode set")
    parser.add_argument("--episodes", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = asyncio.run(run(read_episode_refs(args.episodes)))
        print(json.dumps(result))
        if not result["completed"]:
            parser.exit(
                2, "Study not completed; retain pacing and inspect content-free diagnostics.\n"
            )
    except Exception:
        # Source/model/transport exceptions may contain personal text or credentials.
        parser.exit(2, "Study unavailable; inspect private scope, evidence and spending state.\n")


if __name__ == "__main__":
    main()
