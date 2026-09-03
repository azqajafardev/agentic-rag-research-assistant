"""Reranker abstraction.

Disabled by default (RERANKER_ENABLED=false): retrieval results are returned
unchanged, already sorted by vector similarity score. This keeps the RAG
pipeline usable without an extra heavyweight reranking model. The hook is
kept as an explicit pipeline stage so a real cross-encoder reranker can be
dropped in later without changing chat_service.
"""

import logging

from app.core.config import Settings
from app.services.retrieval_service import EvidenceChunk

logger = logging.getLogger("evidencerag")


class RerankerService:
    def __init__(self, settings: Settings) -> None:
        self._enabled = settings.reranker_enabled

    def rerank(self, question: str, evidence: list[EvidenceChunk]) -> list[EvidenceChunk]:
        if not self._enabled:
            return evidence

        # No reranking model is bundled in Phase 2; fall back to score order.
        logger.warning("reranker_enabled_but_not_implemented")
        return sorted(evidence, key=lambda chunk: chunk.score, reverse=True)
