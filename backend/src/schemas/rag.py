from pydantic import BaseModel


class RAGResponse(BaseModel):
    success: bool
    question: str
    answer: str
    sources: list[str]
