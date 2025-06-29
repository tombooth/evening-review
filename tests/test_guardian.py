import requests
import types

from guardian import get_guardian_articles, Article

class DummyResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

def test_get_guardian_articles_parses_links(monkeypatch):
    html = """
    <section id='news'>
        <h2>News</h2>
        <a href='/a1' aria-label='Title 1'></a>
        <a href='#skip'>skip</a>
    </section>
    <section id='sport'>
        <h2>Sport</h2>
        <a href='/a1' aria-label='Title 1 duplicate'></a>
        <a href='/a2'>Title 2</a>
    </section>
    """

    def fake_get(url, timeout=10, verify=False):
        return DummyResponse(html)

    monkeypatch.setattr(requests, "get", fake_get)

    articles = get_guardian_articles("http://example.com")

    assert articles == [
        Article(url="https://www.theguardian.com/a1", title="Title 1", section="News"),
        Article(url="https://www.theguardian.com/a2", title="Title 2", section="Sport"),
    ]

