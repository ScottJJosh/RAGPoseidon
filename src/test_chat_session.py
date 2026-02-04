#!/usr/bin/env python3
"""Test chat session with follow-up questions."""

from vector_store import VectorStore
from interactive_chat import CreditAnalystChatbot
from datetime import datetime

def format_response(question, response):
    """Format a Q&A response for output."""
    output = []
    output.append("\n" + "="*80)
    output.append(f"Q: {question}")
    output.append("="*80)
    output.append(f"\nA: {response['answer']}\n")
    output.append(f"[Used {response['chunks_count']} chunks]")
    output.append("\n" + "-"*80)
    return "\n".join(output)

def main():
    print("Loading vector store and initializing chatbot...")

    # Load vector store
    vector_store = VectorStore()
    vector_store.load_vectorstore()

    # Initialize chatbot
    chatbot = CreditAnalystChatbot(vector_store)

    print("✓ Chatbot initialized\n")

    # Define test questions with follow-ups
    questions = [
        "What was CVS's revenue in Q4 2024?",
        "How does that compare to Q3 2024?",
        "What did management say about guidance for next quarter?",
        "Were there any mentions of restructuring or layoffs?",
        "What was said about free cash flow?",
        "How is CVS planning to improve margins?",
    ]

    # Collect all responses
    conversation_log = []
    conversation_log.append("="*80)
    conversation_log.append("CHATBOT TEST SESSION")
    conversation_log.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    conversation_log.append(f"Model: {chatbot.llm_model}")
    conversation_log.append(f"Vector Store: {vector_store.get_collection_count()} chunks")
    conversation_log.append("="*80)

    # Ask questions
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] Asking: {question}")
        response = chatbot.chat(question)
        conversation_log.append(format_response(question, response))
        print("✓ Answer received")

    # Add conversation summary
    conversation_log.append("\n\n" + "="*80)
    conversation_log.append("CONVERSATION SUMMARY")
    conversation_log.append("="*80)
    conversation_log.append(chatbot.get_conversation_summary())

    # Save to file
    output_file = "chatbot_test_session.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(conversation_log))

    print(f"\n✓ Conversation saved to: {output_file}")
    print(f"✓ Total exchanges: {len(questions)}")

if __name__ == "__main__":
    main()
