"""Database layer for gitbutt.

Extends data/repos.sqlite3, which the extraction prototype created with
videos, repos, and video_repos tables. This module adds the idea-space
tables.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPO_DB = PROJECT_ROOT / "data" / "repos.sqlite3"

IDEA_SCHEMA = """
CREATE TABLE IF NOT EXISTS video_transcripts (
    video_id TEXT NOT NULL REFERENCES videos(video_id),
    start_ms INTEGER NOT NULL,
    end_ms INTEGER NOT NULL,
    text TEXT NOT NULL,
    PRIMARY KEY (video_id, start_ms)
);

CREATE TABLE IF NOT EXISTS repo_summaries (
    full_name TEXT PRIMARY KEY REFERENCES repos(full_name),
    summary TEXT NOT NULL,
    tags TEXT,
    source TEXT DEFAULT 'ai',
    generated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ideas (
    idea_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pitch TEXT NOT NULL,
    target_customer TEXT,
    marketing_angle TEXT,
    source_run TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS idea_repos (
    idea_id INTEGER NOT NULL REFERENCES ideas(idea_id),
    full_name TEXT NOT NULL REFERENCES repos(full_name),
    PRIMARY KEY (idea_id, full_name)
);

CREATE TABLE IF NOT EXISTS idea_scores (
    idea_id INTEGER PRIMARY KEY REFERENCES ideas(idea_id),
    score REAL NOT NULL,
    dimensions TEXT NOT NULL,
    signals TEXT,
    kill_switch TEXT,
    scored_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS email_drafts (
    idea_id INTEGER PRIMARY KEY REFERENCES ideas(idea_id),
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    generated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def connect(db_path: Path = REPO_DB) -> sqlite3.Connection:
    """Open a configured SQLite connection; creates the data dir if needed."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def init_idea_schema(conn: sqlite3.Connection | None = None) -> None:
    """Create the idea-space tables if missing. Safe to call on every start."""
    own_conn = conn is None
    if own_conn:
        conn = connect()
    try:
        conn.executescript(IDEA_SCHEMA)
        _migrate(conn)
        conn.commit()
    finally:
        if own_conn:
            conn.close()


def _migrate(conn: sqlite3.Connection) -> None:
    """Add columns introduced after the first schema version."""
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "videos" in tables:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(videos)")}
        if "description" not in cols:
            conn.execute("ALTER TABLE videos ADD COLUMN description TEXT")
    if "repo_summaries" in tables:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(repo_summaries)")}
        if "source" not in cols:
            conn.execute("ALTER TABLE repo_summaries ADD COLUMN source TEXT DEFAULT 'ai'")
    if "repos" in tables:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(repos)")}
        if "category" not in cols:
            conn.execute("ALTER TABLE repos ADD COLUMN category TEXT")
