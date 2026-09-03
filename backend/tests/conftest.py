"""Shared pytest fixtures: an isolated FastAPI TestClient backed by temp storage."""

import io
from pathlib import Path

import fitz
import pytest
from fastapi.testclient import TestClient

from app.api.deps import (
    get_db_connection,
    get_embedding_service,
    get_llm_service,
)
from app.core.config import Settings, get_settings
from app.db.database import get_connection, init_db
from app.main import app
from tests.fakes import FakeEmbeddingService, FakeLLMService


@pytest.fixture()
def settings(tmp_path: Path) -> Settings:
    return Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        upload_dir=tmp_path / "uploads",
        max_upload_size_mb=1,
        frontend_url="http://localhost:5173",
        vector_db_path=tmp_path / "chroma",
        top_k=5,
        similarity_threshold=0.35,
    )


@pytest.fixture()
def fake_embedding_service() -> FakeEmbeddingService:
    return FakeEmbeddingService()


@pytest.fixture()
def fake_llm_service() -> FakeLLMService:
    return FakeLLMService()


@pytest.fixture()
def client(
    settings: Settings,
    fake_embedding_service: FakeEmbeddingService,
    fake_llm_service: FakeLLMService,
) -> TestClient:
    init_db(settings)

    def override_get_settings() -> Settings:
        return settings

    def override_get_db_connection():
        conn = get_connection(settings.database_path)
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_settings] = override_get_settings
    app.dependency_overrides[get_db_connection] = override_get_db_connection
    app.dependency_overrides[get_embedding_service] = lambda: fake_embedding_service
    app.dependency_overrides[get_llm_service] = lambda: fake_llm_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def make_pdf_bytes(pages_text: list[str]) -> bytes:
    """Build a real, minimal PDF in memory with one page per given text string."""
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    buffer = io.BytesIO()
    doc.save(buffer)
    doc.close()
    return buffer.getvalue()
