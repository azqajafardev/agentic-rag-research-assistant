from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    backend: str
    database: str
    vector_db: str
