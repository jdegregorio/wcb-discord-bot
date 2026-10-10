"""Operator-only, accounted acceptance with captured sends and no Discord message writes."""

from __future__ import annotations

import argparse
import asyncio
import io
import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord
from PIL import Image, ImageDraw, ImageFont

from trubot.app import build_client
from trubot.config import Settings
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.learning import _private
from trubot.vision import ImageCollector


class Typing:
    async def __aenter__(self):
        return None

    async def __aexit__(self, *_args):
        return None


async def evaluate(expected_team_file: Path):
    _private(expected_team_file)
    expected_team = (await asyncio.to_thread(expected_team_file.read_text)).strip().casefold()
    if not expected_team:
        raise ValueError("Operator-reviewed private expectation required")
    settings = Settings.from_env()
    client = build_client(settings, spending_purpose="maintenance")
    learning = client._learning
    if learning is None:
        raise RuntimeError("Verified private store required for this operator evaluation")
    identity = learning.identity
    await client.login(settings.discord_token)
    try:
        member = await client.http.get_member(identity.guild_id, identity.user_id)
        if int(member["user"]["id"]) != identity.user_id or member["user"].get("bot"):
            raise RuntimeError("Pinned human membership verification failed")
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

        image = Image.new("RGB", (640, 420), "white")
        draw = ImageDraw.Draw(image)
        draw.polygon([(70, 260), (170, 70), (270, 260)], fill="red")
        draw.ellipse((340, 70, 540, 270), fill="blue")
        draw.text((100, 320), "LEAGUE 42", fill="black", font=ImageFont.load_default(size=44))
        output = io.BytesIO()
        image.save(output, format="PNG")
        fetch_image = AsyncMock(return_value=output.getvalue())
        results = []
        channel = next(iter(channels.values()))
        # Pixel tests use a synthetic fixture and fake CDN, while going through
        # the actual Discord handler, image decoder, Responses adapter and ledger.
        cases = [
            ("baseball-direct", "direct", "Who is your baseball team?", False),
            ("baseball-followup", "followup", "Who is your baseball team?", False),
            ("image-direct", "direct", "Name the two colored shapes and the printed label.", True),
            (
                "image-reaction",
                "reaction",
                "Name the two colored shapes and the printed label.",
                True,
            ),
        ]
        with (
            patch.object(client, "get_channel", side_effect=channels.get),
            patch(
                "trubot.discord_client.ImageCollector",
                side_effect=lambda: ImageCollector(fetch_image),
            ),
        ):
            for case_id, mode, question, visual in cases:
                message = MagicMock(spec=discord.Message)
                message.id = 123
                message.channel, message.guild = channel, channel.guild
                message.author = SimpleNamespace(
                    id=1, bot=False, display_name="Synthetic evaluator"
                )
                message.mentions = []
                message.reference = None
                message.content = message.clean_content = (
                    "🤖 " + question if mode == "direct" else question
                )
                message.attachments = (
                    [
                        SimpleNamespace(
                            url="https://cdn.discordapp.com/synthetic.png",
                            size=len(output.getvalue()),
                            content_type="image/png",
                        )
                    ]
                    if visual
                    else []
                )
                message.embeds = []
                channel.send.reset_mock()
                if mode == "followup":
                    client._attention.activate(channel.id, datetime.now(UTC))
                if mode == "reaction":
                    original_fetch = channel.fetch_message
                    channel.fetch_message = AsyncMock(return_value=message)
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
                        channel.fetch_message = original_fetch
                else:
                    await client.on_message(message)
                reply = channel.send.call_args.args[0] if channel.send.call_args else ""
                lowered = reply.lower()
                passed = (
                    all(term in lowered for term in ("red", "triangle", "blue", "circle", "42"))
                    if visual
                    else expected_team in lowered
                    and not any(x in lowered for x in ("since day one", "lifelong", "always been"))
                )
                results.append({"id": case_id, "passed": passed, "posts": int(bool(reply))})
        # A bot's earlier false claim must not establish a different preference.
        reply = await client._responder.reply(
            [
                ConversationMessage("assistant", "I root for the invented Moon Otters."),
                ConversationMessage("user", "Who is your baseball team?"),
            ],
            mode=ReplyMode.DIRECT,
            safety_id="synthetic-evaluation",
            target="Who is your baseball team?",
        )
        results.append(
            {
                "id": "unsupported-bot-memory",
                "passed": "otter" not in (reply or "").lower(),
                "posts": int(bool(reply)),
            }
        )
        print(json.dumps({"no_discord_writes": True, "cases": results}))
        if not all(r["passed"] for r in results):
            raise SystemExit(1)
    finally:
        await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-team-file", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(evaluate(args.expected_team_file))
