import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from src.vector_store.chroma import ChromaVectorStore
from src.services.prompt_service import PromptService
from src.services.llm_service import LLMService
from src.schemas.rag import RAGResponse
from src.repository.chat_history import create_chat_history
from src.schemas.chat_history import ChatHistoryCreate
from src.database.config import get_db

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3


@router.post("/", response_model=RAGResponse)
def ask_llama_rag(
    request: QueryRequest,
    db: Session = Depends(get_db),
):
    logger.info(f"Received question: {request.question}")

    # --- Vector store (singleton) ---
    vector_store = ChromaVectorStore.get_instance()
    logger.info("ChromaVectorStore instance retrieved")

    # --- Retrieve ---
    results = vector_store.get_top_chunks(
        question=request.question,
        top_k=request.top_k,
    )

    text_chuncks = [c["document"] for c in results]

    # --- Prompt ---
    prompt = PromptService.build(request.question, text_chuncks)
    logger.info("RAG prompt built")

    # --- LLM ---
    llm = LLMService()
    answer = llm.generate(prompt)
    logger.info("LLM generated answer")

    # --- Store history ---
    history_data = ChatHistoryCreate(
        question=request.question,
        answer=answer,
        source_chunks=json.dumps(text_chuncks),
    )
    create_chat_history(history_data, db)
    logger.info("Chat history stored in DB")

    # --- Response ---
    return RAGResponse(
        success=True,
        question=request.question,
        answer=answer,
        sources=text_chuncks,
    )
