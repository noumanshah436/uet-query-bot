from fastapi import FastAPI
from src.routers import ingest_api, search_api, ask_llama_api

app = FastAPI(title="RAG Backend")

app.include_router(ingest_api.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(search_api.router, prefix="/search", tags=["Search"])
app.include_router(ask_llama_api.router, prefix="/ask", tags=["Ask llama"])
