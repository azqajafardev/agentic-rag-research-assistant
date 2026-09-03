"""Document upload, listing, detail and deletion endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import get_db_connection, get_embedding_service, get_vector_service
from app.core.config import Settings, get_settings
from app.schemas.document import (
    DeleteResponse,
    DocumentListResponse,
    DocumentResponse,
    UploadedDocument,
    UploadResponse,
)
from app.services import document_service
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _to_response(document) -> DocumentResponse:  # type: ignore[no-untyped-def]
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        page_count=document.page_count,
        chunk_count=document.chunk_count,
        status=document.status,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


@router.post("/upload", response_model=UploadResponse, summary="Upload one or more PDF documents")
async def upload_documents(
    files: list[UploadFile],
    conn: sqlite3.Connection = Depends(get_db_connection),
    settings: Settings = Depends(get_settings),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_service: VectorService = Depends(get_vector_service),
) -> UploadResponse:
    uploaded: list[UploadedDocument] = []

    for file in files:
        file_bytes = await file.read()
        document = document_service.process_upload(
            conn,
            filename=file.filename or "upload.pdf",
            file_bytes=file_bytes,
            settings=settings,
            embedding_service=embedding_service,
            vector_service=vector_service,
        )
        uploaded.append(
            UploadedDocument(id=document.id, filename=document.filename, status=document.status)
        )

    return UploadResponse(documents=uploaded)


@router.get("", response_model=DocumentListResponse, summary="List all documents")
def list_documents(conn: sqlite3.Connection = Depends(get_db_connection)) -> DocumentListResponse:
    documents = document_service.list_documents(conn)
    return DocumentListResponse(documents=[_to_response(doc) for doc in documents])


@router.get("/{document_id}", response_model=DocumentResponse, summary="Get document details")
def get_document(
    document_id: str, conn: sqlite3.Connection = Depends(get_db_connection)
) -> DocumentResponse:
    document = document_service.get_document(conn, document_id)
    return _to_response(document)


@router.delete("/{document_id}", response_model=DeleteResponse, summary="Delete a document")
def delete_document(
    document_id: str,
    conn: sqlite3.Connection = Depends(get_db_connection),
    vector_service: VectorService = Depends(get_vector_service),
) -> DeleteResponse:
    document_service.delete_document(conn, document_id, vector_service)
    return DeleteResponse(id=document_id, deleted=True)
