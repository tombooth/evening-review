"""Scraper for theguardian.com front page."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup
import urllib3


@dataclass
class Article:
    """Represents a link to a Guardian article."""

    url: str
    title: str
    section: str


def get_guardian_articles(url: str = "https://www.theguardian.com/uk") -> List[Article]:
    """Return a list of articles from the Guardian UK front page.

    Each article includes its URL, headline and the section name in which it
    appeared.  The function fetches ``url`` using ``requests`` and parses the
    returned HTML with ``BeautifulSoup``.
    """

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(url, timeout=10, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    articles: list[Article] = []
    seen: set[str] = set()

    for section in soup.find_all("section"):
        # Attempt to determine the section title.
        section_title = None
        header = section.find("h2")
        if header:
            section_title = header.get_text(strip=True)
        if not section_title:
            section_title = section.get("id")
        if not section_title:
            continue

        for anchor in section.find_all("a", href=True):
            href = anchor["href"].strip()
            if not href or href.startswith("#"):
                continue

            # Normalise relative URLs.
            if href.startswith("/"):
                href = "https://www.theguardian.com" + href

            # Avoid duplicates.
            if href in seen:
                continue

            title = anchor.get("aria-label") or anchor.get_text(strip=True)
            if not title:
                continue

            articles.append(Article(url=href, title=title, section=section_title))
            seen.add(href)

    return articles


if __name__ == "__main__":
    for article in get_guardian_articles():
        print(f"[{article.section}] {article.title} -> {article.url}")

