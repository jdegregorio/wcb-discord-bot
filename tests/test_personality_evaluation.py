"""Regression tests for the no-post live evaluation harness, without network access."""

import json
import runpy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

ROOT = Path(__file__).parents[1]
EVALUATE = runpy.run_path(str(ROOT / "scripts/evaluate_personality.py"))["evaluate"]
FIXTURES = ROOT / "tests/fixtures/emotional_judgment.json"


@pytest.mark.asyncio
async def test_evaluation_exercises_all_triggers_and_records_only_synthetic_posts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "discord-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-secret")
    calls = []

    async def create(**request: object) -> SimpleNamespace:
        calls.append(request)
        focused = request["input"][-1]["content"]
        reply = "<NO_REPLY>" if "Morgan, can you" in focused else "That comeback was worth it."
        return SimpleNamespace(
            output_text=reply,
            usage=SimpleNamespace(
                input_tokens=100,
                input_tokens_details=SimpleNamespace(cached_tokens=80),
                output_tokens=10,
            ),
        )

    api = SimpleNamespace(responses=SimpleNamespace(create=create), close=AsyncMock())
    with patch("trubot.app.AsyncOpenAI", return_value=api):
        report = await EVALUATE(FIXTURES, 1)

    assert report["discord_writes"] == 0
    assert report["rubric_review_required"] is True
    assert report["requests"] == 10
    assert report["successful_responses"] == 10
    assert report["missing_usage_responses"] == 0
    assert report["usage"] == {
        "input_tokens": 1000,
        "cached_input_tokens": 800,
        "output_tokens": 100,
    }
    assert all(result["transport_pass"] for result in report["results"])
    assert {result["mode"] for result in report["results"]} == {"direct", "reaction", "follow_up"}
    assert api.close.await_count == 10
    assert all(request["store"] is False for request in calls)
    assert all("Emotional engagement:" in request["instructions"] for request in calls)
    # No test reply is sent through discord.py's real HTTP transport.
    assert len(report["results"]) == 10


@pytest.mark.asyncio
async def test_provider_failure_fails_evaluation_instead_of_scoring_fallback_as_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "discord-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-secret")
    api = SimpleNamespace(
        responses=SimpleNamespace(create=AsyncMock(side_effect=TimeoutError)),
        close=AsyncMock(),
    )
    with patch("trubot.app.AsyncOpenAI", return_value=api):
        report = await EVALUATE(FIXTURES, 1)

    assert report["requests"] == 10
    assert all(not result["transport_pass"] for result in report["results"])
    assert report["successful_responses"] == 0
    assert api.close.await_count == 10


@pytest.mark.parametrize("samples", [0, 4])
@pytest.mark.asyncio
async def test_evaluation_rejects_unbounded_runs_before_using_credentials(samples: int) -> None:
    with patch("trubot.app.AsyncOpenAI") as api, pytest.raises(ValueError, match="Samples"):
        await EVALUATE(FIXTURES, samples)
    api.assert_not_called()


@pytest.mark.parametrize("cases", [[], [{}] * 13, {}])
@pytest.mark.asyncio
async def test_evaluation_rejects_unbounded_cases(tmp_path: Path, cases: object) -> None:
    fixtures = tmp_path / "cases.json"
    fixtures.write_text(json.dumps(cases))
    with patch("trubot.app.AsyncOpenAI") as api, pytest.raises(ValueError, match="synthetic"):
        await EVALUATE(fixtures, 1)
    api.assert_not_called()
