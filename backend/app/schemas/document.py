from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    page_count: int
    chunk_count: int
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]


class UploadedDocument(BaseModel):
    id: str
    filename: str
    status: str


class UploadResponse(BaseModel):
    documents: list[UploadedDocument]


class DeleteResponse(BaseModel):
    id: str
    deleted: bool
