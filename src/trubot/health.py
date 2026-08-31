"""Discord-connection readiness lifecycle and container health check."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from contextlib import suppress
from pathlib import Path

from trubot.config import DEFAULT_READY_FILE

logger = logging.getLogger(__name__)


class ReadinessFile:
    def __init__(self, path: Path, *, refresh_seconds: float) -> None:
        self.path = path
        self.refresh_seconds = refresh_seconds
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._refresh(), name="readiness-refresh")

    async def stop(self) -> None:
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        self.path.unlink(missing_ok=True)

    async def _refresh(self) -> None:
        while True:
            await asyncio.sleep(self.refresh_seconds)
            self.path.touch()


def is_ready(path: Path, max_age_seconds: float, *, now: float | None = None) -> bool:
    try:
        modified_at = path.stat().st_mtime
    except (FileNotFoundError, OSError):
        return False
    age = (time.time() if now is None else now) - modified_at
    return 0 <= age <= max_age_seconds


def main() -> None:
    path = Path(os.getenv("HEALTH_READY_FILE", str(DEFAULT_READY_FILE)))
    try:
        max_age = float(os.getenv("HEALTH_MAX_AGE_SECONDS", "180"))
    except ValueError:
        logger.error("HEALTH_MAX_AGE_SECONDS must be a number")
        raise SystemExit(2) from None
    sys.exit(0 if is_ready(path, max_age) else 1)


if __name__ == "__main__":
    main()
