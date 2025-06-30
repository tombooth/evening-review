from __future__ import annotations

import time
from typing import Iterable, List

from cache import get_html as cache_get_html, store_html as cache_store_html

from tqdm import tqdm


import requests

from guardian import get_guardian_articles, Article
from ft import get_ft_articles
from archiver import fetch_archive_html
from ebook import create_epub
from models import Scraped


USER_AGENT = "evening-review/0.1 (+https://example.com/)"
HEADERS = {"User-Agent": USER_AGENT}
REQUEST_DELAY = 1.0  # seconds


def fetch_html(url: str) -> str:
    """Fetch ``url`` returning the raw HTML text."""
    cached = cache_get_html(url)
    if cached is not None:
        return cached
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    html = response.text
    cache_store_html(url, html)
    return html


def fetch_articles_html(articles: Iterable[Article], use_archive: bool = False) -> List[Scraped]:
    """Return a list of :class:`Scraped` objects containing article HTML.

    ``articles`` is an iterable of :class:`Article` objects. If ``use_archive`` is
    ``True`` then the HTML is retrieved via :func:`fetch_archive_html` rather
    than directly from the site.  The function pauses ``REQUEST_DELAY`` seconds
    between requests so that we behave politely towards the target servers.
    """

    article_list = list(articles)
    result: list[Scraped] = []
    for article in tqdm(article_list, desc="fetching", unit="article"):
        if use_archive:
            html = fetch_archive_html(article.url)
        else:
            html = fetch_html(article.url)
        result.append(Scraped(article=article, html=html))
        time.sleep(REQUEST_DELAY)
    return result


def main() -> None:
    guardian_articles = get_guardian_articles()
    ft_articles = get_ft_articles()

    guardian_html = fetch_articles_html(guardian_articles)
    ft_html = fetch_articles_html(ft_articles, use_archive=True)

    print(f"Fetched {len(guardian_html)} Guardian articles")
    print(f"Fetched {len(ft_html)} FT articles via archive")

    create_epub(guardian_html + ft_html, "evening_review.epub")
    print("Wrote evening_review.epub")


if __name__ == "__main__":
    main()
