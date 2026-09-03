"""Citation engine: turns retrieved evidence into the canonical source list.

Sources are built exclusively from retrieved chunks. The LLM never supplies
citation metadata - it only sees the already-numbered SOURCE blocks produced
from this list (see context_builder.py) and is instructed to cite by number.
"""

from dataclasses import dataclass

from app.services.retrieval_service import EvidenceChunk


@dataclass
class Source:
    id: str
    document_id: str
    filename: str
    page: int
    score: float
    evidence: str


def build_sources(evidence: list[EvidenceChunk]) -> list[Source]:
    return [
        Source(
            id=f"source_{index + 1}",
            document_id=chunk.document_id,
            filename=chunk.filename,
            page=chunk.page,
            score=round(chunk.score, 4),
            evidence=chunk.text,
        )
        for index, chunk in enumerate(evidence)
    ]
