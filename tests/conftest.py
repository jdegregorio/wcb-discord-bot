from pathlib import Path

import pytest

from trubot.budget import UsageLedger


@pytest.fixture(autouse=True)
def private_test_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> UsageLedger:
    ledger = UsageLedger.initialize(tmp_path / "usage.sqlite3")
    monkeypatch.setenv("TRUBOT_USAGE_LEDGER_PATH", str(ledger.path))
    return ledger
