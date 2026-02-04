#!/usr/bin/env python3
"""Interactive chat interface for earnings transcript Q&A."""

import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import argparse
from src.vector_store import VectorStore
from src.interactive_chat import CreditAnalystChatbot


def print_header():
    """Print the chat interface header."""
    print("\n" + "=" * 80)
    print("EARNINGS TRANSCRIPT Q&A")
    print("=" * 80)
    print("\nAsk questions about the earnings transcripts.")
    print("Responses will be concise with clear citations.")
    print("\nCommands:")
    print("  - Type your question and press Enter")
    print("  - Type 'reset' to clear conversation history")
    print("  - Type 'history' to see conversation summary")
    print("  - Type 'exit' or 'quit' to end the session")
    print("=" * 80 + "\n")


def print_answer(response: dict, show_chunks: bool = False):
    """Print the chatbot's answer.

    Args:
        response: Response dictionary from chatbot
        show_chunks: Whether to show chunk information
    """
    print("\n" + "-" * 80)
    print("ANSWER:")
    print("-" * 80)
    print(response['answer'])
    print()
    print(f"[Used {response['chunks_count']} relevant chunks | "
          f"Conversation: {response['conversation_length']} exchanges]")

    if show_chunks:
        print("\n" + "-" * 80)
        print("SOURCE CHUNKS:")
        print("-" * 80)
        for chunk in response['chunks'][:3]:  # Show first 3
            print(f"\n¶{chunk['paragraph']}. [{chunk['company']} {chunk['quarter']}]")
            print(f"   {chunk['content'][:200]}...")

    print("-" * 80 + "\n")


def main():
    """Run the interactive chat interface."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Interactive Earnings Transcript Chat',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Chat with all transcripts
  python chat.py

  # Filter by industry
  python chat.py --industry Healthcare

  # Filter by one company
  python chat.py --companies CVS

  # Filter by two companies
  python chat.py --companies CVS DVA

  # Filter by industry and quarters
  python chat.py --industry Healthcare --quarters "Q3 2024" "Q4 2024"

  # List what's available
  python chat.py --list-available
        """
    )
    parser.add_argument('--industry', type=str,
                       help='Filter by industry')
    parser.add_argument('--companies', type=str, nargs='+', metavar='COMPANY',
                       help='Filter by one or two companies (e.g., CVS or CVS DVA)')
    parser.add_argument('--quarters', type=str, nargs='+', metavar='QUARTER',
                       help='Filter by quarters (e.g., "Q3 2024" "Q4 2024")')
    parser.add_argument('--list-available', action='store_true',
                       help='List available industries, companies, and quarters')
    args = parser.parse_args()

    # Validate companies argument
    if args.companies and len(args.companies) > 2:
        print("Error: Maximum 2 companies can be specified")
        return

    print("Loading vector store and initializing chatbot...")

    try:
        # Load vector store
        vector_store = VectorStore()
        vector_store.load_vectorstore()
        total_chunks = vector_store.get_collection_count()

        # Handle list-available command
        if args.list_available:
            metadata = vector_store.get_available_metadata()
            print("\nAvailable in vector store:")
            if 'industries' in metadata and metadata['industries']:
                print(f"  Industries: {', '.join(metadata['industries'])}")
            print(f"  Companies:  {', '.join(metadata['companies'])}")
            print(f"  Quarters:   {', '.join(metadata['quarters'])}")
            return

        # Initialize chatbot with filters
        chatbot = CreditAnalystChatbot(
            vector_store,
            industry=args.industry,
            companies=args.companies,
            quarters=args.quarters
        )

        print(f"✓ Vector store loaded ({total_chunks} chunks)")
        print(f"✓ Using model: {chatbot.llm_model}")
        if args.industry:
            print(f"✓ Filtering by industry: {args.industry}")
        if args.companies:
            print(f"✓ Filtering by companies: {', '.join(args.companies)}")
        if args.quarters:
            print(f"✓ Filtering by quarters: {', '.join(args.quarters)}")
        print("✓ Chatbot ready")

        # Print header
        print_header()

        # Main chat loop
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                # Handle commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!")
                    break

                elif user_input.lower() == 'reset':
                    chatbot.reset_conversation()
                    continue

                elif user_input.lower() == 'history':
                    print("\n" + chatbot.get_conversation_summary())
                    continue

                elif user_input.lower() == 'help':
                    print_header()
                    continue

                elif not user_input:
                    continue

                # Process the question
                print("\n[Analyzing transcripts...]")
                response = chatbot.chat(user_input)

                # Print the answer
                print_answer(response, show_chunks=False)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit or continue chatting.")
                continue
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again or type 'exit' to quit.\n")
                continue

    except Exception as e:
        print(f"\nError initializing: {e}")
        print("Make sure you have run main.py at least once to create the vector store.")
        sys.exit(1)


if __name__ == "__main__":
    main()
