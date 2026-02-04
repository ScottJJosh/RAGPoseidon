"""Module for loading and chunking earnings call transcripts."""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import config


class DocumentProcessor:
    """Handles loading and chunking of transcript documents."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """Initialize the document processor.

        Args:
            chunk_size: Size of each text chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def load_transcript(self, file_path: str, metadata: dict = None) -> Document:
        """Load a transcript from a text file.

        Args:
            file_path: Path to the transcript file
            metadata: Optional metadata to attach (e.g., quarter, year, company)

        Returns:
            Document object with the transcript content
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        doc_metadata = metadata or {}
        doc_metadata['source'] = file_path

        return Document(page_content=content, metadata=doc_metadata)

    def chunk_document(self, document: Document) -> List[Document]:
        """Split a document into chunks.

        Args:
            document: Document to chunk

        Returns:
            List of document chunks with preserved metadata
        """
        chunks = self.text_splitter.split_documents([document])
        return chunks

    def process_transcripts(self, transcript_files: List[tuple]) -> List[Document]:
        """Process multiple transcript files.

        Args:
            transcript_files: List of tuples (file_path, metadata_dict)

        Returns:
            List of all document chunks from all transcripts
        """
        all_chunks = []

        for file_path, metadata in transcript_files:
            doc = self.load_transcript(file_path, metadata)
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)

        return all_chunks
