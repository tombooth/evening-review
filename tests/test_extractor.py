from guardian import Article
from models import Scraped


def test_scraped_text_simple():
    html = "<html><body><article><p>First</p><p>Second</p></article></body></html>"
    scraped = Scraped(article=Article(url="http://example.com", title="T", section="S"), html=html)
    result = scraped.text
    assert "First" in result
    assert "Second" in result
