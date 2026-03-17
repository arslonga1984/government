import sqlite3
import logging
from contextlib import contextmanager
from config.settings import DB_PATH

logger = logging.getLogger(__name__)


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS announcements (
                content_hash TEXT PRIMARY KEY,
                title        TEXT NOT NULL,
                source_site  TEXT NOT NULL,
                url          TEXT,
                deadline     TEXT,
                org          TEXT,
                summary      TEXT,
                crawled_at   TEXT NOT NULL,
                notified     INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS match_results (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                announcement_hash TEXT NOT NULL,
                product_name      TEXT NOT NULL,
                match_score       REAL NOT NULL,
                matched_keywords  TEXT,
                created_at        TEXT NOT NULL,
                FOREIGN KEY (announcement_hash) REFERENCES announcements(content_hash)
            );

            CREATE TABLE IF NOT EXISTS crawl_log (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id       TEXT NOT NULL,
                status        TEXT NOT NULL,
                items_found   INTEGER DEFAULT 0,
                new_items     INTEGER DEFAULT 0,
                error_message TEXT,
                started_at    TEXT NOT NULL,
                finished_at   TEXT
            );
        """)
    logger.info("DB 초기화 완료: %s", DB_PATH)


def upsert_announcement(item: dict) -> bool:
    """새 공고 저장. 이미 존재하면 False 반환."""
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT OR IGNORE INTO announcements
               (content_hash, title, source_site, url, deadline, org, summary, crawled_at)
               VALUES (:content_hash, :title, :source_site, :url, :deadline, :org, :summary, :crawled_at)""",
            item,
        )
        return cur.rowcount > 0


def save_match_results(results: list[dict]):
    with get_conn() as conn:
        conn.executemany(
            """INSERT INTO match_results
               (announcement_hash, product_name, match_score, matched_keywords, created_at)
               VALUES (:announcement_hash, :product_name, :match_score, :matched_keywords, :created_at)""",
            results,
        )


def get_unnotified_matches(min_score: float = 40.0) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT a.title, a.url, a.deadline, a.org, a.source_site,
                      m.announcement_hash, m.product_name, m.match_score, m.matched_keywords
               FROM match_results m
               JOIN announcements a ON a.content_hash = m.announcement_hash
               WHERE a.notified = 0
                 AND m.match_score >= ?
               ORDER BY m.match_score DESC""",
            (min_score,),
        ).fetchall()
        return [dict(r) for r in rows]


def mark_notified(announcement_hashes: list[str]):
    with get_conn() as conn:
        conn.executemany(
            "UPDATE announcements SET notified = 1 WHERE content_hash = ?",
            [(h,) for h in announcement_hashes],
        )


def get_unmatched_announcements() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT a.content_hash, a.title, a.summary
               FROM announcements a
               LEFT JOIN match_results m ON m.announcement_hash = a.content_hash
               WHERE m.id IS NULL"""
        ).fetchall()
        return [dict(r) for r in rows]


def log_crawl_start(site_id: str, started_at: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO crawl_log (site_id, status, started_at) VALUES (?, 'running', ?)",
            (site_id, started_at),
        )
        return cur.lastrowid


def log_crawl_finish(log_id: int, status: str, items_found: int, new_items: int,
                     finished_at: str, error_message: str = None):
    with get_conn() as conn:
        conn.execute(
            """UPDATE crawl_log
               SET status=?, items_found=?, new_items=?, finished_at=?, error_message=?
               WHERE id=?""",
            (status, items_found, new_items, finished_at, error_message, log_id),
        )
