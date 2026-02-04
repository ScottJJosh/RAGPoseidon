"""Configuration settings for the RAG application."""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.resolve()

# Ollama settings
EMBEDDING_MODEL = "nomic-embed-text"  # Popular Ollama embedding model
LLM_MODEL = "qwen2.5:14b"  # Stronger model for better reasoning and analysis

# Chunking settings
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks

# Retrieval settings
TOP_K_CHUNKS = 20  # Number of relevant chunks to retrieve per question

# Directory paths (absolute paths for cross-platform compatibility)
TRANSCRIPTS_DIR = PROJECT_ROOT / "transcripts"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"
DOCS_DIR = PROJECT_ROOT / "docs"
QUESTIONS_FILE = DOCS_DIR / "10Q.txt"

# Vector store settings
PERSIST_DIRECTORY = str(CHROMA_DB_DIR)  # ChromaDB needs string path
COLLECTION_NAME = "earnings_transcripts"
