"""Configuration settings for the RAG application."""

# Ollama settings
EMBEDDING_MODEL = "nomic-embed-text"  # Popular Ollama embedding model
LLM_MODEL = "qwen2.5:14b"  # Stronger model for better reasoning and analysis

# Chunking settings
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks

# Retrieval settings
TOP_K_CHUNKS = 20  # Number of relevant chunks to retrieve per question

# Vector store settings
PERSIST_DIRECTORY = "./chroma_db"
COLLECTION_NAME = "earnings_transcripts"
