from app.core.config import Settings
from app.rag.citation import build_sources
from app.rag.context_builder import build_context
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.retrieval_service import EvidenceChunk


def _evidence(chunk_id: str, page: int, score: float, text: str) -> EvidenceChunk:
    return EvidenceChunk(
        chunk_id=chunk_id,
        document_id="doc_1",
        filename="paper.pdf",
        page=page,
        text=text,
        score=score,
    )


def test_build_sources_preserves_metadata_and_orders_by_input() -> None:
    evidence = [
        _evidence("c1", 4, 0.91, "HAM10000 dataset details."),
        _evidence("c2", 8, 0.62, "Additional discussion."),
    ]

    sources = build_sources(evidence)

    assert [s.id for s in sources] == ["source_1", "source_2"]
    assert sources[0].filename == "paper.pdf"
    assert sources[0].page == 4
    assert sources[0].score == 0.91
    assert sources[0].evidence == "HAM10000 dataset details."


def test_build_sources_never_invents_metadata() -> None:
    evidence = [_evidence("c1", 4, 0.91, "text")]
    sources = build_sources(evidence)
    # every field traces directly back to the retrieved chunk, nothing synthesized
    assert sources[0].document_id == evidence[0].document_id
    assert sources[0].page == evidence[0].page


def test_context_builder_includes_all_sources_within_budget() -> None:
    evidence = [_evidence("c1", 1, 0.9, "short evidence text")]
    sources = build_sources(evidence)

    context = build_context(sources, max_chars=10000)

    assert "SOURCE 1" in context
    assert "Document: paper.pdf" in context
    assert "Page: 1" in context
    assert "short evidence text" in context


def test_context_builder_respects_max_chars_budget() -> None:
    evidence = [
        _evidence("c1", 1, 0.9, "a" * 100),
        _evidence("c2", 2, 0.8, "b" * 100),
        _evidence("c3", 3, 0.7, "c" * 100),
    ]
    sources = build_sources(evidence)

    context = build_context(sources, max_chars=150)

    assert "SOURCE 1" in context
    assert "SOURCE 3" not in context


def test_embedding_service_rejects_unsupported_provider() -> None:
    settings = Settings(embedding_provider="unsupported-provider")
    try:
        EmbeddingService(settings)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_llm_service_rejects_unsupported_provider() -> None:
    settings = Settings(llm_provider="unsupported-provider")
    try:
        LLMService(settings)
        assert False, "expected ValueError"
    except ValueError:
        pass
