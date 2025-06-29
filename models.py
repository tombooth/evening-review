from __future__ import annotations

from dataclasses import dataclass

from guardian import Article
import trafilatura


@dataclass
class Scraped:
    """Represents scraped HTML for an article."""

    article: Article
    html: str

    def text(self) -> str:
        """Return ``self.html`` converted to plain text using Trafilatura."""
        extracted = trafilatura.extract(self.html)
        return extracted or ""
