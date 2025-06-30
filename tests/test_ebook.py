import zipfile
import datetime
from pathlib import Path
from guardian import Article
from models import Scraped
from ebook import create_epub

def test_create_epub_writes_index(tmp_path: Path):
    scraped = Scraped(
        article=Article(url='http://example.com', title='Hello', section='News'),
        html='<p>content</p>'
    )
    out = tmp_path / 'book.epub'
    create_epub([scraped], str(out))
    assert out.exists()
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        assert 'EPUB/index.xhtml' in names
        assert 'EPUB/cover.png' in names
        assert any(n.endswith('.xhtml') and n != 'EPUB/index.xhtml' for n in names)
        index_html = zf.read('EPUB/index.xhtml').decode()
        today = datetime.date.today().isoformat()
        assert today in index_html
        assert 'example.com' in index_html
        assert 'Hello' in index_html
