"""Page-aware word-based chunking.

This is a deliberately simple MVP chunker: it splits each page's text into
overlapping word windows. Semantic/section-aware chunking is a Phase 2+
concern and is intentionally not implemented here.
"""

from dataclasses import dataclass

CHUNK_SIZE_WORDS = 800
CHUNK_OVERLAP_WORDS = 120


@dataclass
class PageText:
    page: int
    text: str


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    filename: str
    page: int
    text: str


def chunk_pages(
    pages: list[PageText],
    *,
    document_id: str,
    filename: str,
    chunk_size: int = CHUNK_SIZE_WORDS,
    overlap: int = CHUNK_OVERLAP_WORDS,
) -> list[Chunk]:
    """Split page text into overlapping, page-aware chunks.

    Chunks never span multiple pages so that every chunk keeps a single,
    accurate page citation.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks: list[Chunk] = []

    for page in pages:
        words = page.text.split()
        if not words:
            continue

        chunk_index = 0
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = " ".join(words[start:end]).strip()

            if chunk_text:
                chunk_index += 1
                chunks.append(
                    Chunk(
                        chunk_id=f"{document_id}_page_{page.page}_chunk_{chunk_index:02d}",
                        document_id=document_id,
                        filename=filename,
                        page=page.page,
                        text=chunk_text,
                    )
                )

            if end == len(words):
                break
            start = end - overlap

    return chunks
