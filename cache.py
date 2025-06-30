import os
import sqlite3
from typing import Optional

DB_PATH = os.environ.get("EVENING_REVIEW_CACHE", "cache.db")


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS pages (url TEXT PRIMARY KEY, html TEXT)"
    )


def get_html(url: str) -> Optional[str]:
    """Return cached HTML for ``url`` or ``None`` if not cached."""
    conn = sqlite3.connect(DB_PATH)
    try:
        _ensure_table(conn)
        row = conn.execute("SELECT html FROM pages WHERE url=?", (url,)).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def store_html(url: str, html: str) -> None:
    """Store ``html`` for ``url`` in the cache."""
    conn = sqlite3.connect(DB_PATH)
    try:
        _ensure_table(conn)
        conn.execute(
            "INSERT OR REPLACE INTO pages (url, html) VALUES (?, ?)", (url, html)
        )
        conn.commit()
    finally:
        conn.close()


def set_db_path(path: str) -> None:
    """Set the database path used for caching."""
    global DB_PATH
    DB_PATH = path
