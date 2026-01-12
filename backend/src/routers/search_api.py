from fastapi import APIRouter
from loguru import logger
from src.schemas.request import QueryRequest
from src.vector_store.chroma import ChromaVectorStore

router = APIRouter()


@router.post("/")
def search(request: QueryRequest):
    logger.info(f"Received search query: {request.question}")

    store = ChromaVectorStore.get_instance()
    logger.info("ChromaVectorStore instance retrieved")

    results = store.get_top_chunks(
        question=request.question,
        top_k=request.top_k,
    )

    return {
        "query": request.question,
        "results": results,
    }
