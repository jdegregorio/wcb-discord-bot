import asyncio
import json
import runpy
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, patch

import httpx2 as httpx
import pytest
from openai import APIConnectionError, AsyncOpenAI

from trubot.app import main
from trubot.budget import (
    INPUT_RATE,
    MAINTENANCE_LIMIT,
    OUTPUT_RATE,
    RUNTIME_LIMIT,
    BudgetExceeded,
    BudgetUnavailable,
    UsageLedger,
)
from trubot.conversation import ConversationMessage, ReplyMode
from trubot.openai_responder import EmptyResponseError, OpenAITruaxResponder


def reserve(ledger: UsageLedger, **overrides: Any):
    args = dict(
        model="gpt-6-luna", input_bound=1000, output_bound=180, purpose="runtime", mode="direct"
    )
    return ledger.reserve(**(args | overrides))


def fill(ledger: UsageLedger, amount: int, purpose: str = "runtime") -> None:
    reservation = reserve(ledger, purpose=purpose)
    with sqlite3.connect(ledger.path) as db:
        db.execute(
            "UPDATE attempts SET reserved=?,charged=?,status='settled',settled_month=month "
            "WHERE id=?",
            (amount, amount, reservation.id),
        )


def test_atomic_concurrent_process_connections_cannot_overspend(private_test_ledger: UsageLedger):
    ledger = private_test_ledger
    amount = 1000 * INPUT_RATE + 180 * OUTPUT_RATE
    fill(ledger, RUNTIME_LIMIT - amount)

    def try_reserve(_i):
        try:
            reserve(UsageLedger(ledger.path))
            return True
        except BudgetExceeded:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(try_reserve, range(16))) == 1
    assert UsageLedger(ledger.path).summary()["runtime_usd"] == 18
    assert ledger.summary()["unsettled_attempts"] == 1


def test_maintenance_has_separate_two_dollar_allocation(private_test_ledger: UsageLedger):
    ledger = private_test_ledger
    fill(ledger, RUNTIME_LIMIT)
    reserve(ledger, purpose="maintenance")
    with pytest.raises(BudgetExceeded):
        reserve(ledger)
    fill(ledger, MAINTENANCE_LIMIT, "maintenance")
    with pytest.raises(BudgetExceeded):
        reserve(ledger, purpose="maintenance")


def test_usage_reconciles_cached_tokens_and_persists_without_content(
    private_test_ledger: UsageLedger,
):
    ledger = private_test_ledger
    reservation = reserve(ledger)
    assert (
        ledger.settle(reservation, input_tokens=1000, cached_input_tokens=800, output_tokens=20)
        == 43_000
    )
    with sqlite3.connect(ledger.path) as db:
        row = db.execute("SELECT * FROM attempts").fetchone()
        assert "gpt-6-luna" in row
        assert 1000 in row
        assert 800 in row
    summary = UsageLedger(ledger.path).summary()
    assert summary["runtime_usd"] == 0.000043
    assert summary["unsettled_attempts"] == 0
    with pytest.raises(BudgetUnavailable, match="already settled"):
        ledger.settle(reservation, input_tokens=1000, cached_input_tokens=800, output_tokens=20)


def test_utc_rollover_carries_uncertainty_and_counts_cross_month_settlement(
    private_test_ledger: UsageLedger,
):
    ledger = UsageLedger(
        private_test_ledger.path, clock=lambda: datetime(2026, 10, 31, 23, 59, tzinfo=UTC)
    )
    settled = reserve(ledger)
    ledger.settle(settled, input_tokens=1000, cached_input_tokens=0, output_tokens=1)
    pending = reserve(ledger)
    uncertain = reserve(ledger)
    ledger.uncertain(uncertain)
    november = UsageLedger(ledger.path, clock=lambda: datetime(2026, 11, 1, tzinfo=UTC))
    assert november.summary()["runtime_usd"] == 2 * pending.amount / 1e9
    november.settle(pending, input_tokens=1000, cached_input_tokens=0, output_tokens=1)
    assert november.summary()["runtime_usd"] == (pending.amount + 125500) / 1e9
    december = UsageLedger(ledger.path, clock=lambda: datetime(2026, 12, 1, tzinfo=UTC))
    assert december.summary()["runtime_usd"] == uncertain.amount / 1e9
    with pytest.raises(BudgetUnavailable, match="Clock moved"):
        ledger.check()


@pytest.mark.parametrize("damage", ["missing", "corrupt", "schema", "metadata", "readonly"])
def test_bad_state_fails_closed_and_is_never_recreated(tmp_path: Path, damage: str):
    ledger = UsageLedger.initialize(tmp_path / "damaged.sqlite3")
    if damage == "missing":
        ledger.path.unlink()
    elif damage == "corrupt":
        ledger.path.write_text("not a database")
    elif damage == "readonly":
        ledger.path.chmod(0o400)
    else:
        with sqlite3.connect(ledger.path) as db:
            db.execute("PRAGMA user_version = 9" if damage == "schema" else "DELETE FROM metadata")
    with pytest.raises(BudgetUnavailable):
        ledger.check()
    if damage == "missing":
        assert not ledger.path.exists()


def test_explicit_initialization_cannot_reset_existing_state(private_test_ledger: UsageLedger):
    with pytest.raises(FileExistsError):
        UsageLedger.initialize(private_test_ledger.path)


@pytest.mark.parametrize(
    "override",
    [
        dict(model="gpt-6-astra"),
        dict(input_bound=200001),
        dict(output_bound=4097),
        dict(purpose="other"),
    ],
)
def test_unpriced_or_unbounded_requests_never_reserve(private_test_ledger: UsageLedger, override):
    with pytest.raises(BudgetUnavailable):
        reserve(private_test_ledger, **override)
    assert private_test_ledger.summary()["attempts"] == 0


@pytest.mark.parametrize("tokens", [(1, 2, 1), (-1, 0, 1), (1, 0, True)])
def test_invalid_usage_retains_conservative_charge(private_test_ledger: UsageLedger, tokens):
    item = reserve(private_test_ledger)
    with pytest.raises(BudgetUnavailable, match="Invalid provider"):
        private_test_ledger.settle(
            item, input_tokens=tokens[0], cached_input_tokens=tokens[1], output_tokens=tokens[2]
        )
    assert private_test_ledger.summary()["runtime_usd"] == item.amount / 1e9


def test_usage_overrun_is_recorded_and_halts_all_future_calls(private_test_ledger: UsageLedger):
    item = reserve(private_test_ledger)
    with pytest.raises(BudgetUnavailable, match="exceeded"):
        private_test_ledger.settle(
            item, input_tokens=5000, cached_input_tokens=0, output_tokens=500
        )
    with pytest.raises(BudgetUnavailable, match="reconciliation"):
        reserve(private_test_ledger)
    with sqlite3.connect(private_test_ledger.path) as db:
        assert db.execute("SELECT charged FROM attempts").fetchone()[0] == 875000


def fake_api(create: AsyncMock):
    api = SimpleNamespace(responses=SimpleNamespace(create=create), close=AsyncMock())
    api.with_options = lambda **_kwargs: api
    return api


def fake_response(text="Go Sox.", usage=True):
    return SimpleNamespace(
        output_text=text,
        usage=SimpleNamespace(
            input_tokens=1000,
            input_tokens_details=SimpleNamespace(cached_tokens=800),
            output_tokens=20,
        )
        if usage
        else None,
    )


async def generate(ledger: UsageLedger, create: AsyncMock, *, retries=0, mode=ReplyMode.DIRECT):
    responder = OpenAITruaxResponder(
        cast(AsyncOpenAI, fake_api(create)),
        model="gpt-6-luna",
        max_output_tokens=512,
        budget=ledger,
        max_retries=retries,
    )
    return await responder.reply(
        [ConversationMessage(role="user", content="Casey: Go Sox.")],
        mode=mode,
        safety_id="synthetic-only",
    )


@pytest.mark.asyncio
async def test_retry_reserves_each_attempt_and_retains_failed_upper_bound(
    private_test_ledger: UsageLedger,
):
    error = APIConnectionError(request=httpx.Request("POST", "https://api.openai.com/v1/responses"))
    create = AsyncMock(side_effect=[error, fake_response()])
    with patch("trubot.openai_responder.asyncio.sleep", new_callable=AsyncMock):
        assert await generate(private_test_ledger, create, retries=1) == "Go Sox."
    summary = private_test_ledger.summary()
    assert summary["attempts"] == 2
    assert summary["unsettled_attempts"] == 1
    with sqlite3.connect(private_test_ledger.path) as db:
        statuses = db.execute("SELECT status FROM attempts").fetchall()
        assert statuses == [("uncertain",), ("settled",)]


@pytest.mark.asyncio
async def test_exhausted_budget_blocks_retries_and_all_provider_calls(
    private_test_ledger: UsageLedger,
):
    fill(private_test_ledger, RUNTIME_LIMIT)
    create = AsyncMock()
    with pytest.raises(BudgetExceeded):
        await generate(private_test_ledger, create, retries=2)
    create.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("text,mode", [("", ReplyMode.DIRECT), ("<NO_REPLY>", ReplyMode.FOLLOW_UP)])
async def test_empty_generations_and_abstentions_still_account_usage(
    private_test_ledger: UsageLedger, text, mode
):
    create = AsyncMock(return_value=fake_response(text))
    if text:
        assert await generate(private_test_ledger, create, mode=mode) is None
    else:
        with pytest.raises(EmptyResponseError):
            await generate(private_test_ledger, create)
    assert private_test_ledger.summary()["output_tokens"] == 20


@pytest.mark.asyncio
async def test_missing_usage_remains_charged_at_upper_bound(private_test_ledger: UsageLedger):
    assert (
        await generate(private_test_ledger, AsyncMock(return_value=fake_response(usage=False)))
        == "Go Sox."
    )
    assert private_test_ledger.summary()["unsettled_attempts"] == 1


@pytest.mark.asyncio
async def test_cancelled_provider_request_survives_restart_as_reservation(
    private_test_ledger: UsageLedger,
):
    create = AsyncMock(side_effect=asyncio.CancelledError)
    with pytest.raises(asyncio.CancelledError):
        await generate(private_test_ledger, create)
    assert UsageLedger(private_test_ledger.path).summary()["unsettled_attempts"] == 1


@pytest.mark.asyncio
async def test_provider_exception_preserves_charge_without_retrying_unknown_failure(
    private_test_ledger: UsageLedger,
):
    create = AsyncMock(side_effect=TimeoutError)
    with pytest.raises(TimeoutError):
        await generate(private_test_ledger, create, retries=2)
    assert create.await_count == 1
    assert private_test_ledger.summary()["unsettled_attempts"] == 1


def test_startup_rejects_unsafe_ledger_before_discord_login(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISCORD_TOKEN", "synthetic-only")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-only")
    monkeypatch.setenv("TRUBOT_USAGE_LEDGER_PATH", "/no/such/usage.sqlite3")
    with patch("trubot.app.load_dotenv"), pytest.raises(SystemExit) as exit_info:
        main()
    assert exit_info.value.code == 2


def test_budget_cli_initializes_once_and_reports_content_free_usage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
):
    path = tmp_path / "private" / "usage.sqlite3"
    script = str(Path(__file__).parents[1] / "src/trubot/budget.py")
    monkeypatch.setattr("sys.argv", [script, "init", "--path", str(path)])
    runpy.run_path(script, run_name="__main__")
    assert json.loads(capsys.readouterr().out)["monthly_limit_usd"] == 20
    monkeypatch.setattr("sys.argv", [script, "status", "--path", str(path)])
    runpy.run_path(script, run_name="__main__")
    assert json.loads(capsys.readouterr().out)["attempts"] == 0
    path.write_text("corrupt")
    with pytest.raises(SystemExit, match="BudgetUnavailable"):
        runpy.run_path(script, run_name="__main__")


@pytest.mark.asyncio
async def test_depleted_maintenance_allowance_blocks_real_event_handler_evaluation(
    private_test_ledger: UsageLedger,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("DISCORD_TOKEN", "synthetic-only")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-only")
    fill(private_test_ledger, MAINTENANCE_LIMIT, "maintenance")
    create = AsyncMock(return_value=fake_response())
    evaluate = runpy.run_path(str(Path(__file__).parents[1] / "scripts/evaluate_personality.py"))[
        "evaluate"
    ]
    with patch("trubot.app.AsyncOpenAI", return_value=fake_api(create)):
        report = await evaluate(Path(__file__).parent / "fixtures/emotional_judgment.json", 1)
    create.assert_not_awaited()
    assert report["requests"] == 0
    assert report["discord_writes"] == 0
    assert all(not result["transport_pass"] for result in report["results"])
    assert all(
        result["posts"] == [] for result in report["results"] if result["mode"] == "follow_up"
    )


def test_retention_removes_old_settlements_but_keeps_unresolved_charges(
    private_test_ledger: UsageLedger,
):
    ledger = private_test_ledger
    paid = reserve(ledger)
    ledger.settle(paid, input_tokens=1000, cached_input_tokens=800, output_tokens=20)
    pending = reserve(ledger)
    future = UsageLedger(ledger.path, clock=lambda: datetime.now(UTC) + timedelta(days=460))
    future.check()
    with sqlite3.connect(ledger.path) as db:
        assert db.execute("SELECT id FROM attempts").fetchall() == [(pending.id,)]
    assert future.summary()["runtime_usd"] == pending.amount / 1e9
