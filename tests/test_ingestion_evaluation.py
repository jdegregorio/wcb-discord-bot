import importlib.util
from pathlib import Path


async def test_synthetic_installed_handler_harness_passes_without_external_io():
    path = Path(__file__).parents[1] / "scripts" / "evaluate_ingestion.py"
    spec = importlib.util.spec_from_file_location("ingestion_evaluation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = await module.evaluate()
    assert report["acceptance_pass"]
    assert len(report["results"]) == 8
    assert report["api_calls"] == 0
    assert report["discord_writes"] == 0
