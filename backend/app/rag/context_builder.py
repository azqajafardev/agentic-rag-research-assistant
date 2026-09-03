"""Convert canonical sources into structured LLM context, size-bounded."""

from app.rag.citation import Source


def build_context(sources: list[Source], *, max_chars: int) -> str:
    """Render sources as numbered SOURCE blocks, stopping before max_chars.

    Metadata (document/page) is never dropped: a source is either included in
    full or omitted entirely, never truncated mid-block.
    """
    blocks: list[str] = []
    total_chars = 0

    for index, source in enumerate(sources):
        block = (
            f"SOURCE {index + 1}\n"
            f"Document: {source.filename}\n"
            f"Page: {source.page}\n\n"
            f"Evidence:\n{source.evidence}"
        )

        added_length = len(block) + (2 if blocks else 0)  # account for the join separator
        if blocks and total_chars + added_length > max_chars:
            break

        blocks.append(block)
        total_chars += added_length

    return "\n\n".join(blocks)
