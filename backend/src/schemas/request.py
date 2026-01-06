from pydantic import BaseModel

class IngestRequest(BaseModel):
    file_path: str


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
