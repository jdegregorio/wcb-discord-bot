"""Privately capture earliest guild archives and image episodes; never post.

Operator development only. Runtime intake scope is unchanged. External embedded
images retain references, while actual Discord image attachments retain bytes.
"""

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path

import discord

from trubot.archives import MAX_SOURCE_BYTES, parse_slack_export
from trubot.learning import LearningStore, LearningUnavailable, _private

MAX_VISUAL_BYTES = 64 * 1024 * 1024
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp")


def save(directory: Path, name: str, raw: bytes) -> None:
    target = directory / name
    if target.exists():
        _private(target)
        if target.read_bytes() != raw:
            raise LearningUnavailable("Conflicting staged source")
        return
    with target.open("xb") as stream:
        target.chmod(0o600)
        stream.write(raw)


def context_message(message: discord.Message) -> dict[str, object]:
    return {
        "id": str(message.id),
        "author_id": str(message.author.id),
        "speaker": message.author.display_name,
        "bot": message.author.bot,
        "webhook": message.webhook_id is not None,
        "created_at": message.created_at.isoformat(),
        "edited_at": message.edited_at.isoformat() if message.edited_at else None,
        "content": message.content,
        "reference": message.reference.to_dict() if message.reference else None,
        "reactions": [{"emoji": str(r.emoji), "count": r.count} for r in message.reactions],
        "attachments": [
            {"id": str(a.id), "filename": a.filename, "content_type": a.content_type}
            for a in message.attachments
        ],
        "embeds": [e.to_dict() for e in message.embeds],
    }


async def discover(directory: Path, learning: LearningStore, *, limit: int = 100) -> dict[str, int]:
    identity = learning.identity()
    await asyncio.to_thread(directory.mkdir, mode=0o700, exist_ok=True)
    _private(directory)
    entries, inventory, visuals = [], [], []
    captured_assets: set[str] = set()
    counts = {
        "channels_scanned": 0,
        "unavailable_channels": 0,
        "text_attachments": 0,
        "supported_exports": 0,
        "unsupported_text_files": 0,
        "visual_episodes": 0,
        "image_assets": 0,
        "image_bytes": 0,
        "uncaptured_images": 0,
    }
    async with discord.Client(intents=discord.Intents.none()) as client:
        await client.login(os.environ["DISCORD_TOKEN"])
        guild = await client.fetch_guild(identity.guild_id)
        member = await guild.fetch_member(identity.user_id)
        if member.bot or member.id != identity.user_id:
            raise LearningUnavailable("Pinned human unavailable")
        for channel in await guild.fetch_channels():
            if not isinstance(channel, discord.TextChannel):
                continue
            learning.identity()
            try:
                messages = [m async for m in channel.history(limit=limit, oldest_first=True)]
                for index, message in enumerate(messages):
                    images: list[dict[str, object]] = []
                    for attachment in message.attachments:
                        origin = {
                            "kind": "discord_attachment",
                            "guild_id": str(guild.id),
                            "channel_id": str(channel.id),
                            "message_id": str(message.id),
                            "attachment_id": str(attachment.id),
                            "filename": attachment.filename,
                            "posted_at": message.created_at.isoformat(),
                        }
                        is_image = attachment.filename.lower().endswith(IMAGE_SUFFIXES)
                        is_text = attachment.filename.lower().endswith(".txt")
                        if not is_image and not is_text:
                            continue
                        if not 0 < attachment.size <= MAX_SOURCE_BYTES or (
                            is_image and counts["image_bytes"] + attachment.size > MAX_VISUAL_BYTES
                        ):
                            if is_image:
                                counts["uncaptured_images"] += 1
                                images.append(origin | {"captured": False, "reason": "byte_limit"})
                            continue
                        try:
                            raw = await attachment.read()
                        except discord.HTTPException:
                            if is_image:
                                counts["uncaptured_images"] += 1
                                images.append(
                                    origin | {"captured": False, "reason": "download_unavailable"}
                                )
                            continue
                        digest = hashlib.sha256(raw).hexdigest()
                        suffix = Path(attachment.filename).suffix.lower() if is_image else ".txt"
                        name = digest + suffix
                        await asyncio.to_thread(save, directory, name, raw)
                        if is_image:
                            images.append(
                                origin
                                | {
                                    "captured": True,
                                    "digest": digest,
                                    "path": name,
                                    "content_type": attachment.content_type,
                                }
                            )
                            if digest not in captured_assets:
                                captured_assets.add(digest)
                                counts["image_assets"] += 1
                                counts["image_bytes"] += len(raw)
                            continue
                        counts["text_attachments"] += 1
                        supported = True
                        try:
                            parse_slack_export(raw, target_alias="andrew.truax")
                        except LearningUnavailable:
                            supported = False
                        inventory.append(origin | {"digest": digest, "supported": supported})
                        if not supported:
                            counts["unsupported_text_files"] += 1
                            continue
                        entries.append(
                            {
                                "path": name,
                                "channel": channel.name,
                                "origin": origin,
                                "period_hint": attachment.filename,
                            }
                        )
                        counts["supported_exports"] += 1
                    # External embed URLs are not fetched or mistaken for retained images.
                    for embed in message.embeds:
                        for media in (embed.image, embed.thumbnail):
                            if media.url:
                                images.append(
                                    {
                                        "kind": "external_embed",
                                        "url": media.url,
                                        "captured": False,
                                        "reason": "reference_only",
                                    }
                                )
                                counts["uncaptured_images"] += 1
                    if images:
                        episode = {
                            "source": {
                                "guild_id": str(guild.id),
                                "channel_id": str(channel.id),
                                "message_id": str(message.id),
                            },
                            "images": images,
                            "context": [
                                context_message(m) for m in messages[max(0, index - 5) : index + 6]
                            ],
                            "relation": "adjacent_native_messages",
                            "radius": 5,
                        }
                        name = "episode-" + str(message.id) + ".json"
                        await asyncio.to_thread(save, directory, name, json.dumps(episode).encode())
                        visuals.append({"path": name})
                        counts["visual_episodes"] += 1
                counts["channels_scanned"] += 1
            except discord.HTTPException:
                counts["unavailable_channels"] += 1
    manifest = {
        "schema": 1,
        "target_alias": "andrew.truax",
        "alias_basis": (
            "Joe authorized league Slack history attached in Discord; exact legacy alias only. "
            "No stable Slack author IDs exist in text exports."
        ),
        "files": entries,
        "visuals": visuals,
    }
    for name, value in (("manifest.json", manifest), ("inventory.json", inventory)):
        await asyncio.to_thread(save, directory, name, json.dumps(value, indent=2).encode())
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Private read-only historical attachment discovery"
    )
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument(
        "--learning-path", type=Path, default=Path("/var/lib/trubot/learning.sqlite3")
    )
    arguments = parser.parse_args()
    try:
        print(
            json.dumps(
                asyncio.run(discover(arguments.directory, LearningStore(arguments.learning_path)))
            )
        )
    except (LearningUnavailable, discord.HTTPException, OSError, KeyError):
        parser.exit(2, "Attachment discovery unavailable; inspect private source access.\n")
