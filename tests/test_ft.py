import requests

from ft import get_ft_articles
from guardian import Article

class DummyResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

def test_get_ft_articles_parses_links(monkeypatch):
    html = """
    <div data-trackable-context-storygroup-title='Top Stories'>
        <div class='story-group__title'>Top Stories</div>
        <div class='headline js-teaser-headline'>
            <a data-trackable='heading-link' href='/a1'>Title 1</a>
        </div>
        <div class='headline js-teaser-headline'>
            <a data-trackable='heading-link' href='/a2'>Title 2</a>
        </div>
    </div>
    """

    def fake_get(url, timeout=10):
        return DummyResponse(html)

    monkeypatch.setattr(requests, "get", fake_get)

    articles = get_ft_articles("http://example.com")

    assert articles == [
        Article(url="https://www.ft.com/a1", title="Title 1", section="Top Stories"),
        Article(url="https://www.ft.com/a2", title="Title 2", section="Top Stories"),
    ]

