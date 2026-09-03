"""Embedding provider abstraction.

Only a "local" provider is implemented: ChromaDB's bundled ONNX MiniLM model
(all-MiniLM-L6-v2). It requires no API key and runs entirely offline after
the model is first downloaded, which keeps the RAG pipeline usable without
paid credentials. The abstraction leaves room to add a remote provider
(e.g. OpenAI) later without touching callers.
"""

import logging
import os

import httpx

from app.core.config import Settings
from app.core.exceptions import EmbeddingFailedError

logger = logging.getLogger("evidencerag")

_DOWNLOAD_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)


def _ensure_local_model_downloaded() -> None:
    """Pre-fetch chromadb's ONNX model archive with a generous read timeout.

    chromadb's own downloader (chromadb.utils.embedding_functions
    .onnx_mini_lm_l6_v2.ONNXMiniLM_L6_V2._download) opens an httpx.stream
    with no explicit timeout, which defaults to a 5-second read timeout per
    chunk. On a slow or bursty connection that stalls briefly between
    chunks, this reliably fails partway through the ~79MB download with
    httpx.ReadTimeout. chromadb skips its own download step entirely if a
    valid archive already exists at its expected cache path (verified by
    SHA256), so pre-fetching it here - once, with a longer timeout - avoids
    the failure without patching chromadb itself.
    """
    from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import (
        ONNXMiniLM_L6_V2,
        _verify_sha256,
    )

    archive_path = os.path.join(ONNXMiniLM_L6_V2.DOWNLOAD_PATH, ONNXMiniLM_L6_V2.ARCHIVE_FILENAME)
    if os.path.exists(archive_path) and _verify_sha256(
        archive_path, ONNXMiniLM_L6_V2._MODEL_SHA256
    ):
        return

    os.makedirs(ONNXMiniLM_L6_V2.DOWNLOAD_PATH, exist_ok=True)
    logger.info("embedding_model_download_started")
    with httpx.stream(
        "GET", ONNXMiniLM_L6_V2.MODEL_DOWNLOAD_URL, timeout=_DOWNLOAD_TIMEOUT
    ) as response:
        response.raise_for_status()
        with open(archive_path, "wb") as file:
            for chunk in response.iter_bytes(chunk_size=1024 * 64):
                file.write(chunk)

    if not _verify_sha256(archive_path, ONNXMiniLM_L6_V2._MODEL_SHA256):
        os.remove(archive_path)
        raise EmbeddingFailedError(
            "Downloaded embedding model archive failed integrity verification."
        )
    logger.info("embedding_model_download_completed")


class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        if settings.embedding_provider != "local":
            raise ValueError(
                f"Unsupported embedding provider: '{settings.embedding_provider}'. "
                "Only 'local' is implemented in Phase 2."
            )

        from chromadb.utils import embedding_functions

        _ensure_local_model_downloaded()
        self._embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            # Cast to native float: chromadb's embeddings validator rejects a
            # list of numpy.float32 scalars (list(vector) preserves the numpy
            # scalar type), accepting only native float/int or a real ndarray.
            return [[float(x) for x in vector] for vector in self._embedding_fn(texts)]
        except Exception as exc:
            logger.exception("embedding_failed", extra={"chunk_count": len(texts)})
            raise EmbeddingFailedError("Failed to generate embeddings for document text.") from exc

    def embed_query(self, text: str) -> list[float]:
        try:
            return [float(x) for x in self._embedding_fn([text])[0]]
        except Exception as exc:
            logger.exception("query_embedding_failed")
            raise EmbeddingFailedError("Failed to generate an embedding for the question.") from exc
