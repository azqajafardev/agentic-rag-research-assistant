import io

from fastapi.testclient import TestClient

from tests.conftest import make_pdf_bytes
from tests.fakes import FakeLLMService


def _upload(client: TestClient, filename: str, content: bytes) -> str:
    response = client.post(
        "/api/documents/upload",
        files=[("files", (filename, io.BytesIO(content), "application/pdf"))],
    )
    assert response.status_code == 200
    return response.json()["documents"][0]["id"]


def test_chat_returns_grounded_answer_with_citation(
    client: TestClient, fake_llm_service: FakeLLMService
) -> None:
    pdf = make_pdf_bytes(["The proposed model was evaluated using the HAM10000 dataset."])
    document_id = _upload(client, "paper.pdf", pdf)

    # The fake embedding service is a bag-of-words hash (see tests/fakes.py), not a
    # real semantic model, so the question is phrased to share most vocabulary with
    # the chunk text - that's what drives similarity above the threshold here.
    response = client.post(
        "/api/chat", json={"question": "What was the proposed model evaluated using?"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is True
    assert body["answer"] == fake_llm_service.answer
    assert len(body["sources"]) >= 1
    source = body["sources"][0]
    assert source["filename"] == "paper.pdf"
    assert source["page"] == 1
    assert source["document_id"] == document_id
    assert 0.0 <= source["score"] <= 1.0
    assert len(fake_llm_service.calls) == 1


def test_chat_no_evidence_does_not_call_llm(
    client: TestClient, fake_llm_service: FakeLLMService
) -> None:
    pdf = make_pdf_bytes(["The proposed model was evaluated using the HAM10000 dataset."])
    _upload(client, "paper.pdf", pdf)

    response = client.post(
        "/api/chat", json={"question": "zzz qqq wibble unrelated nonsense gibberish xyzzy"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is False
    assert body["sources"] == []
    assert "couldn't find sufficient evidence" in body["answer"]
    assert len(fake_llm_service.calls) == 0


def test_chat_creates_conversation_when_missing(client: TestClient) -> None:
    pdf = make_pdf_bytes(["Datasets and evaluation results are described here."])
    _upload(client, "paper.pdf", pdf)

    response = client.post("/api/chat", json={"question": "datasets evaluation results"})

    assert response.status_code == 200
    assert response.json()["conversation_id"]


def test_chat_reuses_existing_conversation_id(client: TestClient) -> None:
    pdf = make_pdf_bytes(["Datasets and evaluation results are described here."])
    _upload(client, "paper.pdf", pdf)

    first = client.post(
        "/api/chat",
        json={"question": "datasets evaluation results", "conversation_id": "conversation_fixed"},
    )
    second = client.post(
        "/api/chat",
        json={"question": "datasets evaluation results", "conversation_id": "conversation_fixed"},
    )

    assert first.json()["conversation_id"] == "conversation_fixed"
    assert second.json()["conversation_id"] == "conversation_fixed"


def test_chat_document_ids_filter_restricts_scope(client: TestClient) -> None:
    pdf_a = make_pdf_bytes(["Shared vocabulary about datasets and evaluation metrics."])
    pdf_b = make_pdf_bytes(["Shared vocabulary about datasets and evaluation metrics."])
    doc_a = _upload(client, "a.pdf", pdf_a)
    doc_b = _upload(client, "b.pdf", pdf_b)

    response = client.post(
        "/api/chat",
        json={"question": "datasets evaluation metrics", "document_ids": [doc_a]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is True
    assert all(source["document_id"] == doc_a for source in body["sources"])
    assert all(source["document_id"] != doc_b for source in body["sources"])


def test_chat_rejects_empty_question(client: TestClient) -> None:
    response = client.post("/api/chat", json={"question": ""})
    assert response.status_code == 422  # pydantic min_length validation


def test_chat_deleted_document_vectors_are_excluded(client: TestClient) -> None:
    pdf = make_pdf_bytes(["Datasets and evaluation results are described here."])
    document_id = _upload(client, "paper.pdf", pdf)

    delete_response = client.delete(f"/api/documents/{document_id}")
    assert delete_response.status_code == 200

    response = client.post("/api/chat", json={"question": "datasets evaluation results"})

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is False
    assert body["sources"] == []
