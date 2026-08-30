import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from insult import insult_jim
from truaxbot import generate_truax_reply, normalize_truax_reply


class OpenAICallTests(unittest.TestCase):
    @patch("truaxbot.OpenAI")
    def test_truax_uses_configured_timeout(self, client_class):
        client_class.return_value.responses.create.return_value = SimpleNamespace(output_text=" Hot ")
        with patch.dict(os.environ, {"OPENAI_TIMEOUT_SECONDS": "12"}):
            self.assertEqual(generate_truax_reply([{"role": "user", "content": "hello"}]), "Hot")
        client_class.assert_called_once_with(timeout=12.0)

    def test_truax_reply_removes_bot_speaker_prefix(self):
        self.assertEqual(normalize_truax_reply("trubot: Hot"), "Hot")
        self.assertEqual(normalize_truax_reply("Andrew Truax: Hot"), "Hot")

    def test_truax_reply_preserves_non_speaker_colon(self):
        self.assertEqual(normalize_truax_reply("Hot take: Thomas Jones rules"), "Hot take: Thomas Jones rules")

    @patch("insult.OpenAI")
    def test_insult_uses_configured_timeout(self, client_class):
        client_class.return_value.responses.create.return_value = SimpleNamespace(output_text=" Joke ")
        with patch.dict(os.environ, {"OPENAI_TIMEOUT_SECONDS": "9"}):
            result = insult_jim(type="joke", temperature=0.8)
        self.assertEqual(result["output"], "Joke")
        client_class.assert_called_once_with(timeout=9.0)


if __name__ == "__main__":
    unittest.main()
