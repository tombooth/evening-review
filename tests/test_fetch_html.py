import pytest
import requests

from cache import set_db_path
from main import fetch_html


class DummyResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


@pytest.fixture(autouse=True)
def temp_cache(tmp_path):
    cache_file = tmp_path / "cache.db"
    set_db_path(str(cache_file))
    yield


def test_fetch_html_caches(monkeypatch):
    calls = []

    def fake_get(url, headers=None, timeout=10):
        calls.append(url)
        return DummyResponse("<html>OK</html>")

    monkeypatch.setattr(requests, "get", fake_get)

    first = fetch_html("https://example.com")
    second = fetch_html("https://example.com")

    assert first == "<html>OK</html>"
    assert second == "<html>OK</html>"
    assert len(calls) == 1
