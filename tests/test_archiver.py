import pytest
import requests

from archiver import fetch_archive_html


class DummyResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def test_fetch_archive_html_encodes_url(monkeypatch):
    captured = {}

    def fake_get(url, timeout=10):
        captured['url'] = url
        html = '<html><div id="CONTENT"><p>OK</p></div></html>'
        return DummyResponse(html)

    monkeypatch.setattr(requests, 'get', fake_get)

    result = fetch_archive_html('https://example.com/a b')

    assert result == '<p>OK</p>'
    assert captured['url'] == 'http://archive.is/newest/https%3A%2F%2Fexample.com%2Fa%20b'


def test_fetch_archive_html_raises_for_status(monkeypatch):
    def fake_get(url, timeout=10):
        return DummyResponse('boom', status_code=500)

    monkeypatch.setattr(requests, 'get', fake_get)

    with pytest.raises(requests.HTTPError):
        fetch_archive_html('https://example.com')


def test_fetch_archive_html_requires_content(monkeypatch):
    def fake_get(url, timeout=10):
        return DummyResponse('<html><body>nope</body></html>')

    monkeypatch.setattr(requests, 'get', fake_get)

    with pytest.raises(ValueError):
        fetch_archive_html('https://example.com')
