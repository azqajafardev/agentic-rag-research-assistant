"""Persistent ChromaDB-backed vector store for document chunks."""

import logging
from dataclasses import dataclass
from pathlib import Path

from app.core.exceptions import VectorStoreError
from app.rag.chunker import Chunk

logger = logging.getLogger("evidencerag")

_COLLECTION_NAME = "chunks"


@dataclass
class VectorMatch:
    chunk_id: str
    document_id: str
    filename: str
    page: int
    text: str
    score: float


class VectorService:
    """Thin wrapper around a persistent ChromaDB collection.

    Embeddings are computed by EmbeddingService and passed in explicitly -
    this collection never computes its own embeddings, which keeps retrieval
    scoring and provider choice under our control.
    """

    def __init__(self, vector_db_path: Path) -> None:
        import chromadb

        vector_db_path.mkdir(parents=True, exist_ok=True)
        try:
            self._client = chromadb.PersistentClient(path=str(vector_db_path))
            self._collection = self._client.get_or_create_collection(
                name=_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            logger.exception("vector_store_init_failed", extra={"path": str(vector_db_path)})
            raise VectorStoreError("Failed to initialize the vector store.") from exc

    def upsert_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")

        try:
            self._collection.upsert(
                ids=[chunk.chunk_id for chunk in chunks],
                embeddings=embeddings,
                documents=[chunk.text for chunk in chunks],
                metadatas=[
                    {
                        "document_id": chunk.document_id,
                        "filename": chunk.filename,
                        "page": chunk.page,
                    }
                    for chunk in chunks
                ],
            )
        except Exception as exc:
            logger.exception(
                "vector_upsert_failed", extra={"document_id": chunks[0].document_id}
            )
            raise VectorStoreError("Failed to index document chunks.") from exc

    def query(
        self,
        query_embedding: list[float],
        *,
        top_k: int,
        document_ids: list[str] | None = None,
    ) -> list[VectorMatch]:
        if document_ids is not None and not document_ids:
            return []

        where = {"document_id": {"$in": document_ids}} if document_ids else None

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
            )
        except Exception as exc:
            logger.exception("vector_query_failed")
            raise VectorStoreError("Failed to query the vector store.") from exc

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        matches: list[VectorMatch] = []
        for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
            # Collection uses cosine space: distance = 1 - cosine_similarity.
            score = max(0.0, 1.0 - distance)
            matches.append(
                VectorMatch(
                    chunk_id=chunk_id,
                    document_id=metadata["document_id"],
                    filename=metadata["filename"],
                    page=metadata["page"],
                    text=text,
                    score=score,
                )
            )
        return matches

    def delete_document(self, document_id: str) -> None:
        try:
            self._collection.delete(where={"document_id": document_id})
        except Exception as exc:
            logger.warning(
                "vector_delete_failed", extra={"document_id": document_id, "error": str(exc)}
            )

    def count(self) -> int:
        return self._collection.count()
