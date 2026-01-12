from pydantic import BaseModel

class IngestRequest(BaseModel):
    file_path: str = "docs/UET lahore Document.pdf"


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
