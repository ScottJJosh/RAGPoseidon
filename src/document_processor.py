"""Module for loading and chunking earnings call transcripts."""

import os
import re
from typing import List, Dict
from pathlib import Path
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

    @staticmethod
    def discover_transcripts(base_dir: Path = None) -> List[tuple]:
        """Discover all transcripts in the folder structure.

        Expected structure: transcripts/industry/company/quarter_year.txt

        Args:
            base_dir: Base transcripts directory (Path object or None to use config default)

        Returns:
            List of tuples (file_path, metadata_dict) where metadata contains
            industry, company, quarter, and year
        """
        transcript_files = []

        # Use config default if not provided
        if base_dir is None:
            base_path = config.TRANSCRIPTS_DIR
        else:
            base_path = Path(base_dir) if not isinstance(base_dir, Path) else base_dir

        if not base_path.exists():
            return transcript_files

        # Pattern to match quarter_year.txt files (e.g., Q3_2024.txt, Q4_2024.txt)
        quarter_pattern = re.compile(r'^(Q[1-4])_(\d{4})\.txt$', re.IGNORECASE)

        # Walk through industry/company/quarter_year.txt structure
        for industry_dir in base_path.iterdir():
            if not industry_dir.is_dir():
                continue

            industry = industry_dir.name

            for company_dir in industry_dir.iterdir():
                if not company_dir.is_dir():
                    continue

                company = company_dir.name

                for file_path in company_dir.iterdir():
                    if not file_path.is_file():
                        continue

                    match = quarter_pattern.match(file_path.name)
                    if match:
                        quarter_code = match.group(1).upper()  # Q3, Q4, etc.
                        year = match.group(2)
                        quarter = f"{quarter_code} {year}"  # "Q3 2024"

                        metadata = {
                            "industry": industry,
                            "company": company,
                            "quarter": quarter,
                            "year": year,
                            "quarter_code": quarter_code
                        }

                        transcript_files.append((str(file_path), metadata))

        return sorted(transcript_files, key=lambda x: (x[1]['industry'], x[1]['company'], x[1]['year'], x[1]['quarter_code']))

    @staticmethod
    def get_available_metadata(transcript_files: List[tuple]) -> Dict[str, set]:
        """Extract all unique industries, companies, quarters, and years from transcript files.

        Args:
            transcript_files: List of tuples (file_path, metadata_dict)

        Returns:
            Dictionary with sets of unique values for each metadata field
        """
        industries = set()
        companies = set()
        quarters = set()
        years = set()

        for _, metadata in transcript_files:
            industries.add(metadata.get('industry'))
            companies.add(metadata.get('company'))
            quarters.add(metadata.get('quarter'))
            years.add(metadata.get('year'))

        return {
            'industries': sorted(list(industries)),
            'companies': sorted(list(companies)),
            'quarters': sorted(list(quarters)),
            'years': sorted(list(years))
        }
