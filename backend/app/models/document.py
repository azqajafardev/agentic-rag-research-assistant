"""Internal representation of a document record (not a Pydantic API schema)."""

from dataclasses import dataclass
from datetime import datetime


class DocumentStatus:
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


@dataclass
class Document:
    id: str
    filename: str
    file_path: str
    file_hash: str
    page_count: int
    chunk_count: int
    status: str
    created_at: datetime
    updated_at: datetime
