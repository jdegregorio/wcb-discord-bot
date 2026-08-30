import tempfile
import time
import unittest
from pathlib import Path

from healthcheck import is_ready


class HealthcheckTests(unittest.TestCase):
    def test_missing_file_is_not_ready(self):
        self.assertFalse(is_ready(Path("/definitely/missing/wcb-ready"), 60))

    def test_recent_file_is_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ready"
            path.touch()
            self.assertTrue(is_ready(path, 60))

    def test_stale_file_is_not_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ready"
            path.touch()
            old = time.time() - 120
            import os
            os.utime(path, (old, old))
            self.assertFalse(is_ready(path, 60))


if __name__ == "__main__":
    unittest.main()
