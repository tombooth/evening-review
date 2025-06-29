"""Scraper for ft.com front page."""

from __future__ import annotations

from typing import List

import requests
from bs4 import BeautifulSoup

from guardian import Article


def _find_section(element: BeautifulSoup) -> str:
    """Return the section title for ``element`` by searching ancestors."""
    current = element
    while current:
        # 1) look for explicit attribute
        if current.has_attr("data-trackable-context-storygroup-title"):
            return current["data-trackable-context-storygroup-title"].strip()
        if current.has_attr("data-trackable") and current["data-trackable"].startswith(
            "storyGroupTitle:"
        ):
            value = current["data-trackable"].split(":", 1)[1]
            return value.strip()
        # 2) look for visible story group title
        title_div = current.find("div", class_="story-group__title")
        if title_div:
            return title_div.get_text(strip=True)
        current = current.parent  # type: ignore[assignment]
    return ""


def get_ft_articles(url: str = "https://www.ft.com") -> List[Article]:
    """Return a list of articles from the FT front page."""

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    articles: list[Article] = []
    seen: set[str] = set()

    for headline in soup.select("div.headline"):
        anchor = headline.find("a", href=True)
        if not anchor:
            continue
        href = anchor["href"].strip()
        if not href or href.startswith("#"):
            continue
        if href.startswith("/"):
            href = "https://www.ft.com" + href
        if href in seen:
            continue
        title = anchor.get_text(strip=True)
        if not title:
            continue
        section = _find_section(headline)
        articles.append(Article(url=href, title=title, section=section))
        seen.add(href)

    return articles


if __name__ == "__main__":
    for article in get_ft_articles():
        print(f"[{article.section}] {article.title} -> {article.url}")
