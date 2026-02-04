#!/usr/bin/env python3
"""Interactive chat interface for earnings transcript Q&A."""

import sys
from vector_store import VectorStore
from interactive_chat import CreditAnalystChatbot


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
        for i, chunk in enumerate(response['chunks'][:3], 1):  # Show first 3
            print(f"\n{i}. [{chunk['company']} {chunk['quarter']}]")
            print(f"   {chunk['content'][:200]}...")

    print("-" * 80 + "\n")


def main():
    """Run the interactive chat interface."""
    print("Loading vector store and initializing chatbot...")

    try:
        # Load vector store
        vector_store = VectorStore()
        vector_store.load_vectorstore()
        total_chunks = vector_store.get_collection_count()

        # Initialize chatbot
        chatbot = CreditAnalystChatbot(vector_store)

        print(f"✓ Vector store loaded ({total_chunks} chunks)")
        print(f"✓ Using model: {chatbot.llm_model}")
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
