"""Operator-only real Discord smoke with durable, content-free attempt receipts.

Run inside the existing container with its app-scoped environment. No gateway,
background worker, human impersonation, arbitrary prompt or automatic retry.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import os
import re
import tempfile
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import discord

from trubot.app import build_client
from trubot.config import Settings
from trubot.learning import LearningStore, _private

GUILD = 1043023451482505226
CHANNEL = 1043023451482505229
CASES = {
    "attribution": (
        "[Synthetic operator smoke fixture. All people and statements are fictional.] "
        "A chat export labels a copied link preview as Pat. The preview contains "
        "I prefer vanilla. Does that prove Pat personally prefers vanilla? Give a short answer."
    ),
    "care": (
        "[Synthetic operator smoke fixture. Fictional scenario, not personal news.] "
        "A fictional league manager says their old dog died this morning. "
        "Give them a short response."
    ),
    "humor": (
        "[Synthetic operator smoke fixture.] Give me one quick playful Thomas Jones "
        "joke about a deer standing in a trail-camera picture."
    ),
}
STATES = {
    "claimed",
    "verified",
    "probe_sending",
    "probe_sent",
    "dispatching",
    "completed",
    "failed",
    "uncertain",
}
FLAGS = {
    "synthetic_dispatch",
    "human_authored_question",
    "main_gateway_tested",
    "raw_retained",
    "auxiliary_closed",
    "ready_isolated",
    "learning_count_unchanged",
    "transport_pass",
}
COUNTS = {"response_count", "answer_words"}
IDS = {"probe_id", "answer_id"}
FIELDS = (
    FLAGS
    | COUNTS
    | IDS
    | {
        "schema",
        "run_id",
        "case",
        "state",
        "created_at",
        "updated_at",
        "response_sha256",
    }
)


def timestamp():
    return datetime.now(UTC).isoformat()


def sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class Receipt:
    def __init__(self, learning, run_id, case):
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", run_id) or case not in CASES:
            raise ValueError("Invalid smoke identity")
        self.learning = learning
        self.run_id, self.case = run_id, case
        self.directory = learning.path.parent / "smoke-tests" / run_id
        self.path = self.directory / (case + ".json")

    def read(self):
        self.learning.identity()  # Withdrawal remains authoritative for inspection too.
        _private(self.path)
        if self.path.stat().st_size > 8192:
            raise ValueError("Oversized smoke receipt")
        result = json.loads(self.path.read_text())
        if (
            not isinstance(result, dict)
            or set(result) - FIELDS
            or result.get("schema") != 1
            or result.get("run_id") != self.run_id
            or result.get("case") != self.case
            or result.get("state") not in STATES
        ):
            raise ValueError("Invalid smoke receipt")
        for key, value in result.items():
            if key in FLAGS and type(value) is not bool:
                raise ValueError("Invalid smoke flag")
            if key in COUNTS | IDS and (type(value) is not int or not 0 <= value < 2**64):
                raise ValueError("Invalid smoke count")
            if key in {"created_at", "updated_at"} and datetime.fromisoformat(value).tzinfo is None:
                raise ValueError("Missing smoke timezone")
            if key == "response_sha256" and not re.fullmatch(r"[a-f0-9]{64}", value):
                raise ValueError("Invalid smoke digest")
        return result

    def claim(self):
        self.learning.identity()
        _private(self.learning.path)
        root = self.directory.parent
        root.mkdir(mode=0o700, exist_ok=True)
        _private(root)
        self.directory.mkdir(mode=0o700, exist_ok=True)
        _private(self.directory)
        initial = {
            "schema": 1,
            "run_id": self.run_id,
            "case": self.case,
            "state": "claimed",
            "created_at": timestamp(),
            "updated_at": timestamp(),
            "synthetic_dispatch": True,
            "human_authored_question": False,
            "main_gateway_tested": False,
            "raw_retained": False,
            "response_count": 0,
            "transport_pass": False,
            "auxiliary_closed": False,
        }
        try:
            descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return self.read(), False
        with os.fdopen(descriptor, "w") as stream:
            json.dump(initial, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        sync_directory(self.directory)
        sync_directory(root)
        sync_directory(root.parent)
        return initial, True

    def save(self, record):
        self.learning.identity()
        _private(self.path)
        record["updated_at"] = timestamp()
        descriptor, name = tempfile.mkstemp(dir=self.directory, prefix=".receipt-")
        staged = Path(name)
        try:
            with os.fdopen(descriptor, "w") as stream:
                json.dump(record, stream, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(staged, self.path)
            sync_directory(self.directory)
        finally:
            staged.unlink(missing_ok=True)


async def scope(client, settings):
    if (
        settings.development_guild_id != GUILD
        or CHANNEL not in settings.allowed_channel_ids
        or "🍆" not in settings.reaction_emoji_names
    ):
        raise ValueError("Private smoke scope unavailable")
    learning = client._learning
    if learning is None:
        raise ValueError("Learning identity unavailable")
    source = await client.fetch_guild(learning.identity.guild_id)
    client._connection._add_guild(source)
    await learning.verify_member(client)
    if not learning.verified:
        raise ValueError("Pinned human unavailable")
    dev = await client.fetch_guild(GUILD, with_counts=True)
    if dev.id != GUILD or dev.approximate_member_count != 2:
        raise ValueError("Private smoke membership changed")
    owner = await dev.fetch_member(dev.owner_id)
    bot = await dev.fetch_member(client.user.id)
    if (
        owner.bot
        or not bot.bot
        or owner.id != dev.owner_id
        or bot.id != client.user.id
        or owner.id == learning.identity.user_id
    ):
        raise ValueError("Private smoke membership unavailable")
    channel = await dev.fetch_channel(CHANNEL)
    if (
        not isinstance(channel, discord.TextChannel)
        or channel.id != CHANNEL
        or channel.guild.id != GUILD
    ):
        raise ValueError("Private smoke channel unavailable")
    permissions = channel.permissions_for(bot)
    if not (
        permissions.view_channel and permissions.read_message_history and permissions.send_messages
    ):
        raise ValueError("Private smoke permission unavailable")
    if learning.accepts(channel):
        raise ValueError("Development must not be learned")
    client._connection._add_guild(dev)
    dev._add_channel(channel)
    return channel, owner


async def run(settings, receipt):
    record, fresh = receipt.claim()
    if not fresh:
        return record  # Never construct a client or retry a previously claimed attempt.
    client = None
    original = None
    persistence_failed = False
    try:
        isolated = replace(
            settings, ready_file=Path(tempfile.gettempdir()) / ("trubot-smoke-" + uuid4().hex)
        )
        client = build_client(isolated, spending_purpose="maintenance")
        record["ready_isolated"] = client._settings.ready_file != settings.ready_file
        if not record["ready_isolated"]:
            raise ValueError("Smoke readiness not isolated")
        await client.login(settings.discord_token)
        channel, owner = await scope(client, settings)
        record["state"] = "verified"
        receipt.save(record)
        original = client.http.send_message

        async def observed_send(channel_id, *args, **kwargs):
            nonlocal persistence_failed
            if int(channel_id) != CHANNEL:
                raise ValueError("Unexpected smoke destination")
            data = await original(channel_id, *args, **kwargs)
            # Observe the real transport response. Recording must never raise into
            # the handler and provoke its visible-error fallback after a real send.
            try:
                if record["state"] == "probe_sending":
                    record["probe_id"] = int(data["id"])
                else:
                    text = data["content"]
                    record["answer_id"] = int(data["id"])
                    record["response_count"] += 1
                    record["response_sha256"] = hashlib.sha256(text.encode()).hexdigest()
                    record["answer_words"] = len(text.split())
                receipt.save(record)
            except Exception:
                persistence_failed = True
            return data

        client.http.send_message = observed_send
        record["state"] = "probe_sending"
        receipt.save(record)  # An interrupted or ambiguous send consumes the attempt.
        receipt.learning.identity()
        before = client._learning.store.status()["messages"]
        probe = await channel.send(
            CASES[receipt.case], allowed_mentions=discord.AllowedMentions.none()
        )
        if not probe.author.bot or probe.author.id != client.user.id:
            raise ValueError("Synthetic probe authorship unavailable")
        record["state"] = "probe_sent"
        receipt.save(record)
        record["state"] = "dispatching"
        receipt.save(record)
        receipt.learning.identity()
        await client.on_raw_reaction_add(
            SimpleNamespace(
                channel_id=CHANNEL,
                user_id=owner.id,
                message_id=probe.id,
                emoji=SimpleNamespace(name="🍆"),
                member=owner,
            )
        )
        # Fetch the exact observed send, rather than guessing from concurrent history.
        answer = await channel.fetch_message(record["answer_id"])
        if (
            answer.author.id != client.user.id
            or answer.webhook_id is not None
            or hashlib.sha256(answer.content.encode()).hexdigest() != record["response_sha256"]
        ):
            raise ValueError("Smoke readback unavailable")
        record["learning_count_unchanged"] = client._learning.store.status()["messages"] == before
        record["transport_pass"] = record["response_count"] == 1 and not persistence_failed
        record["state"] = "completed" if record["transport_pass"] else "uncertain"
    except BaseException:
        record["state"] = (
            "uncertain"
            if record["state"] in {"probe_sending", "probe_sent", "dispatching"}
            else "failed"
        )
        record["transport_pass"] = False
    finally:
        if client is not None:
            if original is not None:
                client.http.send_message = original
            try:
                await asyncio.wait_for(client.close(), timeout=15)
                record["auxiliary_closed"] = True
            except Exception:
                record["state"], record["transport_pass"] = "uncertain", False
        receipt.save(record)
    return record


async def bounded_run(settings, receipt):
    return await asyncio.wait_for(run(settings, receipt), timeout=120)


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("run", "status"))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--case", choices=tuple(CASES), required=True)
    args = parser.parse_args()
    try:
        settings = Settings.from_env()
        receipt = Receipt(LearningStore(settings.learning_store_path), args.run_id, args.case)
        result = (
            receipt.read()
            if args.action == "status"
            else asyncio.run(bounded_run(settings, receipt))
        )
        exit_code = 0 if result["state"] == "completed" else 2
    except Exception:
        result, exit_code = {"error": "smoke_unavailable"}, 1
    try:
        print(json.dumps(result, sort_keys=True))
    except BrokenPipeError:
        return 2  # The durable receipt, never stdout, is authoritative.
    return exit_code


def main():
    previous = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        return _main()
    finally:
        logging.disable(previous)


if __name__ == "__main__":
    raise SystemExit(main())
