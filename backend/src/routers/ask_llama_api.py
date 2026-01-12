import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import ollama
from src.schemas.rag import RAGResponse
from src.repository.chat_history import create_chat_history
from src.schemas.chat_history import ChatHistoryCreate
from src.database.config import get_db
from src.providers.chroma_provider import query_chunks
from sqlalchemy.orm import Session


router = APIRouter()


# -----------------------------
# Request model
# -----------------------------
class QueryRequest(BaseModel):
    question: str


# -----------------------------
# Helper function to build RAG prompt
# -----------------------------
# def build_rag_prompt(question: str, top_chunks: list[str]) -> str:
#     """
#     Build a prompt for RAG using the retrieved chunks as context.
#     """
#     context = "\n\n".join(top_chunks)
#     prompt = (
#         f"You are a helpful assistant. Use the following context to answer the question.\n\n"
#         f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
#     )
#     return prompt


def build_rag_prompt(question: str, top_chunks: list[str]) -> str:
    """
    Build a RAG prompt that ensures accurate answers strictly based on the provided context.
    """
    context = "\n\n".join(top_chunks)
    prompt = (
        "You are an expert academic advisor. Answer the question using only the context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Instructions:\n"
        "- Give a clear, complete answer in natural language.\n"
        "- Check eligibility lists carefully if present.\n"
        "- Reference context sections if helpful.\n"
        "- Combine info from multiple chunks if needed.\n"
        "- Say 'The information is not provided in the context.' if unknown.\n"
        "- Do NOT output JSON, braces, lists, or code.\n\n"
        "Answer:"
    )
    return prompt


# -----------------------------
# API endpoint
# -----------------------------
@router.post("/")
def ask_llama_rag(request: QueryRequest, db: Session = Depends(get_db)) -> RAGResponse:
    # Step 1: Retrieve top chunks from ChromaDB
    results = query_chunks(request.question)
    if not results:
        raise HTTPException(status_code=404, detail="No relevant chunks found")

    top_texts = [r["text"] for r in results]

    # Step 2: Build RAG prompt
    prompt = build_rag_prompt(request.question, top_texts)

    # Step 3: Call Ollama
    # gemma3:4b
    try:
        response = ollama.chat(
            model="llama3.2", messages=[{"role": "user", "content": prompt}]
        )

        # response = ollama.chat(
        #     model="gemma3:4b", messages=[{"role": "user", "content": prompt}]
        # )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

    answer = response["message"]["content"]

    # Step 4: Store chat history
    history_data = ChatHistoryCreate(
        question=request.question,
        answer=answer,
        source_chunks=json.dumps(top_texts),  # SQLite-safe
    )
    create_chat_history(history_data, db)

    # Step 5: Return response
    return RAGResponse(
        success=True,
        question=request.question,
        answer=answer,
        sources=top_texts,
    )
