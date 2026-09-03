"""Orchestrates the document ingestion pipeline: validate, store, extract, chunk, persist."""

import logging
import sqlite3
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import (
    DocumentNotFoundError,
    DocumentProcessingFailedError,
    EmptyFileError,
    FileTooLargeError,
    InvalidFileTypeError,
    StorageError,
)
from app.db import repositories
from app.models.document import Document, DocumentStatus
from app.rag.chunker import chunk_pages
from app.services.embedding_service import EmbeddingService
from app.services.pdf_service import extract_pages, is_readable_pdf
from app.services.vector_service import VectorService
from app.utils.file_utils import (
    generate_document_id,
    resolve_upload_path,
    sanitize_filename,
    sha256_bytes,
    unique_stored_filename,
)

logger = logging.getLogger("evidencerag")


def _validate_upload(filename: str, file_bytes: bytes, settings: Settings) -> None:
    if not filename.lower().endswith(".pdf"):
        raise InvalidFileTypeError("Only PDF files are supported.")

    if len(file_bytes) == 0:
        raise EmptyFileError("Uploaded file is empty.")

    if len(file_bytes) > settings.max_upload_size_bytes:
        raise FileTooLargeError(
            f"File exceeds the maximum allowed size of {settings.max_upload_size_mb}MB."
        )

    if not is_readable_pdf(file_bytes):
        raise InvalidFileTypeError("Uploaded file is not a valid, readable PDF.")


def _store_file(file_bytes: bytes, original_filename: str, settings: Settings) -> Path:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = unique_stored_filename(original_filename)
    destination = resolve_upload_path(settings.upload_dir, stored_filename)

    try:
        destination.write_bytes(file_bytes)
    except OSError as exc:
        logger.error("file_storage_failed", extra={"error": str(exc)})
        raise StorageError("Failed to store the uploaded file.") from exc

    return destination


def process_upload(
    conn: sqlite3.Connection,
    *,
    filename: str,
    file_bytes: bytes,
    settings: Settings,
    embedding_service: EmbeddingService,
    vector_service: VectorService,
) -> Document:
    """Run the full ingestion pipeline for a single uploaded PDF."""
    safe_filename = sanitize_filename(filename)
    _validate_upload(safe_filename, file_bytes, settings)

    file_hash = sha256_bytes(file_bytes)
    file_path = _store_file(file_bytes, safe_filename, settings)
    document_id = generate_document_id()

    repositories.create_document(
        conn,
        document_id=document_id,
        filename=safe_filename,
        file_path=str(file_path),
        file_hash=file_hash,
        status=DocumentStatus.UPLOADED,
    )
    logger.info(
        "document_uploaded", extra={"document_id": document_id, "doc_filename": safe_filename}
    )

    repositories.update_document_status(conn, document_id, DocumentStatus.PROCESSING)
    logger.info("document_processing_started", extra={"document_id": document_id})

    try:
        pages = extract_pages(file_bytes)
        logger.info(
            "pdf_extraction_completed",
            extra={"document_id": document_id, "page_count": len(pages)},
        )

        chunks = chunk_pages(pages, document_id=document_id, filename=safe_filename)
        logger.info(
            "chunks_created",
            extra={"document_id": document_id, "chunk_count": len(chunks)},
        )

        embeddings = embedding_service.embed_documents([chunk.text for chunk in chunks])
        vector_service.upsert_chunks(chunks, embeddings)
        logger.info(
            "chunks_embedded_and_indexed",
            extra={"document_id": document_id, "chunk_count": len(chunks)},
        )

        repositories.update_document_counts(
            conn, document_id, page_count=len(pages), chunk_count=len(chunks)
        )
        repositories.update_document_status(conn, document_id, DocumentStatus.INDEXED)
        logger.info("document_indexed", extra={"document_id": document_id})
    except Exception as exc:
        vector_service.delete_document(document_id)  # avoid orphaned partial vectors
        repositories.update_document_status(conn, document_id, DocumentStatus.FAILED)
        logger.error(
            "document_processing_failed",
            extra={"document_id": document_id, "error": str(exc)},
        )
        if isinstance(exc, DocumentProcessingFailedError):
            raise
        raise DocumentProcessingFailedError("Unable to process the uploaded PDF.") from exc

    return repositories.get_document(conn, document_id)  # type: ignore[return-value]


def list_documents(conn: sqlite3.Connection) -> list[Document]:
    return repositories.get_documents(conn)


def get_document(conn: sqlite3.Connection, document_id: str) -> Document:
    document = repositories.get_document(conn, document_id)
    if document is None:
        raise DocumentNotFoundError(f"Document '{document_id}' was not found.")
    return document


def delete_document(
    conn: sqlite3.Connection, document_id: str, vector_service: VectorService
) -> None:
    document = get_document(conn, document_id)

    file_path = Path(document.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError as exc:
            logger.warning(
                "document_file_delete_failed",
                extra={"document_id": document_id, "error": str(exc)},
            )

    vector_service.delete_document(document_id)
    repositories.delete_document(conn, document_id)
    logger.info("document_deleted", extra={"document_id": document_id})
