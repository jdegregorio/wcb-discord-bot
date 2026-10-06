"""Bounded, opt-in live evaluation through Discord event handlers, with no Discord writes.

Only repository-owned synthetic fixtures may be supplied. Outputs need rubric review;
transport checks alone cannot measure enthusiasm or authenticity. No LLM judge is used.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from trubot.app import build_client
from trubot.config import Settings


class TypingContext:
    async def __aenter__(self) -> None:
        return None

    async def __aexit__(self, *_args: object) -> None:
        return None


async def evaluate(fixtures: Path, samples: int) -> dict[str, object]:
    cases = json.loads(await asyncio.to_thread(fixtures.read_text))
    if not isinstance(cases, list) or not 1 <= len(cases) <= 12:
        raise ValueError("Supply 1 to 12 synthetic cases")
    if not 1 <= samples <= 3:
        raise ValueError("Samples must be between 1 and 3")
    settings = Settings.from_env()
    # Synthetic IDs ensure neither a real guild nor a real user's ID is transmitted.
    settings = Settings(
        discord_token=settings.discord_token,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        openai_timeout_seconds=settings.openai_timeout_seconds,
        openai_max_retries=0,
        openai_max_output_tokens=min(settings.openai_max_output_tokens, 180),
        allowed_channel_ids=frozenset({10}),
        auto_daily_limit=0,
        ready_file=Path("/tmp/trubot-evaluation-ready"),  # noqa: S108 - isolated fixture heartbeat
    )
    results = []
    input_tokens = cached_tokens = output_tokens = requests = successful_responses = 0
    missing_usage_responses = 0
    for case in cases:
        for sample in range(samples):
            client = build_client(settings)
            client._connection.user = SimpleNamespace(id=999, name="Trubot")
            channel = MagicMock(spec=discord.TextChannel)
            channel.id = 10
            channel.guild = SimpleNamespace(id=77)
            channel.send = AsyncMock()
            channel.typing.return_value = TypingContext()
            history_messages = [
                SimpleNamespace(
                    clean_content=item["text"],
                    author=SimpleNamespace(
                        id=999 if item.get("bot") else 1,
                        bot=item.get("bot", False),
                        display_name=item["speaker"],
                    ),
                )
                for item in case["history"]
            ]

            async def history(
                history_messages=history_messages, **_kwargs: object
            ) -> AsyncIterator[object]:
                for item in reversed(history_messages):
                    yield item

            channel.history = history
            message = MagicMock(spec=discord.Message)
            message.channel = channel
            message.id = 123
            message.guild = channel.guild
            message.author = SimpleNamespace(id=1, bot=False, display_name="Casey")
            message.mentions = []
            message.reference = None
            message.content = message.clean_content = case["target"]
            if case["mode"] == "direct":
                message.content = message.clean_content = "🤖 " + case["target"]
            if case["mode"] == "follow_up":
                client._attention.activate(10, datetime.now(UTC))
            channel.fetch_message = AsyncMock(return_value=message)
            create = client._responder._client.responses.create
            generation_completed = False

            async def measured_create(create=create, **kwargs: object) -> object:
                nonlocal input_tokens, cached_tokens, output_tokens, requests
                nonlocal successful_responses, missing_usage_responses, generation_completed
                requests += 1
                response = await create(**kwargs)
                generation_completed = True
                successful_responses += 1
                if response.usage:
                    input_tokens += response.usage.input_tokens
                    cached_tokens += response.usage.input_tokens_details.cached_tokens
                    output_tokens += response.usage.output_tokens
                else:
                    missing_usage_responses += 1
                return response

            try:
                with patch.object(
                    client._responder._client.responses, "create", side_effect=measured_create
                ):
                    if case["mode"] == "reaction":
                        payload = SimpleNamespace(
                            user_id=1,
                            channel_id=10,
                            message_id=123,
                            emoji=SimpleNamespace(name="ThomasJones"),
                            member=None,
                        )
                        with patch.object(client, "get_channel", return_value=channel):
                            await client.on_raw_reaction_add(payload)
                    else:
                        await client.on_message(message)
                posts = [call.args[0] for call in channel.send.await_args_list]
                fallback = "Something broke. Probably Tim's fault."
                transport_pass = generation_completed and (
                    not posts
                    if case.get("expect_abstain")
                    else len(posts) == 1 and posts[0] != fallback and 0 < len(posts[0]) <= 2000
                )
                results.append(
                    {
                        "id": case["id"],
                        "sample": sample + 1,
                        "mode": case["mode"],
                        "posts": posts,
                        "transport_pass": transport_pass,
                        "rubric": case["rubric"],
                    }
                )
            finally:
                await client.close()
    return {
        "model": settings.openai_model,
        "requests": requests,
        "successful_responses": successful_responses,
        "missing_usage_responses": missing_usage_responses,
        "usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_tokens,
            "output_tokens": output_tokens,
        },
        "results": results,
        "rubric_review_required": True,
        "discord_writes": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--samples", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args()
    # Suppress SDK/Discord logs. Only synthetic fixture outputs are emitted.
    logging.basicConfig(level=logging.CRITICAL)
    report = asyncio.run(evaluate(args.fixtures, args.samples))
    print(json.dumps(report, indent=2))
    if not all(item["transport_pass"] for item in report["results"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
