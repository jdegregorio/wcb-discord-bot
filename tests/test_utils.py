import unittest
from unittest.mock import patch

from utils import create_trello_card


class TrelloTests(unittest.TestCase):
    @patch("utils.requests.request")
    def test_create_card_uses_timeout_and_returns_json(self, request):
        request.return_value.json.return_value = {"id": "card-1"}
        result = create_trello_card("list", "name", "description", "key", "token")
        request.return_value.raise_for_status.assert_called_once_with()
        self.assertEqual(result["id"], "card-1")
        self.assertEqual(request.call_args.kwargs["timeout"], 15)


if __name__ == "__main__":
    unittest.main()
