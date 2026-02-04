"""Vector store module for storing and retrieving document embeddings."""

from typing import List
from langchain_core.documents import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import config


class VectorStore:
    """Manages vector embeddings and similarity search."""

    def __init__(self, embedding_model: str = None, persist_directory: str = None):
        """Initialize the vector store.

        Args:
            embedding_model: Name of the Ollama embedding model
            persist_directory: Directory to persist the vector database
        """
        self.embedding_model = embedding_model or config.EMBEDDING_MODEL
        self.persist_directory = persist_directory or config.PERSIST_DIRECTORY

        # Initialize Ollama embeddings
        self.embeddings = OllamaEmbeddings(model=self.embedding_model)
        self.vectorstore = None

    def create_vectorstore(self, documents: List[Document]) -> None:
        """Create and persist vector store from documents.

        Args:
            documents: List of document chunks to embed and store
        """
        # Delete existing collection if it exists to avoid duplicates
        try:
            existing_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=config.COLLECTION_NAME
            )
            existing_store.delete_collection()
            print("Deleted existing collection to prevent duplicates")
        except Exception:
            # Collection doesn't exist, which is fine
            pass

        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=config.COLLECTION_NAME
        )
        print(f"Created vector store with {len(documents)} document chunks")

    def load_vectorstore(self) -> None:
        """Load existing vector store from disk."""
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=config.COLLECTION_NAME
        )
        print("Loaded existing vector store")

    def get_collection_count(self) -> int:
        """Get the number of documents in the vector store.

        Returns:
            Number of documents in the collection
        """
        if not self.vectorstore:
            return 0
        return self.vectorstore._collection.count()

    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """Search for most relevant document chunks.

        Args:
            query: Query text to search for
            k: Number of top results to return

        Returns:
            List of most relevant document chunks
        """
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Call create_vectorstore or load_vectorstore first.")

        k = k or config.TOP_K_CHUNKS
        results = self.vectorstore.similarity_search(query, k=k)
        return results

    def add_documents(self, documents: List[Document]) -> None:
        """Add new documents to existing vector store.

        Args:
            documents: List of document chunks to add
        """
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Call create_vectorstore first.")

        self.vectorstore.add_documents(documents)
        print(f"Added {len(documents)} new document chunks to vector store")
