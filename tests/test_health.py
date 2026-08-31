import os
from pathlib import Path
from unittest.mock import patch

import pytest

from trubot.health import ReadinessFile, is_ready, main


def test_readiness_age_checks_missing_recent_stale_and_future_files(tmp_path: Path) -> None:
    path = tmp_path / "ready"
    assert not is_ready(path, 60, now=100)

    path.touch()
    os.utime(path, (50, 50))
    assert is_ready(path, 60, now=100)
    assert not is_ready(path, 40, now=100)
    assert not is_ready(path, 60, now=40)


@pytest.mark.asyncio
async def test_readiness_lifecycle_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "ready"
    readiness = ReadinessFile(path, refresh_seconds=0.01)

    await readiness.start()
    await readiness.start()
    assert path.exists()
    await readiness.stop()
    await readiness.stop()
    assert not path.exists()


def test_healthcheck_main_returns_process_status(tmp_path: Path) -> None:
    path = tmp_path / "ready"
    path.touch()
    with (
        patch.dict(
            os.environ,
            {"HEALTH_READY_FILE": str(path), "HEALTH_MAX_AGE_SECONDS": "60"},
            clear=True,
        ),
        pytest.raises(SystemExit) as exit_info,
    ):
        main()
    assert exit_info.value.code == 0

    path.unlink()
    with (
        patch.dict(
            os.environ,
            {"HEALTH_READY_FILE": str(path), "HEALTH_MAX_AGE_SECONDS": "60"},
            clear=True,
        ),
        pytest.raises(SystemExit) as exit_info,
    ):
        main()
    assert exit_info.value.code == 1


def test_healthcheck_rejects_invalid_max_age() -> None:
    with (
        patch.dict(os.environ, {"HEALTH_MAX_AGE_SECONDS": "nope"}, clear=True),
        pytest.raises(SystemExit) as exit_info,
    ):
        main()
    assert exit_info.value.code == 2
