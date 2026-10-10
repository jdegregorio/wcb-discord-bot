"""One private corpus study in a disposable graph clone, reporting counts only."""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import tempfile
import time
from contextlib import closing
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from trubot.app import build_client
from trubot.config import Settings
from trubot.graph import GraphStore


async def evaluate():
    settings = Settings.from_env()
    client = build_client(settings, spending_purpose="maintenance")
    learning = client._learning
    if learning is None:
        raise RuntimeError("Verified source state required")
    await client.login(settings.discord_token)
    try:
        identity = learning.identity
        member = await client.http.get_member(identity.guild_id, identity.user_id)
        if int(member["user"]["id"]) != identity.user_id or member["user"].get("bot"):
            raise RuntimeError("Pinned human membership unavailable")
        learning.verified = True
        original = GraphStore(learning.store)
        with tempfile.TemporaryDirectory(
            prefix="private-study-", dir=original.path.parent
        ) as temporary:
            graph = GraphStore(learning.store)
            graph.path = Path(temporary) / "memory-graph.sqlite3"
            # Consistent online copy under the shared learning lock; source databases
            # and the spending ledger are never copied, replaced or reinitialized.
            with (
                learning.store._transaction(),
                closing(sqlite3.connect(original.path.as_uri() + "?mode=ro", uri=True)) as source,
                closing(sqlite3.connect(graph.path)) as target,
            ):
                source.backup(target)
                if target.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise RuntimeError("Disposable graph integrity failed")
            graph.path.chmod(0o600)
            client._distiller.store.graph = graph
            channels = {}
            for channel_id in learning.channel_ids:
                channel = MagicMock(spec=discord.TextChannel)
                channel.id, channel.guild = channel_id, SimpleNamespace(id=identity.guild_id)
                channel.send = AsyncMock()

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

                channel.fetch_message = fetch
                channels[channel_id] = channel
            before = graph.status()
            actual_study = client._responder.study_json
            calls, packets = [], []

            async def study(**kwargs):
                calls.append(kwargs["name"])
                packet = kwargs["payload"]["sources"]
                packets.append(
                    {
                        "passages": len(packet),
                        "unknown_dates": sum(p["unknown_date"] for p in packet),
                        "adjacent_context_blocks": sum(len(p["adjacent_context"]) for p in packet),
                    }
                )
                return await actual_study(**kwargs)

            started = time.perf_counter()
            with (
                patch.object(client, "get_channel", side_effect=channels.get),
                patch.object(client._responder, "study_json", side_effect=study),
            ):
                await client._distiller.cycle(client)
            after = graph.status()
            print(
                json.dumps(
                    {
                        "private_sources": True,
                        "disposable_graph": True,
                        "no_discord_writes": all(
                            c.send.await_count == 0 for c in channels.values()
                        ),
                        "provider_calls": len(calls),
                        "packets": packets,
                        "study_ms": round((time.perf_counter() - started) * 1000, 2),
                        "studies_before": before["studies"],
                        "studies_after": after["studies"],
                        "qualified_observations_added": sum(
                            after["nodes"].get(k, 0) - before["nodes"].get(k, 0)
                            for k in ["claim", "preference", "style", "humor"]
                        ),
                        "limitation": (
                            "One bounded corpus packet is a learning-path probe, "
                            "not a fidelity or coverage benchmark."
                        ),
                    }
                )
            )
            if not calls:
                raise RuntimeError("No accounted corpus study executed")
    finally:
        await client.close()


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    try:
        asyncio.run(evaluate())
    except Exception as error:
        raise SystemExit("Private study unavailable: " + type(error).__name__) from None
