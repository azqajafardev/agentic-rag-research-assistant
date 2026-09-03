"""SQLite connection management and schema initialization."""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.core.config import Settings

logger = logging.getLogger("evidencerag")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 0,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages (conversation_id);
"""


def get_connection(db_path: Path) -> sqlite3.Connection:
    # check_same_thread=False: FastAPI may run the sync dependency that opens
    # this connection in a different worker thread than the async route
    # handler that uses it. The connection is still scoped to a single
    # request and never shared concurrently across threads.
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(settings: Settings) -> None:
    """Create the database directory/file and required tables if missing.

    Safe to call on every startup: it never drops or truncates existing data.
    """
    db_path = settings.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection(db_path) as conn:
        conn.executescript(_SCHEMA)
        conn.commit()

    logger.info("database_initialized", extra={"path": str(db_path)})


@contextmanager
def session(settings: Settings) -> Iterator[sqlite3.Connection]:
    conn = get_connection(settings.database_path)
    try:
        yield conn
    finally:
        conn.close()
