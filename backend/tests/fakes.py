"""Deterministic, offline test doubles for the embedding and LLM services.

Real embedding downloads a model and the real LLM calls a paid API - neither
is acceptable in automated tests. These fakes are wired in via FastAPI
dependency overrides in conftest.py.

The fake embedding is a simple feature-hashed bag-of-words vector: text
sharing vocabulary gets a high cosine similarity, text sharing no vocabulary
gets a similarity of ~0. That makes retrieval/threshold behavior testable
without a real model.
"""

import hashlib
import re
from collections import Counter

from app.models.conversation import Message

_VECTOR_DIM = 64
_WORD_RE = re.compile(r"[a-z0-9]+")


def _hash_bucket(word: str) -> int:
    digest = hashlib.sha256(word.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % _VECTOR_DIM


def _bag_of_words_vector(text: str) -> list[float]:
    words = _WORD_RE.findall(text.lower())
    vector = [0.0] * _VECTOR_DIM
    for word, count in Counter(words).items():
        vector[_hash_bucket(word)] += float(count)
    return vector


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.embed_documents_calls = 0
        self.embed_query_calls = 0

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.embed_documents_calls += 1
        return [_bag_of_words_vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        self.embed_query_calls += 1
        return _bag_of_words_vector(text)


class FakeLLMService:
    def __init__(self, answer: str = "This is a fake grounded answer.") -> None:
        self.answer = answer
        self.calls: list[dict] = []

    def generate(self, question: str, context: str, history: list[Message]) -> str:
        self.calls.append({"question": question, "context": context, "history": history})
        return self.answer
