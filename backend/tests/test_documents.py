import io

from fastapi.testclient import TestClient

from tests.conftest import make_pdf_bytes


def _upload(client: TestClient, filename: str, content: bytes, content_type: str = "application/pdf"):
    return client.post(
        "/api/documents/upload",
        files=[("files", (filename, io.BytesIO(content), content_type))],
    )


def test_upload_valid_pdf(client: TestClient) -> None:
    pdf_bytes = make_pdf_bytes(["Page one content about datasets and results."])

    response = _upload(client, "paper.pdf", pdf_bytes)

    assert response.status_code == 200
    body = response.json()
    assert len(body["documents"]) == 1
    document = body["documents"][0]
    assert document["filename"] == "paper.pdf"
    assert document["status"] == "indexed"


def test_upload_multiple_pdfs(client: TestClient) -> None:
    pdf_a = make_pdf_bytes(["Content A"])
    pdf_b = make_pdf_bytes(["Content B"])

    response = client.post(
        "/api/documents/upload",
        files=[
            ("files", ("a.pdf", io.BytesIO(pdf_a), "application/pdf")),
            ("files", ("b.pdf", io.BytesIO(pdf_b), "application/pdf")),
        ],
    )

    assert response.status_code == 200
    documents = response.json()["documents"]
    assert len(documents) == 2
    assert {doc["filename"] for doc in documents} == {"a.pdf", "b.pdf"}


def test_upload_rejects_invalid_extension(client: TestClient) -> None:
    response = _upload(client, "image.png", b"not a pdf", content_type="image/png")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FILE_TYPE"


def test_upload_rejects_empty_file(client: TestClient) -> None:
    response = _upload(client, "empty.pdf", b"")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_FILE"


def test_upload_rejects_oversized_file(client: TestClient) -> None:
    # test client fixture configures max_upload_size_mb=1
    oversized = b"%PDF-1.4\n" + (b"0" * (2 * 1024 * 1024))

    response = _upload(client, "big.pdf", oversized)

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_upload_rejects_corrupted_pdf(client: TestClient) -> None:
    response = _upload(client, "corrupt.pdf", b"%PDF-1.4\nnot really a pdf structure")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FILE_TYPE"


def test_list_documents(client: TestClient) -> None:
    _upload(client, "paper.pdf", make_pdf_bytes(["Some content"]))

    response = client.get("/api/documents")

    assert response.status_code == 200
    documents = response.json()["documents"]
    assert len(documents) == 1
    assert documents[0]["filename"] == "paper.pdf"
    assert documents[0]["page_count"] == 1
    assert documents[0]["chunk_count"] >= 1


def test_get_document_details(client: TestClient) -> None:
    upload_response = _upload(client, "paper.pdf", make_pdf_bytes(["Content"]))
    document_id = upload_response.json()["documents"][0]["id"]

    response = client.get(f"/api/documents/{document_id}")

    assert response.status_code == 200
    assert response.json()["id"] == document_id


def test_get_document_details_not_found(client: TestClient) -> None:
    response = client.get("/api/documents/doc_does_not_exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_delete_document(client: TestClient) -> None:
    upload_response = _upload(client, "paper.pdf", make_pdf_bytes(["Content"]))
    document_id = upload_response.json()["documents"][0]["id"]

    delete_response = client.delete(f"/api/documents/{document_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True

    get_response = client.get(f"/api/documents/{document_id}")
    assert get_response.status_code == 404


def test_delete_missing_document_returns_404(client: TestClient) -> None:
    response = client.delete("/api/documents/doc_does_not_exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"
