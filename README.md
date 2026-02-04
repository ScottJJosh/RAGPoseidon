# Earnings Transcript RAG System

A Retrieval-Augmented Generation (RAG) application for analyzing earnings call transcripts with two modes:
1. **Batch Analysis**: Answer 10 predefined questions across transcripts
2. **Interactive Chat**: Credit analyst chatbot for open-ended Q&A with conversation context

## Features

### Batch Analysis Mode
- Automated answering of 10 earnings call questions
- Multiple output formats (JSON, PDF with/without chunks, prompts for external LLMs)
- Configurable chunk retrieval (default: 20 chunks per question)
- Timestamped output folders for tracking runs

### Interactive Chat Mode
- **Credit analyst persona** with specialized system prompt
- Conversation history maintained across questions
- RAG-based retrieval for each query (20 relevant chunks)
- Real-time analysis with qwen2.5:14b model
- Commands: `reset`, `history`, `help`, `exit`

### Core Features
- Document chunking with overlap for context preservation
- Vector embeddings using Ollama (nomic-embed-text)
- Semantic search for relevant transcript sections
- Support for multiple quarters and companies
- Persistent ChromaDB vector store

## Prerequisites

1. **Python 3.8+**
2. **Ollama installed and running** ([Install Ollama](https://ollama.ai))
3. Required Ollama models:
   ```bash
   ollama pull nomic-embed-text  # For embeddings
   ollama pull qwen2.5:14b        # For analysis (stronger reasoning than llama3.2)
   ```

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Verify Ollama is running:
   ```bash
   ollama list
   ```

## Project Structure

```
TranscriptQuestions/
├── config.py                  # Configuration settings
├── document_processor.py      # Document loading and chunking
├── vector_store.py           # Vector embeddings and retrieval
├── qa_system.py              # Batch Q&A logic
├── interactive_chat.py       # Interactive chatbot with credit analyst persona
├── output_formatter.py       # Multi-format output generation
├── main.py                   # Batch analysis pipeline
├── chat.py                   # Interactive chat interface
├── 10Q.txt                   # 10 predefined questions
├── transcripts/              # Directory for transcript files
│   ├── cvs_Q3.txt
│   └── cvs_Q4.txt
├── chroma_db/                # Vector store (created automatically)
└── outputs/                  # Timestamped output folders
    └── run_YYYYMMDD_HHMMSS/
        ├── results.json
        ├── results_with_chunks.pdf
        ├── results_answers_only.pdf
        ├── prompts_for_llm.txt
        └── run_metadata.json
```

## Usage

### Mode 1: Batch Analysis (Predefined Questions)

#### 1. Prepare Your Transcripts

Create a `transcripts/` directory and add your earnings call transcript files:

```bash
mkdir transcripts
# Add your transcript files to this directory
```

Update the `transcript_files` list in `main.py` with your actual files:

```python
transcript_files = [
    ("transcripts/q1_2024.txt", {"quarter": "Q1 2024", "company": "Your Company"}),
    ("transcripts/q2_2024.txt", {"quarter": "Q2 2024", "company": "Your Company"}),
]
```

#### 2. Run Batch Analysis

```bash
python main.py
```

On first run, answer 'y' to build the vector store. On subsequent runs, you can answer 'n' to reuse the existing vector store.

#### 3. View Results

Results are saved in `outputs/run_YYYYMMDD_HHMMSS/`:
- `results_answers_only.pdf` - Clean report (8KB)
- `results_with_chunks.pdf` - Full report with source excerpts (87KB)
- `results.json` - Complete data with metadata
- `prompts_for_llm.txt` - Ready to paste into Claude or other LLMs

### Mode 2: Interactive Chat (Credit Analyst)

#### 1. Start the Chatbot

```bash
python chat.py
```

#### 2. Ask Questions

The chatbot analyzes transcripts from a **credit analyst perspective**, focusing on:
- Financial health and liquidity
- Cash flow generation and debt levels
- Management quality and credibility
- Risk factors and red flags
- Credit metrics and coverage ratios
- Forward-looking credit implications

#### 3. Example Session

```
You: What is CVS's liquidity situation?
CREDIT ANALYST: Based on Q3 and Q4 2024 transcripts, CVS's liquidity
appears under pressure due to negative MA margins, elevated premium
deficiency reserves, and retail headwinds. Recent May 2024 financing
suggests efforts to bolster short-term liquidity...
[Used 20 relevant chunks | Conversation: 1 exchanges]

You: Are there any positive credit factors?
CREDIT ANALYST: Yes, several positives emerged in Q3-Q4 2024:
1. Star Ratings Performance: 88% of members in 4-star or higher plans
2. Rate Increases: Mid-4% rate increase achieved in Medicaid
3. Large Account Wins: North Carolina state contract...
[Used 20 relevant chunks | Conversation: 2 exchanges]

You: history
Conversation History (2 exchanges):
1. Q: What is CVS's liquidity situation?
   A: Based on Q3 and Q4 2024 transcripts, CVS's liquidity...
   (Used 20 chunks)

You: exit
Thank you for using the Credit Analyst Chatbot. Goodbye!
```

#### 4. Available Commands

- **Type your question** - Get credit-focused analysis
- `reset` - Clear conversation history
- `history` - View conversation summary
- `help` - Show commands
- `exit` or `quit` - End session

## Configuration

Edit `config.py` to customize:

- **Embedding model**: Change `EMBEDDING_MODEL` (default: `nomic-embed-text`)
- **LLM model**: Change `LLM_MODEL` (default: `llama3.2`)
- **Chunk size**: Adjust `CHUNK_SIZE` (default: 1000 characters)
- **Chunk overlap**: Adjust `CHUNK_OVERLAP` (default: 200 characters)
- **Retrieval count**: Change `TOP_K_CHUNKS` (default: 5 chunks per question)

## Questions Answered

The system answers these 10 questions about each transcript:

1. What phrases were consistent with the previous quarter commentary?
2. What phrases were different from the previous quarter commentary?
3. Was guidance revised? Why?
4. What did the company say was going well?
5. What did the company say needed improvement?
6. What are announcements or goals stated for the next quarter?
7. How does the company expect to improve Sales and Margins?
8. How does the company expect to improve Free Cash Flow and what is Capex expected to be?
9. What's the company's assessment of the consumer and economy?
10. Was there mentions around restructuring or distress?

## Scaling to Multiple Companies

To compare multiple companies:

1. Add transcripts with company metadata:
   ```python
   transcript_files = [
       ("transcripts/company_a_q1.txt", {"quarter": "Q1 2024", "company": "Company A"}),
       ("transcripts/company_b_q1.txt", {"quarter": "Q1 2024", "company": "Company B"}),
   ]
   ```

2. The system will retrieve relevant chunks from all transcripts when answering questions

3. Modify questions to compare companies explicitly if needed

## Troubleshooting

**Ollama connection errors:**
- Ensure Ollama is running: `ollama serve`
- Check if models are installed: `ollama list`

**Memory issues:**
- Reduce `CHUNK_SIZE` in config.py
- Use a smaller LLM model
- Process fewer transcripts at once

**Poor answer quality:**
- Increase `TOP_K_CHUNKS` to retrieve more context
- Adjust `CHUNK_OVERLAP` for better context continuity
- Try different Ollama models (e.g., `llama3.1`, `mistral`)

## Future Enhancements

- Web interface for easier interaction
- Comparison mode for side-by-side analysis
- Time-series analysis across multiple quarters
- Export to different formats (PDF, Excel)
- Custom question input
