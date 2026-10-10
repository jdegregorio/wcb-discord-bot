"""Bounded private graph acceptance through real handlers, with every send captured."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from trubot.app import build_client
from trubot.config import Settings
from trubot.learning import _private


class Typing:
    async def __aenter__(self):
        return None

    async def __aexit__(self, *_args):
        return None


async def evaluate(expectations: Path, *, phase: str):
    _private(expectations)
    if (await asyncio.to_thread(expectations.stat)).st_size > 16_000:
        raise ValueError("Private expectations must be bounded")
    cases = json.loads(await asyncio.to_thread(expectations.read_text))["cases"]
    if not 1 <= len(cases) <= 3:
        raise ValueError("At most three private acceptance cases")
    settings = Settings.from_env()
    client = build_client(settings, spending_purpose="maintenance")
    learning = client._learning
    if learning is None:
        raise RuntimeError("Verified private source store required")
    identity = learning.identity
    await client.login(settings.discord_token)
    results = []
    try:
        member = await client.http.get_member(identity.guild_id, identity.user_id)
        if int(member["user"]["id"]) != identity.user_id or member["user"].get("bot"):
            raise RuntimeError("Pinned human membership unavailable")
        learning.verified = True
        client._connection.user = SimpleNamespace(id=999, name="Trubot")
        channels = {}
        for channel_id in sorted(learning.channel_ids):
            channel = MagicMock(spec=discord.TextChannel)
            channel.id = channel_id
            channel.guild = SimpleNamespace(id=identity.guild_id)
            channel.send = AsyncMock()
            channel.typing.return_value = Typing()

            async def history(**_kwargs):
                for item in []:
                    yield item

            async def fetch(message_id, channel_id=channel_id, channel=channel):
                row = await client.http.get_message(channel_id, message_id)
                return SimpleNamespace(
                    id=int(row["id"]),
                    channel=channel,
                    guild=channel.guild,
                    author=SimpleNamespace(
                        id=int(row["author"]["id"]), bot=row["author"].get("bot", False)
                    ),
                    webhook_id=row.get("webhook_id"),
                    created_at=datetime.fromisoformat(row["timestamp"]),
                    edited_at=datetime.fromisoformat(row["edited_timestamp"])
                    if row.get("edited_timestamp")
                    else None,
                    content=row["content"],
                    attachments=row.get("attachments", []),
                    embeds=row.get("embeds", []),
                    reference=(
                        discord.MessageReference(
                            message_id=int(row["message_reference"]["message_id"]),
                            channel_id=int(row["message_reference"]["channel_id"]),
                            guild_id=identity.guild_id,
                        )
                        if (row.get("message_reference") or {}).get("message_id")
                        else None
                    ),
                )

            channel.history = history
            channel.fetch_message = fetch
            channels[channel_id] = channel
        channel = next(iter(channels.values()))
        root = expectations.parent
        private_results = []
        with patch.object(client, "get_channel", side_effect=channels.get):
            for index, case in enumerate(cases):
                mode = case["mode"]
                question = case["question"]
                if mode not in {"direct", "reaction", "followup"} or len(question) > 800:
                    raise ValueError("Bounded valid acceptance mode/question required")
                message = MagicMock(spec=discord.Message)
                message.id = 123
                message.channel, message.guild = channel, channel.guild
                message.author = SimpleNamespace(
                    id=1, bot=False, display_name="Synthetic evaluator"
                )
                message.mentions, message.attachments, message.embeds = [], [], []
                message.reference = None
                message.content = message.clean_content = (
                    "🤖 " + question if mode == "direct" else question
                )
                channel.send.reset_mock()
                captured_context = {"text": "", "milliseconds": 0.0}
                memory_context = client._memory_context

                async def capture_memory(
                    *args,
                    memory_context=memory_context,
                    captured_context=captured_context,
                    **kwargs,
                ):
                    started = time.perf_counter()
                    text = await memory_context(*args, **kwargs)
                    captured_context["text"] = text
                    captured_context["milliseconds"] = round(
                        (time.perf_counter() - started) * 1000, 2
                    )
                    return text

                client._memory_context = capture_memory
                start = time.perf_counter()
                if mode == "followup":
                    client._attention.activate(channel.id, datetime.now(UTC))
                if mode == "reaction":
                    source_fetch = channel.fetch_message

                    async def reaction_fetch(
                        message_id, message=message, source_fetch=source_fetch
                    ):
                        return (
                            message if message_id == message.id else await source_fetch(message_id)
                        )

                    channel.fetch_message = reaction_fetch
                    try:
                        await client.on_raw_reaction_add(
                            SimpleNamespace(
                                user_id=1,
                                channel_id=channel.id,
                                message_id=123,
                                emoji=SimpleNamespace(
                                    name=next(iter(settings.reaction_emoji_names))
                                ),
                                member=SimpleNamespace(bot=False),
                            )
                        )
                    finally:
                        channel.fetch_message = source_fetch
                else:
                    await client.on_message(message)
                reply = channel.send.call_args.args[0] if channel.send.call_args else ""
                client._memory_context = memory_context
                context = captured_context["text"]
                graph_used = "CONNECTED REVIEWED MEMORY" in context
                retrieval_ms = captured_context["milliseconds"]
                passed = bool(reply) and any(
                    term.casefold() in reply.casefold() for term in case["required_any"]
                )
                results.append(
                    {
                        "case": index + 1,
                        "mode": mode,
                        "passed": passed,
                        "graph_used": graph_used,
                        "context_bytes": len(context.encode()),
                        "retrieval_ms": retrieval_ms,
                        "response_ms": round((time.perf_counter() - start) * 1000, 2),
                        "captured_posts": channel.send.await_count,
                    }
                )
                private_results.append(
                    {"question": question, "reply": reply, "context": context, "passed": passed}
                )
        path = root / ("responses-" + phase + ".json")
        path.write_text(json.dumps(private_results, ensure_ascii=False))
        path.chmod(0o600)
        report = {
            "phase": phase,
            "no_discord_writes": True,
            "cases": results,
            "rubric": "Answer terms check recall; contextual fidelity needs separate review.",
        }
        print(json.dumps(report))
        if phase != "before" and not all(r["passed"] and r["graph_used"] for r in results):
            raise SystemExit(1)
    finally:
        await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expectations", type=Path, required=True)
    parser.add_argument("--phase", choices=("before", "candidate", "installed"), required=True)
    args = parser.parse_args()
    logging.disable(logging.CRITICAL)
    try:
        asyncio.run(evaluate(args.expectations, phase=args.phase))
    except Exception as error:
        parser.exit(2, "Graph acceptance unavailable: " + type(error).__name__ + ".\n")
