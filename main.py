"""Main RAG pipeline for analyzing earnings call transcripts."""

import os
import json
from document_processor import DocumentProcessor
from vector_store import VectorStore
from qa_system import QASystem
from output_formatter import OutputFormatter


def load_questions(questions_file: str) -> list:
    """Load questions from the 10Q.txt file.

    Args:
        questions_file: Path to the questions file

    Returns:
        List of question strings
    """
    questions = [
        "What phrases were consistent with the previous quarter commentary?",
        "What phrases were different from the previous quarter commentary?",
        "Was guidance revised? Why?",
        "What did the company say was going well?",
        "What did the company say needed improvement?",
        "What are announcements or goals stated for the next quarter?",
        "How does the company expect to improve Sales and Margins?",
        "How does the company expect to improve Free Cash Flow and what is Capex expected to be over the next quarter or next 12 months?",
        "What's the company's assessment of the consumer and economy?",
        "Was there mentions around restructuring or distress? -Layoffs, dispositions, refinancing challenges, etc."
    ]
    return questions


def main():
    """Run the RAG pipeline."""
    print("=== Earnings Transcript RAG System ===\n")

    # Define transcript files
    transcript_files = [
        ("transcripts/cvs_Q3.txt", {"quarter": "Q3 2024", "company": "CVS"}),
        ("transcripts/cvs_Q4.txt", {"quarter": "Q4 2024", "company": "CVS"}),
    ]

    # Check if we should create a new vector store or load existing
    rebuild_store = input("Rebuild vector store from transcripts? (y/n): ").lower() == 'y'

    # Initialize components
    print("\nInitializing components...")
    doc_processor = DocumentProcessor()
    vector_store = VectorStore()
    qa_system = QASystem()
    output_formatter = OutputFormatter()

    total_chunks = 0
    if rebuild_store:
        print("\nProcessing transcripts...")

        # Check if transcript files exist
        existing_files = [(path, meta) for path, meta in transcript_files if os.path.exists(path)]

        if not existing_files:
            print("\nWARNING: No transcript files found!")
            print("Please create a 'transcripts' directory and add your transcript files.")
            print("Expected files:")
            for path, meta in transcript_files:
                print(f"  - {path}")
            return

        # Process transcripts
        chunks = doc_processor.process_transcripts(existing_files)
        total_chunks = len(chunks)
        print(f"Created {total_chunks} chunks from {len(existing_files)} transcripts")

        # Create vector store
        print("\nCreating vector store with embeddings...")
        vector_store.create_vectorstore(chunks)
        print("Vector store created successfully!")

    else:
        # Load existing vector store
        print("\nLoading existing vector store...")
        try:
            vector_store.load_vectorstore()
            total_chunks = vector_store.get_collection_count()
            print(f"Vector store contains {total_chunks} chunks")
        except Exception as e:
            print(f"Error loading vector store: {e}")
            print("Please rebuild the vector store.")
            return

    # Load questions
    print("\nLoading questions...")
    questions = load_questions("10Q.txt")
    print(f"Loaded {len(questions)} questions")

    # Answer questions
    print("\nAnswering questions using RAG system...")
    print("(This may take a few minutes depending on your system)\n")
    results = qa_system.answer_multiple_questions(questions, vector_store)

    # Display results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80 + "\n")

    for i, (question, result_data) in enumerate(results.items(), 1):
        answer = result_data['answer']
        chunks = result_data['chunks']
        print(f"\nQuestion {i}: {question}")
        print(f"\nAnswer: {answer}")
        print(f"\n(Used {len(chunks)} chunks from transcripts)")
        print("\n" + "-"*80)

    # Prepare metadata
    metadata = {
        "transcripts": [meta for _, meta in transcript_files],
        "total_chunks": total_chunks,
        "num_questions": len(questions)
    }

    # Save results in multiple formats
    print("\n\nSaving results in multiple formats...")
    file_paths = output_formatter.save_all_formats(results, metadata)

    print(f"\n{'='*80}")
    print("OUTPUT FILES CREATED")
    print(f"{'='*80}")
    print(f"Output Directory: {output_formatter.output_dir}")
    print(f"\nGenerated files:")
    for format_type, filepath in file_paths.items():
        print(f"  • {format_type.upper()}: {os.path.basename(filepath)}")
    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()
