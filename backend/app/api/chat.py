"""RAG chat endpoint."""

import sqlite3

from fastapi import APIRouter, Depends

from app.api.deps import get_chat_service, get_db_connection
from app.schemas.chat import ChatRequest, ChatResponse, SourceResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse, summary="Ask a grounded question")
def chat(
    request: ChatRequest,
    conn: sqlite3.Connection = Depends(get_db_connection),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    result = chat_service.answer(
        conn,
        question=request.question,
        document_ids=request.document_ids,
        conversation_id=request.conversation_id,
    )

    return ChatResponse(
        conversation_id=result.conversation_id,
        answer=result.answer,
        grounded=result.grounded,
        sources=[
            SourceResponse(
                id=source.id,
                document_id=source.document_id,
                filename=source.filename,
                page=source.page,
                score=source.score,
                evidence=source.evidence,
            )
            for source in result.sources
        ],
    )
