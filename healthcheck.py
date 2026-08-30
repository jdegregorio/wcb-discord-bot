import os
import sys
import time
from pathlib import Path


def is_ready(path: Path, max_age_seconds: int) -> bool:
    try:
        age = time.time() - path.stat().st_mtime
    except FileNotFoundError:
        return False
    return 0 <= age <= max_age_seconds


if __name__ == "__main__":
    ready_file = Path(os.getenv("HEALTH_READY_FILE", "/tmp/wcb-bot-ready"))
    max_age = int(os.getenv("HEALTH_MAX_AGE_SECONDS", "180"))
    sys.exit(0 if is_ready(ready_file, max_age) else 1)
