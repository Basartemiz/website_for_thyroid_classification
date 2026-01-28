"""
ChromaDB vector store operations for RAG pipeline.
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings
from django.conf import settings

from .embeddings import get_embeddings


class VectorStore:
    """ChromaDB vector store wrapper for thyroid guidelines."""

    COLLECTION_NAME = "thyroid_guidelines"

    def __init__(self, persist_directory: Optional[Path] = None):
        """
        Initialize the vector store.

        Args:
            persist_directory: Path to persist the vector store
        """
        self.persist_directory = persist_directory or settings.VECTORSTORE_DIR

        # Ensure directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )

        self._collection = None

    @property
    def collection(self):
        """Get or create the collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add documents to the vector store.

        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
        """
        embeddings = get_embeddings(documents)

        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def query(
        self,
        query_text: str,
        n_results: int = 6,
        where: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store for similar documents.

        Args:
            query_text: Query string
            n_results: Number of results to return
            where: Optional filter criteria

        Returns:
            Dictionary with documents, metadatas, distances, and ids
        """
        query_embedding = get_embeddings([query_text])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        return {
            'documents': results['documents'][0] if results['documents'] else [],
            'metadatas': results['metadatas'][0] if results['metadatas'] else [],
            'distances': results['distances'][0] if results['distances'] else [],
            'ids': results['ids'][0] if results['ids'] else [],
        }

    def is_ready(self) -> bool:
        """Check if the vector store has documents."""
        try:
            count = self.collection.count()
            return count > 0
        except Exception:
            return False

    def count(self) -> int:
        """Return the number of documents in the store."""
        return self.collection.count()

    def delete_collection(self) -> None:
        """Delete the collection (for re-ingestion)."""
        try:
            self.client.delete_collection(self.COLLECTION_NAME)
            self._collection = None
        except Exception:
            pass


# Global instance
_vectorstore_instance: Optional[VectorStore] = None


def get_vectorstore() -> VectorStore:
    """Get or create the global vector store instance."""
    global _vectorstore_instance
    if _vectorstore_instance is None:
        _vectorstore_instance = VectorStore()
    return _vectorstore_instance
