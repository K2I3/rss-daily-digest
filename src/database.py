import os
import sqlite3
from contextlib import contextmanager


@contextmanager
def get_connection(db_path: str):
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str):
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                distribution_date TEXT,   -- RSS配信日(このバッチが配信された日, JST)
                feed_name TEXT,           -- 参考情報: どのフィード由来か
                title TEXT,
                link TEXT UNIQUE,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)


def is_url_processed(db_path: str, url: str) -> bool:
    """既にDBに登録済みのURLかどうかを判定(重複配信防止)"""
    with get_connection(db_path) as conn:
        cur = conn.execute("SELECT 1 FROM articles WHERE link = ?", (url,))
        return cur.fetchone() is not None


def save_entry(db_path: str, record: dict):
    with get_connection(db_path) as conn:
        conn.execute("""
            INSERT OR IGNORE INTO articles (distribution_date, feed_name, title, link)
            VALUES (:distribution_date, :feed_name, :title, :link)
        """, record)
