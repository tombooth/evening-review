from __future__ import annotations

import datetime
import uuid
from collections import OrderedDict
from html import escape
from io import BytesIO
from typing import Iterable
from urllib.parse import urlparse

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from ebooklib import epub

from models import Scraped


def _generate_cover_bytes(text: str, size: tuple[int, int] = (600, 800)) -> bytes:
    """Return PNG bytes for a simple cover image with ``text`` centered."""
    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)

    font_path = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"
    try:
        font = ImageFont.truetype(str(font_path), 40)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    pos = ((size[0] - w) / 2, (size[1] - h) / 2)
    draw.multiline_text(pos, text, fill="black", font=font, align="center")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_epub(articles: Iterable[Scraped], output_path: str) -> None:
    """Create an EPUB file at ``output_path`` with the supplied articles."""
    groups: "OrderedDict[str, OrderedDict[str, list[Scraped]]]" = OrderedDict()
    for scraped in articles:
        domain = urlparse(scraped.article.url).netloc
        site = groups.setdefault(domain, OrderedDict())
        site.setdefault(scraped.article.section, []).append(scraped)

    book = epub.EpubBook()
    book.set_identifier(str(uuid.uuid4()))
    date_str = datetime.date.today().isoformat()
    book.set_title(f"Evening Review - {date_str}")
    book.set_language("en")

    cover_text = f"Evening Review\n{date_str}"
    cover_bytes = _generate_cover_bytes(cover_text)
    book.set_cover("cover.png", cover_bytes)

    nav_items: list[epub.Link] = []
    spine: list = ["nav"]

    index_lines = [f"<h1>Evening Review - {date_str}</h1>"]

    # maintain article order by iterating through groups in insertion order
    counter = 0
    for domain, sections in groups.items():
        index_lines.append(f"<h2>{escape(domain)}</h2>")
        for section, items in sections.items():
            index_lines.append(f"<h3>{escape(section)}</h3>")
            index_lines.append("<ul>")
            for scraped in items:
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
