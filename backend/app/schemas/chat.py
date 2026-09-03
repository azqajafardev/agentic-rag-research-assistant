from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    document_ids: list[str] | None = None
    conversation_id: str | None = None


class SourceResponse(BaseModel):
    id: str
    document_id: str
    filename: str
    page: int
    score: float
    evidence: str


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    grounded: bool
    sources: list[SourceResponse]
