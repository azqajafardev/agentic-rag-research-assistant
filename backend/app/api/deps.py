"""Shared FastAPI dependencies."""

import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Iterator

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.db.database import get_connection, init_db
from app.services.chat_service import ChatService
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.reranker_service import RerankerService
from app.services.retrieval_service import RetrievalService
from app.services.vector_service import VectorService


def get_db_connection(settings: Settings = Depends(get_settings)) -> Iterator[sqlite3.Connection]:
    init_db(settings)  # idempotent: CREATE TABLE IF NOT EXISTS, restart-safe
    conn = get_connection(settings.database_path)
    try:
        yield conn
    finally:
        conn.close()


@lru_cache
def _cached_embedding_service(provider: str, model: str) -> EmbeddingService:
    settings = get_settings().model_copy(update={"embedding_provider": provider, "embedding_model": model})
    return EmbeddingService(settings)


def get_embedding_service(settings: Settings = Depends(get_settings)) -> EmbeddingService:
    return _cached_embedding_service(settings.embedding_provider, settings.embedding_model)


@lru_cache
def _cached_vector_service(vector_db_path: str) -> VectorService:
    return VectorService(Path(vector_db_path))


def get_vector_service(settings: Settings = Depends(get_settings)) -> VectorService:
    return _cached_vector_service(str(settings.vector_db_path))


@lru_cache
def _cached_llm_service(provider: str, model: str, api_key: str) -> LLMService:
    settings = get_settings().model_copy(
        update={"llm_provider": provider, "llm_model": model, "llm_api_key": api_key}
    )
    return LLMService(settings)


def get_llm_service(settings: Settings = Depends(get_settings)) -> LLMService:
    return _cached_llm_service(settings.llm_provider, settings.llm_model, settings.llm_api_key)


def get_reranker_service(settings: Settings = Depends(get_settings)) -> RerankerService:
    return RerankerService(settings)


def get_retrieval_service(
    settings: Settings = Depends(get_settings),
    vector_service: VectorService = Depends(get_vector_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> RetrievalService:
    return RetrievalService(vector_service, embedding_service, settings)


def get_chat_service(
    settings: Settings = Depends(get_settings),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    reranker_service: RerankerService = Depends(get_reranker_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> ChatService:
    return ChatService(retrieval_service, reranker_service, llm_service, settings)
