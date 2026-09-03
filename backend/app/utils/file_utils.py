"""Filesystem-safe file handling helpers: sanitization, hashing, unique paths."""

import hashlib
import re
import uuid
from pathlib import Path

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    """Strip any path components and unsafe characters from a user-supplied filename."""
    name = Path(filename).name  # drop any directory components (path traversal)
    name = _UNSAFE_CHARS.sub("_", name).strip("._")
    return name or "file.pdf"


def unique_stored_filename(original_filename: str) -> str:
    """Build a unique, filesystem-safe filename for storing an upload."""
    safe_name = sanitize_filename(original_filename)
    suffix = Path(safe_name).suffix or ".pdf"
    return f"{uuid.uuid4().hex}{suffix}"


def resolve_upload_path(upload_dir: Path, stored_filename: str) -> Path:
    """Resolve a stored filename to a path guaranteed to live inside upload_dir."""
    upload_dir = upload_dir.resolve()
    candidate = (upload_dir / stored_filename).resolve()
    if upload_dir not in candidate.parents and candidate != upload_dir:
        raise ValueError("Resolved path escapes the upload directory")
    return candidate


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def generate_document_id() -> str:
    return f"doc_{uuid.uuid4().hex[:20]}"
