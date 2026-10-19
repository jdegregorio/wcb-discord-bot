"""Operator-only, bounded backward recovery of pinned-human original photo posts."""

from __future__ import annotations

import argparse
import asyncio
import fcntl
import json
import os
from collections import Counter
from collections.abc import Iterator
from contextlib import AsyncExitStack, contextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

import aiohttp
import discord
from openai import AsyncOpenAI
from PIL import Image

from trubot.budget import UsageLedger
from trubot.config import Settings
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable, _private, _time
from trubot.openai_responder import OpenAITruaxResponder
from trubot.photos import MAX_PHOTOS, PhotoMemory
from trubot.vision import image_urls

PAGE_SIZE = 100
MAX_PAGES = 6
MAX_CAPTURES = 2
_SCHEMA = """
CREATE TABLE IF NOT EXISTS photo_history (
    channel INTEGER PRIMARY KEY, before_id INTEGER NOT NULL,
    scanned INTEGER NOT NULL DEFAULT 0, captured INTEGER NOT NULL DEFAULT 0,
    gaps INTEGER NOT NULL DEFAULT 0, state TEXT NOT NULL DEFAULT 'pending',
    updated_at TEXT NOT NULL, turn INTEGER NOT NULL DEFAULT 0
)
"""


class PhotoAccessUnavailable(LearningUnavailable):
    """A denied channel is a gap, never proof of exhausted history."""


class PhotoHistory:
    def __init__(self, photos: PhotoMemory) -> None:
        self.photos = photos
        self.archives = photos.store.archives
        self.learning = photos.learning

    def initialize(self, *, now: datetime) -> None:
        # Backward history starts before the existing recent-intake floor. Never reset it.
        floor = discord.utils.time_snowflake(
            now - timedelta(days=self.learning.store.retention_days)
        )
        identity = self.learning.store.identity()
        with self.archives._transaction() as db:
            # Require already initialized photo memory, including its lifecycle controls.
            db.execute("SELECT channel FROM photo_cursors LIMIT 1")
            db.execute(_SCHEMA)
            db.executemany(
                "INSERT OR IGNORE INTO photo_history(channel,before_id,updated_at) VALUES (?,?,?)",
                [(cid, floor, _time(now)) for cid in sorted(identity.channel_ids)],
            )

    def rows(self) -> list[dict[str, Any]]:
        with self.archives._transaction() as db:
            return [
                dict(row) for row in db.execute("SELECT * FROM photo_history ORDER BY turn,channel")
            ]

    def status(self) -> dict[str, Any]:
        rows = self.rows()
        return {
            "channels": len(rows),
            "states": dict(Counter(r["state"] for r in rows)),
            **{key: sum(r[key] for r in rows) for key in ("scanned", "captured", "gaps")},
            "full_history": False,
            "scope": "pinned_human_first_attachment_existing_text_channels",
        }

    @contextmanager
    def exclusive(self) -> Iterator[None]:
        # Separate job lock: source transactions must remain available during network I/O.
        path = self.archives.path.with_name("photo-history.lock")
        self.learning.store.identity()
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            _private(path)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise LearningUnavailable("Photo history is already running") from error
            yield
        finally:
            os.close(fd)

    def checkpoint(
        self,
        row: dict[str, Any],
        *,
        before: int,
        scanned: int,
        captured: int,
        gaps: int,
        state: str,
    ) -> None:
        if not 0 <= before <= row["before_id"]:
            raise LearningUnavailable("Backward history cursor must not move forward")
        if self.learning.store.identity() != self.learning.identity:
            raise LearningUnavailable("Photo history source identity changed")
        with self.archives._transaction() as db:
            changed = db.execute(
                "UPDATE photo_history SET before_id=?,scanned=scanned+?,captured=captured+?,"
                "gaps=gaps+?,state=?,updated_at=?,turn=(SELECT MAX(turn)+1 FROM photo_history) "
                "WHERE channel=? AND before_id=?",
                (
                    before,
                    scanned,
                    captured,
                    gaps,
                    state,
                    _time(self.learning.clock()),
                    row["channel"],
                    row["before_id"],
                ),
            ).rowcount
            if changed != 1:
                raise LearningUnavailable("Photo history checkpoint changed")

    async def channel(self, client: discord.Client, channel_id: int) -> discord.TextChannel | None:
        if self.learning.store.identity() != self.learning.identity or not self.learning.verified:
            raise LearningUnavailable("Photo history source identity unavailable")
        if channel_id not in self.learning.channel_ids:
            return None
        guild = await client.fetch_guild(self.learning.identity.guild_id)
        if guild.id != self.learning.identity.guild_id:
            raise LearningUnavailable("Photo history guild mismatch")
        client._connection._add_guild(guild)
        channel = await client.fetch_channel(channel_id)
        if channel.id != channel_id:
            raise LearningUnavailable("Photo history channel mismatch")
        if not isinstance(channel, discord.TextChannel) or not self.learning.accepts(channel):
            return None
        user = client.user
        if user is None:
            raise LearningUnavailable("Authenticated photo history client required")
        member = await channel.guild.fetch_member(user.id)
        permissions = channel.permissions_for(member)
        if not permissions.view_channel or not permissions.read_message_history:
            raise PhotoAccessUnavailable("Photo history access unavailable")
        return channel

    async def scan(self, client: discord.Client, *, pages: int = 1) -> dict[str, Any]:
        if type(pages) is not int or not 1 <= pages <= MAX_PAGES:
            raise LearningUnavailable("Photo history requires one to six bounded pages")
        result = {"pages": 0, "scanned": 0, "captured": 0, "gaps": 0}
        attempts = 0
        self.photos.client = client
        # One page/channel/round, oldest checkpoint first, to avoid starving quiet channels.
        async with asyncio.timeout(90):
            with self.exclusive():
                for _ in range(pages):
                    rows = [
                        r for r in self.rows() if r["state"] not in {"complete", "out_of_scope"}
                    ]
                    if not rows or attempts >= MAX_CAPTURES:
                        break
                    row = rows[0]
                    before = row["before_id"]
                    counts = {"scanned": 0, "captured": 0, "gaps": 0}
                    state = "scanning"
                    try:
                        async with asyncio.timeout(8):
                            channel = await self.channel(client, row["channel"])
                            if channel is None:
                                state = "out_of_scope"
                                batch = []
                            else:
                                batch = [
                                    m
                                    async for m in channel.history(
                                        limit=PAGE_SIZE,
                                        before=discord.Object(id=before),
                                        oldest_first=False,
                                    )
                                ]
                        if channel is not None:
                            ids = [m.id for m in batch]
                            if ids != sorted(set(ids), reverse=True) or any(
                                mid >= before for mid in ids
                            ):
                                raise LearningUnavailable("Invalid backward history page")
                            result["pages"] += 1
                            consumed = True
                            for message in batch:
                                if (
                                    message.channel.id != channel.id
                                    or message.guild is None
                                    or message.guild.id != self.learning.identity.guild_id
                                ):
                                    raise LearningUnavailable("Photo history page changed scope")
                                candidate = (
                                    message.author.id == self.learning.identity.user_id
                                    and self.photos.eligible(message)
                                    and any(
                                        a.url in image_urls(message) for a in message.attachments
                                    )
                                )
                                if candidate:
                                    if attempts >= MAX_CAPTURES:
                                        consumed = False
                                        break
                                    if len(self.photos.store.rows()) >= MAX_PHOTOS:
                                        state, consumed = "capacity", False
                                        break
                                    attempts += 1
                                    try:
                                        async with asyncio.timeout(12):
                                            counts["captured"] += await self.photos.capture(message)
                                    except (
                                        aiohttp.ClientError,
                                        discord.HTTPException,
                                        TimeoutError,
                                        OSError,
                                        ValueError,
                                        Image.DecompressionBombError,
                                    ):
                                        counts["gaps"] += 1
                                        self.photos.store.gap(
                                            channel.id,
                                            message.id,
                                            "history_capture_unavailable",
                                            now=self.learning.clock(),
                                        )
                                before = message.id
                                counts["scanned"] += 1
                            # Empty history can mean denied READ_MESSAGE_HISTORY. Fresh permission
                            # checks precede exhaustion, including after a short page.
                            if consumed and len(batch) < PAGE_SIZE:
                                async with asyncio.timeout(6):
                                    if await self.channel(client, row["channel"]) is None:
                                        raise LearningUnavailable(
                                            "Photo history source scope changed"
                                        )
                                state = "complete"
                    except (discord.HTTPException, TimeoutError, PhotoAccessUnavailable):
                        state = "unavailable"
                        counts["gaps"] += 1
                    self.checkpoint(row, before=before, state=state, **counts)
                    for key, count in counts.items():
                        result[key] += count
        return result | {"provider_calls": 0, "discord_writes": 0, "status": self.status()}


async def run(command: str, *, pages: int) -> dict[str, Any]:
    settings = Settings.from_env()
    learning = MessageIngestor(
        LearningStore(
            settings.learning_store_path, retention_days=settings.learning_retention_days
        ),
        settings.allowed_channel_ids,
    )
    async with AsyncExitStack() as stack:
        api = await stack.enter_async_context(
            AsyncOpenAI(api_key=settings.openai_api_key, max_retries=0)
        )
        responder = OpenAITruaxResponder(
            api,
            model=settings.openai_model,
            max_output_tokens=settings.openai_max_output_tokens,
            budget=UsageLedger(settings.usage_ledger_path),
            purpose="maintenance",
        )
        history = PhotoHistory(PhotoMemory(learning, responder))
        if command == "init":
            history.initialize(now=datetime.now(UTC))
        if command != "scan":
            return history.status()
        # Plain HTTP only: no gateway, readiness heartbeat, provider call or study.
        client = await stack.enter_async_context(discord.Client(intents=discord.Intents.none()))
        await client.login(settings.discord_token)
        guild = await client.fetch_guild(learning.identity.guild_id)
        client._connection._add_guild(guild)
        await learning.verify_member(client)
        return await history.scan(client, pages=pages)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bounded operator recovery of older original photos"
    )
    parser.add_argument("command", choices=("init", "scan", "status"))
    parser.add_argument("--pages", type=int, choices=range(1, MAX_PAGES + 1), default=1)
    args = parser.parse_args()
    try:
        print(json.dumps(asyncio.run(run(args.command, pages=args.pages))))
    except Exception:
        # Transport/source exceptions can include private payloads or credentials.
        parser.exit(
            2, "Photo history unavailable; inspect private source access and checkpoints.\n"
        )


if __name__ == "__main__":
    main()
