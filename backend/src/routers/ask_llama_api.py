from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import ollama
from src.providers.chroma_provider import query_chunks

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
def ask_llama_rag(request: QueryRequest):
    # Step 1: Retrieve top chunks from ChromaDB
    results = query_chunks(request.question)
    if not results:
        raise HTTPException(status_code=404, detail="No relevant chunks found")

    top_texts = [r["text"] for r in results]

    # Step 2: Build RAG prompt
    prompt = build_rag_prompt(request.question, top_texts)

    # Step 3: Call Ollama
    try:
        response = ollama.chat(
            model="llama3.2", messages=[{"role": "user", "content": prompt}]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

    return {
        "query": request.question,
        "answer": response["message"]["content"],
        "top_chunks_used": top_texts,
    }
