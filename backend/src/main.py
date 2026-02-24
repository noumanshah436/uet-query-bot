from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import ingest_api, search_api, ask_llama_api, chat_history_api

app = FastAPI(title="RAG Backend")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ingest_api.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(search_api.router, prefix="/search", tags=["Search"])
app.include_router(ask_llama_api.router, prefix="/ask", tags=["Ask Ollama"])
app.include_router(chat_history_api.router, prefix="/history", tags=["Chat History"])
