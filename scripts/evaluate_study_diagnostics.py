"""Installed synthetic study failures: no provider, Discord client, or live state access."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import tempfile
from contextlib import ExitStack
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord
from openai import APIConnectionError

from trubot.budget import BudgetExceeded, BudgetUnavailable
from trubot.distillation import GraphDistiller
from trubot.graph import GraphStore
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable, SourceMessage
from trubot.openai_responder import ResponderError

SENTINEL = "PRIVATE_SOURCE_CREDENTIAL_SENTINEL"
FAULTS = {
    "budget_exhausted": BudgetExceeded,
    "budget_unavailable": BudgetUnavailable,
    "timeout": TimeoutError,
    "provider_connection": lambda message: APIConnectionError(message=message, request=MagicMock()),
    "responder_unavailable": ResponderError,
    "unexpected_error": RuntimeError,
}


class Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.events = []

    def emit(self, record):
        self.events.append(record.getMessage())


async def evaluate(*, require_diagnostics=False):
    now = datetime.now(UTC)
    identifier = discord.utils.time_snowflake(now - timedelta(days=1))
    audit = {
        "verified": True,
        "exact_name_match": True,
        "user_id": "42",
        "guild_id": "77",
        "username": "synthetic-person",
        "member_username": "synthetic-person",
        "allowed_channel_ids": ["10"],
        "source_channels": ["10"],
        "message_ids": [str(identifier)],
        "observed_at": now.isoformat(),
    }
    logger = logging.getLogger("trubot.distillation")
    capture, old_level = Capture(), logger.level
    logger.addHandler(capture)
    logger.setLevel(logging.DEBUG)
    results = []
    try:
        for case in [
            *FAULTS,
            "source_refresh",
            "source_validation",
            "storage",
            "no_proposal",
            "proposal_invalid",
            "review_invalid",
            "review_declined",
            "accepted",
        ]:
            with tempfile.TemporaryDirectory(prefix="trubot-study-probe-") as temporary:
                learning = LearningStore.initialize(
                    Path(temporary) / "learning.sqlite3", audit, now=now
                )
                text = "I prefer caramel ice cream for dessert."
                learning.observe(
                    SourceMessage(
                        id=identifier,
                        channel_id=10,
                        guild_id=77,
                        author_id=42,
                        bot=False,
                        webhook=False,
                        created_at=now - timedelta(days=1),
                        edited_at=None,
                        observed_at=now,
                        content=text,
                        authoritative=True,
                    ),
                    now=now,
                )
                graph = GraphStore.initialize(learning)
                ingestor = MessageIngestor(learning, frozenset({10}), clock=lambda: now)
                ingestor.verified = True
                # Synthetic source already authoritatively verified at the fixed probe clock.
                ingestor.refresh = AsyncMock()
                responder = SimpleNamespace(study_json=AsyncMock())
                distiller = GraphDistiller(ingestor, responder, clock=lambda: now)
                client = MagicMock(spec=discord.Client)
                client.get_channel.return_value = MagicMock(spec=discord.TextChannel)

                async def generate(case=case, text=text, **kwargs):
                    await kwargs["source_check"]()
                    if kwargs["name"] == "memory_review":
                        if case == "review_invalid":
                            return {"accepted": SENTINEL}
                        return {
                            "accepted": case != "review_declined",
                            "basis": "Synthetic review only.",
                            "contradicts": [],
                        }
                    if case == "no_proposal":
                        return {"observations": []}
                    if case == "proposal_invalid":
                        return {"observations": [{"private": SENTINEL}]}
                    return {
                        "observations": [
                            {
                                "kind": "preference",
                                "support_basis": "explicit_self_report",
                                "summary": "A specific synthetic dessert statement.",
                                "conditions": "Only this synthetic exchange.",
                                "supports": [{"source": 0, "quote": text}],
                                "aliases": ["caramel", "dessert"],
                            }
                        ]
                    }

                responder.study_json.side_effect = generate
                start = len(capture.events)
                with ExitStack() as stack:
                    if case in FAULTS:
                        responder.study_json.side_effect = FAULTS[case](SENTINEL)
                    elif case == "source_refresh":
                        ingestor.refresh.side_effect = TimeoutError(SENTINEL)
                    elif case == "source_validation":
                        stack.enter_context(
                            patch.object(
                                distiller.store, "check", side_effect=LearningUnavailable(SENTINEL)
                            )
                        )
                    elif case == "storage":
                        stack.enter_context(
                            patch.object(
                                distiller.store.graph, "populate", side_effect=OSError(SENTINEL)
                            )
                        )
                    await distiller.cycle(client)
                first_events = capture.events[start:]
                requests = responder.study_json.await_count
                if case != "storage":
                    restarted = GraphDistiller(ingestor, responder, clock=lambda: now)
                    await restarted.cycle(client)
                paced = responder.study_json.await_count == requests
                expected_stage = (
                    "source_refresh"
                    if case == "source_refresh"
                    else "source_validation"
                    if case == "source_validation"
                    else "source_population"
                    if case == "storage"
                    else "extraction"
                )
                expected_reason = (
                    "timeout"
                    if case == "source_refresh"
                    else "evidence_unavailable"
                    if case == "source_validation"
                    else "storage_unavailable"
                    if case == "storage"
                    else case
                )
                completed = case in {
                    "no_proposal",
                    "proposal_invalid",
                    "review_invalid",
                    "review_declined",
                    "accepted",
                }
                category = any(
                    f"reason={expected_reason}" in event
                    and (completed or f"stage={expected_stage}" in event)
                    for event in first_events
                )
                private = any(
                    SENTINEL in event or text in event or str(identifier) in event
                    for event in capture.events[start:]
                )
                result = {
                    "id": case,
                    "diagnosed": category,
                    "pacing_preserved": paced,
                    "private_payload_absent": not private,
                    "study_requests": requests,
                    "observations": graph.status()["nodes"].get("preference", 0),
                }
                result["passed"] = (
                    paced
                    and not private
                    and (category or not require_diagnostics)
                    and result["observations"] == int(case == "accepted")
                )
                results.append(result)
    finally:
        logger.removeHandler(capture)
        logger.setLevel(old_level)
    report = {
        "synthetic_only": True,
        "provider_calls": 0,
        "discord_writes": 0,
        "live_state_access": False,
        "cases": results,
        "diagnosed": sum(r["diagnosed"] for r in results),
        "total": len(results),
        "distinct_pause_events": len(set(e for e in capture.events if "Graph study paused" in e)),
        "passed": all(r["passed"] for r in results),
        "limitation": (
            "Fault injection proves diagnosis and failure isolation, "
            "not measured reply-quality improvement."
        ),
    }
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-diagnostics", action="store_true")
    args = parser.parse_args()
    report = asyncio.run(evaluate(require_diagnostics=args.require_diagnostics))
    print(json.dumps(report))
    if not report["passed"]:
        raise SystemExit(1)
