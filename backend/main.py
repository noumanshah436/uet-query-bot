from fastapi import FastAPI
from src.routers import ingest_api, search_api, ask_llama_api, chat_history_api

app = FastAPI(title="RAG Backend")

app.include_router(ingest_api.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(search_api.router, prefix="/search", tags=["Search"])
app.include_router(ask_llama_api.router, prefix="/ask", tags=["Ask llama"])
app.include_router(chat_history_api.router, prefix="/history", tags=["Chat History"])
