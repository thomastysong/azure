import types
import unittest

from intune_client import IntuneClient


class DummyCredential:
    def __init__(self, token: str = "dummy-token"):
        self._token = token

    def get_token(self, *_):
        return types.SimpleNamespace(token=self._token)


class TestClient(unittest.TestCase):
    def test_headers(self):
        client = IntuneClient(DummyCredential())
        headers = client._headers()
        self.assertEqual(headers["Authorization"], "Bearer dummy-token")
        self.assertEqual(headers["Content-Type"], "application/json")


if __name__ == "__main__":
    unittest.main()
