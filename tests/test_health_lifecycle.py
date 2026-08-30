import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bot as bot_module


class HealthLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.ready_file = Path(self.directory.name) / "ready"
        self.ready_file_patch = patch.object(bot_module, "READY_FILE", self.ready_file)
        self.ready_file_patch.start()
        bot_module._health_task = None

    async def asyncTearDown(self):
        if bot_module._health_task is not None:
            bot_module._health_task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await bot_module._health_task
            bot_module._health_task = None
        self.ready_file_patch.stop()
        self.directory.cleanup()

    async def test_resume_restarts_health_refresh_after_disconnect(self):
        bot_module._start_health_refresh()
        first_task = bot_module._health_task
        self.assertTrue(self.ready_file.exists())

        await bot_module.on_disconnect()
        self.assertFalse(self.ready_file.exists())
        self.assertIsNone(bot_module._health_task)

        await bot_module.on_resumed()
        self.assertTrue(self.ready_file.exists())
        self.assertIsNot(first_task, bot_module._health_task)
        self.assertFalse(bot_module._health_task.done())


if __name__ == "__main__":
    unittest.main()
