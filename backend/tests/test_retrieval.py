import pytest

from app.rag.chunker import Chunk
from app.services.vector_service import VectorService
from tests.fakes import FakeEmbeddingService


@pytest.fixture()
def vector_service(tmp_path) -> VectorService:
    return VectorService(tmp_path / "chroma")


def _chunk(chunk_id: str, document_id: str, page: int, text: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id, document_id=document_id, filename="paper.pdf", page=page, text=text
    )


def test_vector_indexing_and_query(vector_service: VectorService) -> None:
    embedder = FakeEmbeddingService()
    chunks = [
        _chunk("doc_1_p1_c1", "doc_1", 1, "The HAM10000 dataset was used for training."),
        _chunk("doc_1_p2_c1", "doc_1", 2, "Completely unrelated content about gardening."),
    ]
    embeddings = embedder.embed_documents([c.text for c in chunks])
    vector_service.upsert_chunks(chunks, embeddings)

    assert vector_service.count() == 2

    query_embedding = embedder.embed_query("What dataset was used for training?")
    matches = vector_service.query(query_embedding, top_k=5)

    assert len(matches) == 2
    best = matches[0]
    assert best.chunk_id == "doc_1_p1_c1"
    assert best.document_id == "doc_1"
    assert best.filename == "paper.pdf"
    assert best.page == 1
    assert best.score > matches[1].score


def test_vector_query_document_id_filter(vector_service: VectorService) -> None:
    embedder = FakeEmbeddingService()
    chunk_a = _chunk("doc_a_c1", "doc_a", 1, "shared topic words about datasets")
    chunk_b = _chunk("doc_b_c1", "doc_b", 1, "shared topic words about datasets")
    embeddings = embedder.embed_documents([chunk_a.text, chunk_b.text])
    vector_service.upsert_chunks([chunk_a, chunk_b], embeddings)

    query_embedding = embedder.embed_query("datasets")
    matches = vector_service.query(query_embedding, top_k=5, document_ids=["doc_a"])

    assert len(matches) == 1
    assert matches[0].document_id == "doc_a"


def test_vector_query_empty_document_ids_returns_nothing(vector_service: VectorService) -> None:
    matches = vector_service.query([0.1] * 8, top_k=5, document_ids=[])
    assert matches == []


def test_vector_upsert_is_idempotent(vector_service: VectorService) -> None:
    embedder = FakeEmbeddingService()
    chunk = _chunk("doc_1_p1_c1", "doc_1", 1, "some text")
    embeddings = embedder.embed_documents([chunk.text])

    vector_service.upsert_chunks([chunk], embeddings)
    vector_service.upsert_chunks([chunk], embeddings)

    assert vector_service.count() == 1


def test_vector_delete_document(vector_service: VectorService) -> None:
    embedder = FakeEmbeddingService()
    chunks = [
        _chunk("doc_1_c1", "doc_1", 1, "text one"),
        _chunk("doc_2_c1", "doc_2", 1, "text two"),
    ]
    embeddings = embedder.embed_documents([c.text for c in chunks])
    vector_service.upsert_chunks(chunks, embeddings)

    vector_service.delete_document("doc_1")

    assert vector_service.count() == 1
    remaining = vector_service.query(embedder.embed_query("text"), top_k=5)
    assert all(match.document_id == "doc_2" for match in remaining)
