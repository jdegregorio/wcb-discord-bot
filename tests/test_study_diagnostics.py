import asyncio
import importlib.util
import logging
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import discord
import pytest
from openai import APIStatusError, APITimeoutError
from test_distillation import seed, worker
from test_learning import AUDIT, NOW

from trubot.archives import ArchiveStore
from trubot.distillation import StudyStore, _pause_reason
from trubot.graph import GraphStore
from trubot.learning import LearningStore, LearningUnavailable
from trubot.openai_responder import StudyContextExceeded, StudyResponseInvalid


@pytest.fixture
def stores(tmp_path):
    learning = LearningStore.initialize(tmp_path / "learning.sqlite3", AUDIT, now=NOW)
    return learning, ArchiveStore.initialize(learning), GraphStore.initialize(learning)


async def test_installed_fault_probe_covers_diagnosis_privacy_pacing_and_rejection():
    spec = importlib.util.spec_from_file_location(
        "study_diagnostics", Path(__file__).parents[1] / "scripts/evaluate_study_diagnostics.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = await module.evaluate(require_diagnostics=True)
    assert report["passed"] and report["diagnosed"] == report["total"] == 14
    assert report["provider_calls"] == report["discord_writes"] == 0
    assert not report["live_state_access"]


@pytest.mark.parametrize(
    "error,reason",
    [
        (StudyContextExceeded("private payload"), "context_bound"),
        (StudyResponseInvalid("private result"), "provider_response_invalid"),
        (APITimeoutError(request=MagicMock()), "timeout"),
        (sqlite3.DatabaseError("private path"), "storage_unavailable"),
        *[
            (
                APIStatusError(
                    "private body", response=MagicMock(status_code=status), body={"private": "text"}
                ),
                reason,
            )
            for status, reason in [
                (429, "provider_rate_limited"),
                (401, "provider_access"),
                (403, "provider_access"),
                (500, "provider_status"),
            ]
        ],
        *[
            (
                discord.HTTPException(MagicMock(status=status, reason="private"), "private text"),
                reason,
            )
            for status, reason in [(403, "discord_access"), (500, "discord_transport")]
        ],
    ],
)
def test_typed_reasons_never_serialize_exception_body(error, reason):
    assert _pause_reason(error) == reason


def test_selection_reports_pacing_separately_from_absent_sources(stores):
    store = StudyStore(stores[2])
    assert store.select(now=NOW, channel_ids=frozenset({10})).reason == "no_candidate"
    assert store.prepare(now=NOW, channel_ids=frozenset({10})) is None
    seed(stores)
    selection = store.select(now=NOW, channel_ids=frozenset({10}))
    assert selection.study is not None and selection.reason == "ready"
    assert "Study(" not in repr(selection)  # Never expose private study snapshots.
    assert store.select(now=NOW, channel_ids=frozenset({10})).reason == "paced"


async def test_cancelled_study_is_not_a_failure_and_restart_keeps_lease(stores, caplog):
    seed(stores)
    distiller, client, responder, _ = worker(stores)
    responder.study_json.side_effect = asyncio.CancelledError("private source")
    with caplog.at_level(logging.DEBUG), pytest.raises(asyncio.CancelledError):
        await distiller.cycle(client)
    assert "Graph study paused" not in caplog.text and "private source" not in caplog.text
    responder.study_json.reset_mock()
    await worker(stores)[0].cycle(client)
    responder.study_json.assert_not_awaited()


async def test_pre_request_source_failure_is_reported_as_validation_not_provider(stores, caplog):
    seed(stores)
    distiller, client, responder, _ = worker(stores)

    async def fail_check(**kwargs):
        distiller.ingestor.verified = False
        await kwargs["source_check"]()

    responder.study_json.side_effect = fail_check
    await distiller.cycle(client)
    assert "stage=source_validation reason=evidence_unavailable" in caplog.text
    assert "provider" not in caplog.text
    assert not stores[2].lookup("dessert", guild_id=77, now=NOW)


async def test_failed_graph_commit_is_isolated_and_does_not_claim_completion(stores, caplog):
    seed(stores)
    distiller, client, _, _ = worker(stores)
    with patch.object(
        distiller.store, "finish", side_effect=LearningUnavailable("private support")
    ):
        await distiller.cycle(client)
    assert "stage=commit reason=evidence_unavailable" in caplog.text
    assert "Graph study completed" not in caplog.text and "private support" not in caplog.text
    assert not stores[2].lookup("dessert", guild_id=77, now=NOW)


async def test_normal_skips_do_not_warn_each_background_poll(stores, caplog):
    distiller, client, responder, _ = worker(stores)
    with caplog.at_level(logging.DEBUG):
        distiller.ingestor.verified = False
        await distiller.cycle(client)
        distiller.ingestor.verified = True
        await distiller.cycle(client)
        seed(stores)
        await distiller.cycle(client)
        await distiller.cycle(client)
    assert "reason=verification_pending" in caplog.text
    assert "reason=no_candidate" in caplog.text and "reason=paced" in caplog.text
    assert not any(r.levelno >= logging.WARNING for r in caplog.records)
    assert responder.study_json.await_count == 2
