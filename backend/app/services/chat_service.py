"""Orchestrates the full RAG chat flow: retrieve, threshold, rerank, ground, cite."""

import logging
import sqlite3
import uuid
from dataclasses import dataclass

from app.core.config import Settings
from app.core.exceptions import InvalidQuestionError
from app.db import repositories
from app.models.conversation import MessageRole
from app.rag import context_builder
from app.rag.citation import Source, build_sources
from app.services.llm_service import LLMService
from app.services.reranker_service import RerankerService
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger("evidencerag")

NO_EVIDENCE_ANSWER = (
    "I couldn't find sufficient evidence in the uploaded documents to answer this question."
)


@dataclass
class ChatResult:
    conversation_id: str
    answer: str
    grounded: bool
    sources: list[Source]


class ChatService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        reranker_service: RerankerService,
        llm_service: LLMService,
        settings: Settings,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._reranker_service = reranker_service
        self._llm_service = llm_service
        self._settings = settings

    def answer(
        self,
        conn: sqlite3.Connection,
        *,
        question: str,
        document_ids: list[str] | None,
        conversation_id: str | None,
    ) -> ChatResult:
        question = question.strip()
        if not question:
            raise InvalidQuestionError("Question must not be empty.")
        if len(question) > self._settings.max_question_length:
            raise InvalidQuestionError(
                f"Question exceeds the maximum length of "
                f"{self._settings.max_question_length} characters."
            )

        conversation_id = conversation_id or f"conversation_{uuid.uuid4().hex[:20]}"
        repositories.ensure_conversation(conn, conversation_id)
        history = repositories.get_recent_messages(
            conn, conversation_id, self._settings.conversation_history_limit
        )
        repositories.add_message(
            conn, conversation_id=conversation_id, role=MessageRole.USER, content=question
        )

        evidence = self._retrieval_service.retrieve(conn, question, document_ids=document_ids)
        evidence = self._reranker_service.rerank(question, evidence)

        if not evidence:
            logger.info("no_evidence_found", extra={"conversation_id": conversation_id})
            repositories.add_message(
                conn,
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=NO_EVIDENCE_ANSWER,
            )
            return ChatResult(
                conversation_id=conversation_id,
                answer=NO_EVIDENCE_ANSWER,
                grounded=False,
                sources=[],
            )

        sources = build_sources(evidence)
        context = context_builder.build_context(
            sources, max_chars=self._settings.max_context_chars
        )

        answer = self._llm_service.generate(question, context, history)

        repositories.add_message(
            conn, conversation_id=conversation_id, role=MessageRole.ASSISTANT, content=answer
        )
        logger.info(
            "chat_answer_generated",
            extra={"conversation_id": conversation_id, "source_count": len(sources)},
        )

        return ChatResult(
            conversation_id=conversation_id, answer=answer, grounded=True, sources=sources
        )
