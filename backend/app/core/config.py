"""Centralized application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_ANTHROPIC_MODEL = "claude-opus-5"
_DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"


class Settings(BaseSettings):
    app_name: str = "EvidenceRAG API"
    app_env: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./data/evidencerag.db"

    upload_dir: Path = Path("./data/uploads")
    max_upload_size_mb: int = 20

    frontend_url: str = "http://localhost:5173"

    # RAG: embeddings
    embedding_provider: str = "local"  # only "local" (ONNX MiniLM, no API key) is implemented
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_api_key: str = ""

    # RAG: vector store
    vector_db_path: Path = Path("./data/chroma")

    # RAG: retrieval
    top_k: int = 5
    similarity_threshold: float = 0.35

    # RAG: reranking
    reranker_enabled: bool = False

    # RAG: LLM
    llm_provider: str = "anthropic"
    llm_model: str = _DEFAULT_ANTHROPIC_MODEL
    llm_api_key: str = ""

    # RAG: context / chat
    max_context_chars: int = 12000
    max_question_length: int = 2000
    conversation_history_limit: int = 6  # prior messages included per LLM call

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def _apply_groq_default_model(self) -> "Settings":
        # If the provider was switched to groq but LLM_MODEL was left unset
        # (still the anthropic default), use a sensible Groq default instead
        # of sending an Anthropic model name to Groq's API. An explicitly
        # set LLM_MODEL always wins.
        if self.llm_provider == "groq" and self.llm_model == _DEFAULT_ANTHROPIC_MODEL:
            self.llm_model = _DEFAULT_GROQ_MODEL
        return self

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def database_path(self) -> Path:
        # Strip the sqlite:/// prefix to get a filesystem path.
        return Path(self.database_url.removeprefix("sqlite:///"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
