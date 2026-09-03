"""Repository functions encapsulating all SQL for documents, conversations and messages."""

import sqlite3
import uuid
from datetime import datetime, timezone

from app.models.conversation import Conversation, Message
from app.models.document import Document


def _row_to_document(row: sqlite3.Row) -> Document:
    return Document(
        id=row["id"],
        filename=row["filename"],
        file_path=row["file_path"],
        file_hash=row["file_hash"],
        page_count=row["page_count"],
        chunk_count=row["chunk_count"],
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def create_document(
    conn: sqlite3.Connection,
    *,
    document_id: str,
    filename: str,
    file_path: str,
    file_hash: str,
    status: str,
) -> Document:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO documents
            (id, filename, file_path, file_hash, page_count, chunk_count, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, 0, 0, ?, ?, ?)
        """,
        (document_id, filename, file_path, file_hash, status, now, now),
    )
    conn.commit()
    return get_document(conn, document_id)  # type: ignore[return-value]


def get_document(conn: sqlite3.Connection, document_id: str) -> Document | None:
    row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    return _row_to_document(row) if row else None


def get_documents(conn: sqlite3.Connection) -> list[Document]:
    rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    return [_row_to_document(row) for row in rows]


def update_document_status(conn: sqlite3.Connection, document_id: str, status: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE documents SET status = ?, updated_at = ? WHERE id = ?",
        (status, now, document_id),
    )
    conn.commit()


def update_document_counts(
    conn: sqlite3.Connection, document_id: str, *, page_count: int, chunk_count: int
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE documents SET page_count = ?, chunk_count = ?, updated_at = ? WHERE id = ?",
        (page_count, chunk_count, now, document_id),
    )
    conn.commit()


def delete_document(conn: sqlite3.Connection, document_id: str) -> bool:
    cursor = conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    return cursor.rowcount > 0


def get_indexed_document_ids(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT id FROM documents WHERE status = 'indexed'").fetchall()
    return [row["id"] for row in rows]


# --- Conversations & messages -------------------------------------------------


def _row_to_conversation(row: sqlite3.Row) -> Conversation:
    return Conversation(
        id=row["id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _row_to_message(row: sqlite3.Row) -> Message:
    return Message(
        id=row["id"],
        conversation_id=row["conversation_id"],
        role=row["role"],
        content=row["content"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def get_conversation(conn: sqlite3.Connection, conversation_id: str) -> Conversation | None:
    row = conn.execute(
        "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
    ).fetchone()
    return _row_to_conversation(row) if row else None


def ensure_conversation(conn: sqlite3.Connection, conversation_id: str) -> Conversation:
    """Fetch a conversation by id, creating it if it does not exist yet."""
    existing = get_conversation(conn, conversation_id)
    if existing is not None:
        return existing

    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO conversations (id, created_at, updated_at) VALUES (?, ?, ?)",
        (conversation_id, now, now),
    )
    conn.commit()
    return get_conversation(conn, conversation_id)  # type: ignore[return-value]


def touch_conversation(conn: sqlite3.Connection, conversation_id: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id)
    )
    conn.commit()


def add_message(
    conn: sqlite3.Connection, *, conversation_id: str, role: str, content: str
) -> Message:
    message_id = f"msg_{uuid.uuid4().hex[:20]}"
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO messages (id, conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (message_id, conversation_id, role, content, now),
    )
    conn.commit()
    touch_conversation(conn, conversation_id)
    row = conn.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
    return _row_to_message(row)


def get_recent_messages(
    conn: sqlite3.Connection, conversation_id: str, limit: int
) -> list[Message]:
    """Return the most recent `limit` messages for a conversation, oldest first."""
    rows = conn.execute(
        """
        SELECT * FROM (
            SELECT * FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
        )
        ORDER BY created_at ASC, id ASC
        """,
        (conversation_id, limit),
    ).fetchall()
    return [_row_to_message(row) for row in rows]
