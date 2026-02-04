"""Question answering system using Ollama LLM."""

from typing import List
from langchain_core.documents import Document
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import config


class QASystem:
    """Handles question answering using retrieved context."""

    def __init__(self, llm_model: str = None):
        """Initialize the QA system.

        Args:
            llm_model: Name of the Ollama LLM model to use
        """
        self.llm_model = llm_model or config.LLM_MODEL
        self.llm = Ollama(model=self.llm_model)

        # Create prompt template for answering questions
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are analyzing earnings call transcripts. Answer the question using only the information in the context below.

Context:
{context}

Question: {question}

Instructions:
- Cite the specific quarter when mentioning information (e.g. "In Q2 2024...")
- Include specific numbers and percentages from the transcripts
- If the context doesn't answer the question, say "This information is not in the provided transcripts"
- Answer in 3-5 clear sentences

Answer:"""
)

    def answer_question(self, question: str, context_chunks: List[Document]) -> tuple:
        """Generate an answer to a question using relevant context.

        Args:
            question: The question to answer
            context_chunks: List of relevant document chunks

        Returns:
            Tuple of (answer, prompt) where prompt is the full prompt sent to LLM
        """
        # Combine context chunks into a single string
        context = "\n\n".join([
            f"[Source: {chunk.metadata.get('source', 'Unknown')}, "
            f"Quarter: {chunk.metadata.get('quarter', 'Unknown')}]\n{chunk.page_content}"
            for chunk in context_chunks
        ])

        # Generate prompt
        prompt = self.prompt_template.format(context=context, question=question)

        # Get answer from LLM
        answer = self.llm.invoke(prompt)

        return answer, prompt

    def answer_multiple_questions(self, questions: List[str], vector_store,
                                  company: str = None, quarters: List[str] = None) -> dict:
        """Answer multiple questions using the vector store for retrieval.

        Args:
            questions: List of questions to answer
            vector_store: VectorStore instance for retrieving relevant chunks
            company: Optional company filter
            quarters: Optional list of quarters to filter by

        Returns:
            Dictionary mapping questions to dict with 'answer', 'chunks', and 'prompt' keys
        """
        results = {}

        for i, question in enumerate(questions, 1):
            print(f"\nProcessing question {i}/{len(questions)}: {question[:50]}...")

            # Build metadata filter
            filter_dict = {}
            if company:
                filter_dict['company'] = company
            if quarters and len(quarters) == 1:
                filter_dict['quarter'] = quarters[0]

            # Retrieve relevant chunks
            relevant_chunks = vector_store.similarity_search(
                question,
                filter_dict=filter_dict if filter_dict else None
            )

            # Post-filter for multiple quarters if needed
            if quarters and len(quarters) > 1:
                relevant_chunks = [doc for doc in relevant_chunks if doc.metadata.get('quarter') in quarters]

            # Generate answer and get the full prompt
            answer, prompt = self.answer_question(question, relevant_chunks)

            # Store answer, chunks used, and the full prompt
            results[question] = {
                "answer": answer,
                "prompt": prompt,
                "chunks": [
                    {
                        "content": chunk.page_content,
                        "source": chunk.metadata.get('source', 'Unknown'),
                        "quarter": chunk.metadata.get('quarter', 'Unknown'),
                        "company": chunk.metadata.get('company', 'Unknown')
                    }
                    for chunk in relevant_chunks
                ]
            }

        return results
