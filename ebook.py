from __future__ import annotations

import datetime
import uuid
from collections import defaultdict
from html import escape
from typing import Iterable

from ebooklib import epub

from models import Scraped


def create_epub(articles: Iterable[Scraped], output_path: str) -> None:
    """Create an EPUB file at ``output_path`` with the supplied articles."""
    grouped: dict[str, list[Scraped]] = defaultdict(list)
    for article in articles:
        grouped[article.article.section].append(article)

    book = epub.EpubBook()
    book.set_identifier(str(uuid.uuid4()))
    book.set_title("Evening Review")
    book.set_language("en")

    nav_items: list[epub.Link] = []
    spine: list = ["nav"]

    index_lines = ["<h1>Evening Review</h1>"]

    counter = 0
    for section in sorted(grouped):
        index_lines.append(f"<h2>{escape(section)}</h2>")
        index_lines.append("<ul>")
        for scraped in grouped[section]:
            aid = f"a{counter}"
            fname = f"{aid}.xhtml"

            chapter = epub.EpubHtml(title=scraped.article.title, file_name=fname, lang="en")
            chapter.content = (
                f"<h1>{escape(scraped.article.title)}</h1>"
                f'<p><a href="index.xhtml">Back to index</a></p>'
                f"{scraped.text}"
                f'<p><a href="index.xhtml">Back to index</a></p>'
            )
            book.add_item(chapter)
            nav_items.append(epub.Link(fname, scraped.article.title, aid))
            spine.append(chapter)
            index_lines.append(f'<li><a href="{fname}">{escape(scraped.article.title)}</a></li>')
            counter += 1
        index_lines.append("</ul>")

    index_content = "\n".join(index_lines)
    index = epub.EpubHtml(title="Index", file_name="index.xhtml", lang="en")
    index.content = index_content
    book.add_item(index)

    book.toc = nav_items
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())

    spine.insert(1, index)
    book.spine = spine

    epub.write_epub(output_path, book)
