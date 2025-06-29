from __future__ import annotations

import datetime
import uuid
import zipfile
from collections import defaultdict
from html import escape
from typing import Iterable

from models import Scraped


def create_epub(articles: Iterable[Scraped], output_path: str) -> None:
    """Create an EPUB file at ``output_path`` with the supplied articles."""
    grouped: dict[str, list[Scraped]] = defaultdict(list)
    for article in articles:
        grouped[article.article.section].append(article)

    index_lines = [
        '<html xmlns="http://www.w3.org/1999/xhtml">',
        '<head><title>Evening Review</title></head>',
        '<body>',
        '<h1>Evening Review</h1>',
    ]

    article_files: list[tuple[str, str, str]] = []  # (id, filename, html)
    counter = 0
    for section in sorted(grouped):
        index_lines.append(f'<h2>{escape(section)}</h2>')
        index_lines.append('<ul>')
        for scraped in grouped[section]:
            aid = f"a{counter}"
            fname = f"{aid}.xhtml"
            article_html = (
                f'<html xmlns="http://www.w3.org/1999/xhtml">\n'
                f'<head><title>{escape(scraped.article.title)}</title></head>\n'
                f'<body>\n'
                f'<h1>{escape(scraped.article.title)}</h1>\n'
                f'<p><a href="index.xhtml">Back to index</a></p>\n'
                f'{scraped.text}\n'
                f'<p><a href="index.xhtml">Back to index</a></p>\n'
                f'</body>\n'
                f'</html>'
            )
            article_files.append((aid, fname, article_html))
            index_lines.append(f'<li><a href="{fname}">{escape(scraped.article.title)}</a></li>')
            counter += 1
        index_lines.append('</ul>')

    index_lines.append('</body></html>')
    index_html = "\n".join(index_lines)

    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    book_id = uuid.uuid4()

    manifest = [
        '<item id="index" href="index.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
    ]
    spine = ['<itemref idref="index"/>']
    for aid, fname, _ in article_files:
        manifest.append(f'<item id="{aid}" href="{fname}" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{aid}"/>')

    content_opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="BookId">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">urn:uuid:{book_id}</dc:identifier>
    <dc:title>Evening Review</dc:title>
    <meta property="dcterms:modified">{now}</meta>
  </metadata>
  <manifest>
    {'\n    '.join(manifest)}
  </manifest>
  <spine>
    {'\n    '.join(spine)}
  </spine>
</package>
'''

    container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
'''

    with zipfile.ZipFile(output_path, 'w') as zf:
        zf.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        zf.writestr('META-INF/container.xml', container_xml)
        zf.writestr('index.xhtml', index_html)
        for _, fname, html in article_files:
            zf.writestr(fname, html)
        zf.writestr('content.opf', content_opf)
