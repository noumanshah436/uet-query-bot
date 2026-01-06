import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "text_chunks"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_PATH)

if COLLECTION_NAME not in [c.name for c in client.list_collections()]:
    collection = client.create_collection(name=COLLECTION_NAME)
else:
    collection = client.get_collection(name=COLLECTION_NAME)


def add_chunks(chunks: list[str], source: str):
    embeddings = model.encode(chunks).tolist()

    start = collection.count()
    ids = [f"{source}_{i}" for i in range(start, start + len(chunks))]
    metadatas = [{"source": source} for _ in chunks]

    collection.add(
        ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas
    )


def query_chunks(question: str, top_k: int = 3):
    question_embedding = model.encode([question]).tolist()

    results = collection.query(query_embeddings=question_embedding, n_results=top_k)

    return [
        {"text": doc, "score": score, "source": meta["source"]}
        for doc, score, meta in zip(
            results["documents"][0], results["distances"][0], results["metadatas"][0]
        )
    ]
