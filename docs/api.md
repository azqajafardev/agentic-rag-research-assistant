# API Reference

Base URL: `http://127.0.0.1:8000/api` (configurable via `FRONTEND_URL`/`VITE_API_URL`).
Interactive docs: `/docs` (Swagger) and `/redoc`.

All errors share one envelope:

```json
{ "error": { "code": "DOCUMENT_NOT_FOUND", "message": "Document 'doc_x' was not found." } }
```

---

## `GET /api/health`

Real, just-performed checks - never a hardcoded "ready" value. A dependency
that's actually down degrades its own field to `"unavailable"` without
failing the whole endpoint.

**Response `200`**
```json
{
  "status": "ok",
  "backend": "connected",
  "database": "connected",
  "vector_db": "connected"
}
```
`status` is `"ok"` only when both `database` and `vector_db` are `"connected"`; otherwise `"degraded"`.

---

## `POST /api/documents/upload`

`multipart/form-data`, field name `files` (repeatable - upload one or many PDFs in one request).

**Response `200`**
```json
{
  "documents": [
    { "id": "doc_...", "filename": "paper.pdf", "status": "indexed" }
  ]
}
```

**Errors**: `INVALID_FILE_TYPE` (400), `EMPTY_FILE` (400), `FILE_TOO_LARGE` (413),
`DOCUMENT_PROCESSING_FAILED` (422) - extraction, embedding, or vector-store
failure; the document's status is set to `failed` and any partial vectors
are cleaned up.

---

## `GET /api/documents`

**Response `200`**
```json
{
  "documents": [
    {
      "id": "doc_...", "filename": "paper.pdf",
      "page_count": 12, "chunk_count": 84, "status": "indexed",
      "created_at": "2026-09-03T06:15:42.694723Z",
      "updated_at": "2026-09-03T06:15:48.195400Z"
    }
  ]
}
```

---

## `GET /api/documents/{document_id}`

**Response `200`**: a single document object (same shape as above).

**Errors**: `DOCUMENT_NOT_FOUND` (404).

---

## `DELETE /api/documents/{document_id}`

Removes the SQLite record, the stored PDF file, and the document's ChromaDB vectors.

**Response `200`**
```json
{ "id": "doc_...", "deleted": true }
```

**Errors**: `DOCUMENT_NOT_FOUND` (404).

---

## `POST /api/chat`

**Request**
```json
{
  "question": "What dataset was used?",
  "document_ids": ["doc_123"],
  "conversation_id": null
}
```
`document_ids` (optional) scopes retrieval to specific indexed documents; omit or send `null` to search all indexed documents. `conversation_id` (optional) continues an existing conversation; omit or send `null` to start a new one.

**Response `200` - grounded**
```json
{
  "conversation_id": "conversation_...",
  "answer": "The study used the HAM10000 dataset.",
  "grounded": true,
  "sources": [
    {
      "id": "source_1", "document_id": "doc_123", "filename": "paper.pdf",
      "page": 4, "score": 0.91, "evidence": "..."
    }
  ]
}
```

**Response `200` - no evidence found** (the LLM is never called for this case)
```json
{
  "conversation_id": "conversation_...",
  "answer": "I couldn't find sufficient evidence in the uploaded documents to answer this question.",
  "grounded": false,
  "sources": []
}
```

**Errors**: `INVALID_QUESTION` (400 - empty or exceeds `MAX_QUESTION_LENGTH`),
`EMBEDDING_FAILED` (500), `VECTOR_STORE_ERROR` (500), `LLM_ERROR` (503 -
provider auth/rate-limit/timeout/connection failure).

---

## Error codes

| Code | HTTP | Meaning |
|---|---|---|
| `INVALID_FILE_TYPE` | 400 | Not a PDF, or unreadable as one |
| `EMPTY_FILE` | 400 | Zero-byte upload |
| `FILE_TOO_LARGE` | 413 | Exceeds `MAX_UPLOAD_SIZE_MB` |
| `DOCUMENT_NOT_FOUND` | 404 | Unknown `document_id` |
| `DOCUMENT_PROCESSING_FAILED` | 422 | Extraction/embedding/indexing failed |
| `STORAGE_ERROR` | 500 | Could not write the uploaded file |
| `DATABASE_ERROR` | 500 | SQLite failure |
| `EMBEDDING_FAILED` | 500 | Embedding model failure |
| `VECTOR_STORE_ERROR` | 500 | ChromaDB failure |
| `INVALID_QUESTION` | 400 | Empty or over-length question |
| `LLM_ERROR` | 503 | LLM provider unavailable, unauthenticated, or rate-limited |
