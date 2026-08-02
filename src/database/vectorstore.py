from sentence_transformers import SentenceTransformer
from src.core.document import Document
from src.core.exception import VectorStoreError
import chromadb
import logging
import uuid

logger = logging.getLogger(__name__)


class ChromaVectorStore:

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        persist_directory: str = "./chroma_db",
        collection_name: str = "documents",
        batch_size: int = 64,
    ):
        self.batch_size = batch_size
        self._top_k: int | None = None

        try:
            self.embedding_model = SentenceTransformer(
                f"sentence-transformers/{model_name}"
            )
        except Exception as e:
            raise VectorStoreError(
                f"Failed to load embedding model '{model_name}'"
            ) from e

        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            raise VectorStoreError("Failed to initialize ChromaDB client") from e

        logger.info(
            "VectorStore ready — model: %s, collection: %s", model_name, collection_name
        )

    def as_retriever(self, k: int):
        if k < 1:
            raise ValueError("k must be at least 1")
        self._top_k = k
        return self

    def add(self, chunks: list[Document]) -> None:
        valid = [c for c in chunks if c.content and c.content.strip()]

        if not valid:
            logger.warning("No valid chunks to add — all were empty")
            return

        for batch_start in range(0, len(valid), self.batch_size):
            batch = valid[batch_start : batch_start + self.batch_size]
            texts = [c.content for c in batch]
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False).tolist()
            ids = [str(uuid.uuid4()) for _ in batch]

            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=[c.metadata for c in batch],
            )

        logger.info("Added %d chunks to the vector store", len(valid))

    def search(self, query: str) -> list[Document]:
        if not self._top_k:
            raise ValueError(
                "top_k is not set — call as_retriever(k) before searching"
            )

        query_embedding = self.embedding_model.encode(query, show_progress_bar=False).tolist()

        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self._top_k,
        )

        output: list[Document] = []
        for doc, meta in zip(result["documents"][0], result["metadatas"][0]):
            output.append(Document(content=doc, metadata=meta))

        return output

    def count(self) -> int:
        return self.collection.count()

    def clear(self) -> None:
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Vector store collection cleared")
