import importlib.util
from pathlib import Path


def test_withdrawal_probe_covers_restoration_without_live_provider_or_discord():
    spec = importlib.util.spec_from_file_location(
        "evaluate_withdrawal", Path(__file__).parents[1] / "scripts/evaluate_withdrawal.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.evaluate()
    assert report["passed"] == report["total"] == 7
    assert report["provider_calls"] == report["discord_reads"] == report["discord_writes"] == 0
