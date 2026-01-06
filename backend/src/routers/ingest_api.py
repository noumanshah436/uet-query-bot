from fastapi import APIRouter, HTTPException
import os
import json
from src.schemas.request import IngestRequest
from src.utils.chuncker import chunk_text
from src.utils.pdf_reader import read_pdf
from src.providers.chroma_provider import add_chunks


router = APIRouter()


def save_chunks_to_file(chunks: list[str], file_path: str):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Chunks saved to {file_path}")


@router.post("/pdf")
def ingest_pdf(request: IngestRequest):
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Read and clean PDF
    text = read_pdf(request.file_path)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted")

    # Create chunks
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks created from PDF")

    # Save chunks as a list of strings
    output_file = (
        os.path.splitext(os.path.basename(request.file_path))[0] + "_chunks.json"
    )
    save_chunks_to_file(chunks, output_file)

    # Optionally add to your embeddings collection
    add_chunks(chunks, source=os.path.basename(request.file_path))

    return {
        "message": "PDF ingested successfully",
        "chunks_created": len(chunks),
        "saved_file": output_file,
    }
