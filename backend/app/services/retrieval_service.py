"""Semantic retrieval: question -> query embedding -> ChromaDB -> filtered evidence."""

import logging
import sqlite3
from dataclasses import dataclass

from app.core.config import Settings
from app.db import repositories
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

logger = logging.getLogger("evidencerag")


@dataclass
class EvidenceChunk:
    chunk_id: str
    document_id: str
    filename: str
    page: int
    text: str
    score: float


class RetrievalService:
    def __init__(
        self,
        vector_service: VectorService,
        embedding_service: EmbeddingService,
        settings: Settings,
    ) -> None:
        self._vector_service = vector_service
        self._embedding_service = embedding_service
        self._settings = settings

    def retrieve(
        self,
        conn: sqlite3.Connection,
        question: str,
        *,
        document_ids: list[str] | None = None,
    ) -> list[EvidenceChunk]:
        indexed_ids = set(repositories.get_indexed_document_ids(conn))

        if document_ids:
            allowed_ids = [doc_id for doc_id in document_ids if doc_id in indexed_ids]
        else:
            allowed_ids = list(indexed_ids)

        if not allowed_ids:
            return []

        query_embedding = self._embedding_service.embed_query(question)
        matches = self._vector_service.query(
            query_embedding,
            top_k=self._settings.top_k,
            document_ids=allowed_ids,
        )

        evidence = [
            EvidenceChunk(
                chunk_id=match.chunk_id,
                document_id=match.document_id,
                filename=match.filename,
                page=match.page,
                text=match.text,
                score=match.score,
            )
            for match in matches
            if match.score >= self._settings.similarity_threshold
        ]

        logger.info(
            "retrieval_completed",
            extra={"candidates": len(matches), "above_threshold": len(evidence)},
        )
        return evidence
