import os
import warnings
from typing import Optional
from loguru import logger

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=UserWarning)


CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "text_chunks"


class ChromaVectorStore:
    _instance: Optional["ChromaVectorStore"] = None

    def __init__(self):
        logger.info("Initializing ChromaVectorStore...")

        # import here to avoid startup cost
        import chromadb
        from sentence_transformers import SentenceTransformer

        logger.info("Loading SentenceTransformer model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Model loaded successfully")

        logger.info("Creating PersistentClient for ChromaDB...")
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self._get_or_create(COLLECTION_NAME)
        logger.info("ChromaVectorStore initialized successfully")

    def _get_or_create(self, name: str):
        names = [c.name for c in self.client.list_collections()]
        if name in names:
            logger.info(f"Collection '{name}' exists, retrieving it")
            return self.client.get_collection(name)
        logger.info(f"Collection '{name}' does not exist, creating it")
        return self.client.create_collection(name)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            logger.info("Creating new instance of ChromaVectorStore")
            cls._instance = cls()
        else:
            logger.info("Using existing instance of ChromaVectorStore")
        return cls._instance

    def embed(self, texts: list[str]):
        return self.model.encode(texts).tolist()

    def get_top_chunks(self, question: str, top_k: int = 3) -> list[dict]:
        """
        Returns the top_k chunks in a structured format:
        [{"document": doc, "score": score, "source": source}, ...]
        """
        logger.info(f"Retrieving top {top_k} chunks for question")
        question_embedding = self.model.encode([question]).tolist()

        results = self.collection.query(
            query_embeddings=question_embedding, n_results=top_k
        )

        top_chunks = [
            {"document": doc, "score": score, "source": meta["source"]}
            for doc, score, meta in zip(
                results["documents"][0],
                results["distances"][0],
                results["metadatas"][0],
            )
        ]
        logger.info(f"Retrieved {len(top_chunks)} chunks")
        return top_chunks

    def add(self, ids, documents, embeddings, metadatas):
        logger.info(f"Adding {len(documents)} documents to ChromaDB")
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.info("Documents added successfully")
