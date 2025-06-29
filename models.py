from __future__ import annotations

from dataclasses import dataclass

from guardian import Article
import trafilatura


@dataclass
class Scraped:
    """Represents scraped HTML for an article."""

    article: Article
    html: str

    @property
    def text(self) -> str:
        """Return ``self.html`` converted to plain text using Trafilatura."""
        extracted = trafilatura.extract(self.html, output_format="html", include_formatting=True, include_links=True, include_images=True)
        return extracted or ""
