"""Main RAG pipeline for analyzing earnings call transcripts."""

import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import json
import argparse
import config
import os
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.qa_system import QASystem
from src.output_formatter import OutputFormatter


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
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Earnings Transcript RAG System - Batch Question Answering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available transcripts
  python main.py --list-available

  # Analyze CVS Q3 and Q4 2024
  python main.py --company CVS --quarters "Q3 2024" "Q4 2024"

  # Rebuild vector store
  python main.py --rebuild
        """
    )
    parser.add_argument('--company', type=str, required=False,
                       help='Company to analyze (REQUIRED for batch analysis)')
    parser.add_argument('--quarters', type=str, nargs=2, metavar=('Q1', 'Q2'),
                       help='Exactly two quarters to compare (REQUIRED for batch analysis)')
    parser.add_argument('--list-available', action='store_true',
                       help='List available industries, companies, and quarters')
    parser.add_argument('--rebuild', action='store_true',
                       help='Rebuild vector store from transcripts')
    args = parser.parse_args()

    print("=== Earnings Transcript RAG System ===\n")

    # Discover all transcript files from folder structure
    doc_processor = DocumentProcessor()
    transcript_files = doc_processor.discover_transcripts()  # Uses config.TRANSCRIPTS_DIR

    # Handle list-available command
    if args.list_available:
        if transcript_files:
            metadata = doc_processor.get_available_metadata(transcript_files)
            print("Available transcripts:\n")
            print(f"Industries: {', '.join(metadata['industries'])}")
            print(f"Companies:  {', '.join(metadata['companies'])}")
            print(f"Quarters:   {', '.join(metadata['quarters'])}")
            print(f"Years:      {', '.join(metadata['years'])}")
            print(f"\nTotal: {len(transcript_files)} transcript files found")
        else:
            print("No transcripts found in transcripts/ directory.")
            print("Expected structure: transcripts/industry/company/quarter_year.txt")
        return

    # For batch analysis, require company and exactly 2 quarters
    if not args.rebuild:
        if not args.company:
            print("Error: --company is required for batch analysis")
            print("Use --list-available to see available companies")
            print("Or use --rebuild to rebuild the vector store")
            return

        if not args.quarters or len(args.quarters) != 2:
            print("Error: Exactly 2 quarters are required for batch analysis")
            print("Example: --quarters \"Q3 2024\" \"Q4 2024\"")
            print("Use --list-available to see available quarters")
            return

    # Initialize vector store
    vector_store = VectorStore()

    # Check if we should create a new vector store or load existing
    if args.rebuild:
        rebuild_store = True
    else:
        rebuild_store = input("Rebuild vector store from transcripts? (y/n): ").lower() == 'y'

    # Initialize components
    print("\nInitializing components...")
    qa_system = QASystem()
    output_formatter = OutputFormatter()

    # Display filter settings
    if args.company and args.quarters:
        print("\nAnalysis scope:")
        print(f"  Company:  {args.company}")
        print(f"  Quarters: {', '.join(args.quarters)}")
        print()

    total_chunks = 0
    if rebuild_store:
        print("\nProcessing transcripts...")

        if not transcript_files:
            print("\nWARNING: No transcript files found!")
            print("Expected structure: transcripts/industry/company/quarter_year.txt")
            print("Example: transcripts/Healthcare/CVS/Q3_2024.txt")
            return

        # Check if files exist
        existing_files = [(path, meta) for path, meta in transcript_files if os.path.exists(path)]

        if not existing_files:
            print("\nWARNING: Found transcript paths but files don't exist!")
            print("Please check your file paths.")
            return

        print(f"Found {len(existing_files)} transcript files:")
        for path, meta in existing_files:
            print(f"  - {meta['industry']}/{meta['company']}/{meta['quarter']}")

        # Process transcripts
        chunks = doc_processor.process_transcripts(existing_files)
        total_chunks = len(chunks)
        print(f"\nCreated {total_chunks} chunks from {len(existing_files)} transcripts")

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
    results = qa_system.answer_multiple_questions(
        questions,
        vector_store,
        company=args.company,
        quarters=args.quarters
    )

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
        "num_questions": len(questions),
        "filters": {
            "company": args.company,
            "quarters": args.quarters
        }
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
