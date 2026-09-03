from app.rag.chunker import PageText, chunk_pages


def test_short_page_produces_single_chunk() -> None:
    pages = [PageText(page=1, text="hello world this is a short page")]
    chunks = chunk_pages(pages, document_id="doc_1", filename="a.pdf")

    assert len(chunks) == 1
    assert chunks[0].page == 1
    assert chunks[0].document_id == "doc_1"
    assert chunks[0].filename == "a.pdf"
    assert chunks[0].chunk_id == "doc_1_page_1_chunk_01"


def test_long_page_produces_multiple_overlapping_chunks() -> None:
    words = [f"word{i}" for i in range(2000)]
    pages = [PageText(page=3, text=" ".join(words))]

    chunks = chunk_pages(pages, document_id="doc_2", filename="b.pdf", chunk_size=800, overlap=120)

    assert len(chunks) > 1
    assert all(chunk.page == 3 for chunk in chunks)

    first_words = chunks[0].text.split()
    second_words = chunks[1].text.split()
    overlap_words = set(first_words[-120:])
    assert overlap_words & set(second_words[:120])


def test_chunks_never_span_pages() -> None:
    pages = [
        PageText(page=1, text=" ".join(f"a{i}" for i in range(50))),
        PageText(page=2, text=" ".join(f"b{i}" for i in range(50))),
    ]
    chunks = chunk_pages(pages, document_id="doc_3", filename="c.pdf")

    pages_seen = {chunk.page for chunk in chunks}
    assert pages_seen == {1, 2}
    for chunk in chunks:
        prefix = "a" if chunk.page == 1 else "b"
        assert all(word.startswith(prefix) for word in chunk.text.split())


def test_metadata_preserved_on_every_chunk() -> None:
    pages = [PageText(page=5, text="some meaningful content for the chunk")]
    chunks = chunk_pages(pages, document_id="doc_42", filename="paper.pdf")

    for chunk in chunks:
        assert chunk.document_id == "doc_42"
        assert chunk.filename == "paper.pdf"
        assert chunk.page == 5
        assert chunk.chunk_id.startswith("doc_42_page_5_chunk_")


def test_no_empty_chunks_from_blank_pages() -> None:
    pages = [PageText(page=1, text="   "), PageText(page=2, text="real content here")]
    chunks = chunk_pages(pages, document_id="doc_4", filename="d.pdf")

    assert all(chunk.text.strip() for chunk in chunks)
    assert all(chunk.page == 2 for chunk in chunks)
