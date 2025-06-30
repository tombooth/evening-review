"""Utilities for retrieving pages from archive.ph."""

from __future__ import annotations

import urllib.parse

import requests
from bs4 import BeautifulSoup
from cache import get_html as cache_get_html, store_html as cache_store_html


def fetch_archive_html(url: str) -> str:
    """Return the archived HTML for *url* from archive.ph.

    The function fetches ``http://archive.is/newest/[url]`` using ``requests``
    and returns the HTML from within ``div#CONTENT`` of the resulting page.
    ``url`` is URL encoded before it is appended to the archive endpoint.
    """

    cached = cache_get_html(url)
    if cached is not None:
        return cached

    encoded = urllib.parse.quote(url, safe="")
    archive_url = f"http://archive.is/newest/{encoded}"
    response = requests.get(archive_url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    container = soup.find("div", id="CONTENT")
    if container is None:
        raise ValueError("CONTENT not found in archive page")

    html = container.decode_contents()
    cache_store_html(url, html)
    return html
