"""Interactive RAG chatbot for earnings transcript Q&A with concise, cited answers."""

from typing import List, Dict
from langchain_core.documents import Document
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import config


class CreditAnalystChatbot:
    """Interactive chatbot that answers questions about transcripts with concise, cited responses."""

    def __init__(self, vector_store, llm_model: str = None):
        """Initialize the chatbot.

        Args:
            vector_store: VectorStore instance for retrieving relevant chunks
            llm_model: Name of the Ollama LLM model to use
        """
        self.vector_store = vector_store
        self.llm_model = llm_model or config.LLM_MODEL
        self.llm = Ollama(model=self.llm_model)
        self.conversation_history = []

        # Analyst system prompt
        self.system_prompt = """You are a financial analyst. Answer questions directly using only the provided transcript information.

Rules:
- Give concise, factual answers
- Always cite the source: [Company Quarter] at the start of each fact
- Include specific numbers, metrics, and quotes when available
- If the information isn't in the transcripts, say "Not found in provided transcripts"
- No unnecessary analysis or commentary unless explicitly asked"""

        # Create prompt template for chat
        self.prompt_template = PromptTemplate(
            input_variables=["system_prompt", "conversation_history", "context", "question"],
            template="""{system_prompt}

Previous conversation:
{conversation_history}

Available transcript information:
{context}

Question: {question}

Answer concisely with citations in [Company Quarter] format:"""
        )

    def _format_conversation_history(self) -> str:
        """Format conversation history for the prompt.

        Returns:
            Formatted conversation history string
        """
        if not self.conversation_history:
            return "No previous conversation."

        history_text = []
        for entry in self.conversation_history[-5:]:  # Keep last 5 exchanges
            history_text.append(f"User: {entry['question']}")
            history_text.append(f"Analyst: {entry['answer'][:200]}...")  # Truncate for context

        return "\n".join(history_text)

    def _retrieve_relevant_context(self, query: str, k: int = None) -> List[Document]:
        """Retrieve relevant chunks for the query.

        Args:
            query: User's question
            k: Number of chunks to retrieve

        Returns:
            List of relevant document chunks
        """
        k = k or config.TOP_K_CHUNKS
        return self.vector_store.similarity_search(query, k=k)

    def _format_context(self, chunks: List[Document]) -> str:
        """Format retrieved chunks into context string.

        Args:
            chunks: List of retrieved document chunks

        Returns:
            Formatted context string
        """
        context_parts = []
        for chunk in chunks:
            source_info = (f"[{chunk.metadata.get('company', 'Unknown')} "
                          f"{chunk.metadata.get('quarter', 'Unknown')}]")
            context_parts.append(f"{source_info}\n{chunk.page_content}")

        return "\n\n---\n\n".join(context_parts)

    def chat(self, user_question: str) -> Dict[str, any]:
        """Process a user question and return answer with context.

        Args:
            user_question: The user's question

        Returns:
            Dictionary with answer, chunks, and metadata
        """
        # Retrieve relevant chunks
        relevant_chunks = self._retrieve_relevant_context(user_question)

        # Format context
        context = self._format_context(relevant_chunks)

        # Format conversation history
        history = self._format_conversation_history()

        # Generate prompt
        prompt = self.prompt_template.format(
            system_prompt=self.system_prompt,
            conversation_history=history,
            context=context,
            question=user_question
        )

        # Get answer from LLM
        answer = self.llm.invoke(prompt)

        # Store in conversation history
        self.conversation_history.append({
            "question": user_question,
            "answer": answer,
            "chunks_used": len(relevant_chunks)
        })

        # Prepare chunk metadata for display
        chunk_info = [
            {
                "content": chunk.page_content,
                "source": chunk.metadata.get('source', 'Unknown'),
                "quarter": chunk.metadata.get('quarter', 'Unknown'),
                "company": chunk.metadata.get('company', 'Unknown')
            }
            for chunk in relevant_chunks
        ]

        return {
            "answer": answer,
            "chunks": chunk_info,
            "chunks_count": len(relevant_chunks),
            "conversation_length": len(self.conversation_history)
        }

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("Conversation history cleared.")

    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation.

        Returns:
            Formatted summary of conversation
        """
        if not self.conversation_history:
            return "No conversation history."

        summary = f"Conversation History ({len(self.conversation_history)} exchanges):\n"
        summary += "=" * 80 + "\n\n"

        for i, entry in enumerate(self.conversation_history, 1):
            summary += f"{i}. Q: {entry['question']}\n"
            summary += f"   A: {entry['answer'][:150]}...\n"
            summary += f"   (Used {entry['chunks_used']} chunks)\n\n"

        return summary
