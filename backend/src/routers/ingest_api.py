from fastapi import APIRouter, HTTPException
import os
import json
from loguru import logger

from src.schemas.request import IngestRequest
from src.utils.chuncker import chunk_text
from src.utils.pdf_reader import read_pdf
from src.vector_store.chroma import ChromaVectorStore

router = APIRouter()


def save_chunks_to_file(chunks: list[str], file_path: str):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    logger.info(f"Chunks saved to file: {file_path}")


@router.post("/pdf")
def ingest_pdf(request: IngestRequest):
    logger.info(f"Starting PDF ingestion: {request.file_path}")

    if not os.path.exists(request.file_path):
        logger.error("File not found")
        raise HTTPException(404, "File not found")

    text = read_pdf(request.file_path)
    logger.info("PDF read successfully")

    if not text.strip():
        logger.error("No text extracted from PDF")
        raise HTTPException(400, "No text extracted")

    chunks = chunk_text(text)
    logger.info(f"Text chunked into {len(chunks)} chunks")

    if not chunks:
        logger.error("No chunks created")
        raise HTTPException(400, "No chunks created")

    store = ChromaVectorStore.get_instance()
    logger.info("ChromaVectorStore instance retrieved")

    embeddings = store.embed(chunks)
    logger.info("Embeddings created")

    start_index = store.collection.count()
    ids = [
        f"{os.path.basename(request.file_path)}_{i}"
        for i in range(start_index, start_index + len(chunks))
    ]
    metadatas = [{"source": os.path.basename(request.file_path)} for _ in chunks]

    store.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    logger.info("Chunks added to ChromaDB")

    output_file = (
        os.path.splitext(os.path.basename(request.file_path))[0] + "_chunks.json"
    )
    save_chunks_to_file(chunks, output_file)

    logger.info("PDF ingestion completed")

    return {
        "message": "PDF ingested successfully",
        "chunks_created": len(chunks),
        "saved_file": output_file,
    }
