from fastapi import APIRouter
from src.schemas.request import QueryRequest
from src.providers.chroma_provider import query_chunks

router = APIRouter()


@router.post("/")
def search(request: QueryRequest):
    results = query_chunks(request.question, request.top_k)
    return {
        "query": request.question,
        "results": results
    }
