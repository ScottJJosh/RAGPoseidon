# Earnings Transcript RAG System

A Retrieval-Augmented Generation (RAG) application for analyzing earnings call transcripts using local LLMs via Ollama.

## Features

### Two Operating Modes

1. **Batch Analysis** (`main.py`)
   - Answer 10 predefined questions comparing TWO quarters for ONE company
   - Generates comprehensive reports in PDF and JSON formats
   - Requirements: Must specify 1 company + exactly 2 quarters

2. **Interactive Chat** (`chat.py`)
   - Flexible Q&A with conversation history
   - Optional filtering by industry, companies (1-2), and quarters
   - Real-time analysis with credit analyst persona

### Core Capabilities

- 📁 **Hierarchical Organization**: Industry → Company → Quarter structure
- 🔍 **Semantic Search**: Vector-based retrieval of relevant transcript sections
- 🎯 **Flexible Filtering**: Filter by industry, company, and time periods
- 💬 **Conversational Memory**: Chat mode maintains context across questions
- 📊 **Multiple Output Formats**: JSON, PDF with/without chunks, LLM prompts
- 🚀 **Local & Private**: Runs entirely on your machine via Ollama

## Quick Start

**See [QUICKSTART.md](QUICKSTART.md) for a 5-minute getting started guide.**

## Folder Structure

```
TranscriptQuestions/
├── README.md                  # This file
├── QUICKSTART.md              # Quick start guide
├── requirements.txt           # Python dependencies
├── config.py                  # Configuration (paths, models, settings)
│
├── src/                       # Source code modules
│   ├── __init__.py
│   ├── document_processor.py  # Document loading and chunking
│   ├── vector_store.py        # Vector embeddings and retrieval
│   ├── qa_system.py           # Question answering logic
│   ├── interactive_chat.py    # Chat interface with filtering
│   ├── output_formatter.py    # Multi-format output generation
│   ├── migrate_transcripts.py # Migration utility for old files
│   └── test_chat_session.py   # Test/example chat session script
│
├── main.py                    # Batch analysis script
├── chat.py                    # Interactive chat script
├── 10Q.txt                    # 10 predefined questions
│
├── transcripts/               # Your transcript files
│   └── Healthcare/            # Industry folder
│       ├── CVS/               # Company folder
│       │   ├── Q3_2024.txt    # Quarter files
│       │   └── Q4_2024.txt
│       └── DVA/
│           ├── Q3_2024.txt
│           └── Q4_2024.txt
│
├── outputs/                   # Generated analysis reports
│   └── run_YYYYMMDD_HHMMSS/
│       ├── results.json
│       ├── results_with_chunks.pdf
│       ├── results_answers_only.pdf
│       ├── prompts_for_llm.txt
│       └── run_metadata.json
│
├── chroma_db/                 # Vector store database
└── venv/                      # Virtual environment (created by you)
```

### Required Transcript Structure

```
transcripts/
└── {Industry}/
    └── {Company}/
        └── Q{1-4}_YEAR.txt
```

**Example:**
```
transcripts/Healthcare/CVS/Q3_2024.txt
transcripts/Healthcare/DVA/Q4_2024.txt
transcripts/Technology/Apple/Q1_2024.txt
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running ([Install Guide](https://ollama.ai))

### Setup Steps

```bash
# 1. Clone or navigate to project directory
cd TranscriptQuestions

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Ollama models
ollama pull nomic-embed-text  # Embeddings
ollama pull qwen2.5:14b        # LLM for analysis

# 5. Organize your transcripts (see structure above)
# OR run migration if you have old flat structure:
python3 src/migrate_transcripts.py

# 6. Build vector store
python3 main.py --rebuild
```

## Usage

### Batch Analysis Mode

**Purpose:** Answer 10 standard questions comparing two quarters for one company

**Requirements:**
- ✅ Exactly ONE company
- ✅ Exactly TWO quarters

**Commands:**

```bash
# List available data
python3 main.py --list-available

# Analyze CVS Q3 vs Q4 2024
python3 main.py --company CVS --quarters "Q3 2024" "Q4 2024"

# Analyze DVA Q3 vs Q4 2024
python3 main.py --company DVA --quarters "Q3 2024" "Q4 2024"

# Rebuild vector store
python3 main.py --rebuild
```

**Output:** Results saved in `outputs/run_YYYYMMDD_HHMMSS/`

### Interactive Chat Mode

**Purpose:** Flexible Q&A with custom filtering

**Options:**
- No filters (analyze all transcripts)
- Filter by industry
- Filter by 1 or 2 companies
- Filter by any number of quarters
- Combine filters

**Commands:**

```bash
# No filters - all transcripts
python3 chat.py

# Filter by industry
python3 chat.py --industry Healthcare

# Filter by one company
python3 chat.py --companies CVS

# Filter by two companies
python3 chat.py --companies CVS DVA

# Filter by quarters
python3 chat.py --quarters "Q3 2024" "Q4 2024"

# Combine filters
python3 chat.py --industry Healthcare --quarters "Q4 2024"
python3 chat.py --companies CVS DVA --quarters "Q3 2024" "Q4 2024"

# List available data
python3 chat.py --list-available
```

**Chat Session:**
```
You: What is CVS's liquidity situation?

ANALYST: [CVS Q3 2024 ¶5] Cash and equivalents were $8.2B at quarter end.
[CVS Q4 2024 ¶12] The company maintains a $5B revolving credit facility...

[Used 20 relevant chunks | Conversation: 1 exchanges]

You: history     # View conversation
You: reset       # Clear conversation
You: exit        # Quit
```

**Citation Format:**
- Citations include paragraph numbers: `[Company Quarter ¶N]`
- Paragraph numbers (¶1, ¶2, etc.) refer to the retrieved chunks
- This allows you to verify which specific source each fact comes from

## Filtering System

### Batch Analysis Filters

| Filter | Required | Values | Example |
|--------|----------|--------|---------|
| `--company` | ✅ YES | 1 company | `CVS` |
| `--quarters` | ✅ YES | 2 quarters | `"Q3 2024" "Q4 2024"` |

### Chat Mode Filters

| Filter | Required | Values | Example |
|--------|----------|--------|---------|
| `--industry` | Optional | 1 industry | `Healthcare` |
| `--companies` | Optional | 1-2 companies | `CVS` or `CVS DVA` |
| `--quarters` | Optional | Any number | `"Q3 2024"` or `"Q3 2024" "Q4 2024"` |

**All filters are optional in chat mode and can be combined freely.**

## Configuration

Edit `config.py` to customize:

```python
# LLM Models
EMBEDDING_MODEL = "nomic-embed-text"  # Embedding model
LLM_MODEL = "qwen2.5:14b"             # Analysis model

# Chunking
CHUNK_SIZE = 1000        # Characters per chunk
CHUNK_OVERLAP = 200      # Overlap between chunks

# Retrieval
TOP_K_CHUNKS = 20        # Chunks retrieved per question

# Paths (auto-configured with absolute paths)
TRANSCRIPTS_DIR          # transcripts/
OUTPUTS_DIR              # outputs/
CHROMA_DB_DIR            # chroma_db/
```

## The 10 Questions

Batch analysis answers these questions:

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

## Use Cases

### Compare Two Quarters (Batch)
```bash
python3 main.py --company CVS --quarters "Q3 2024" "Q4 2024"
```
Generates comprehensive comparison report

### Industry Analysis (Chat)
```bash
python3 chat.py --industry Healthcare
```
Ask: "What are common themes across Healthcare companies?"

### Company Comparison (Chat)
```bash
python3 chat.py --companies CVS DVA --quarters "Q4 2024"
```
Ask: "Which company had better cash flow performance?"

### Multi-Quarter Trends (Chat)
```bash
python3 chat.py --companies CVS --quarters "Q1 2024" "Q2 2024" "Q3 2024" "Q4 2024"
```
Ask: "What trends do you see across the year?"

## Adding New Data

### Add New Company Transcripts

1. **Create folder structure:**
   ```bash
   mkdir -p transcripts/YourIndustry/YourCompany
   ```

2. **Add transcript files:**
   ```
   transcripts/YourIndustry/YourCompany/Q1_2024.txt
   transcripts/YourIndustry/YourCompany/Q2_2024.txt
   ```

3. **Rebuild vector store:**
   ```bash
   python3 main.py --rebuild
   ```

### Migrate Old Files

If you have existing transcripts in flat structure:

```bash
# With backup (recommended)
python3 src/migrate_transcripts.py

# Without backup
python3 src/migrate_transcripts.py --no-backup
```

The script will:
- Parse old filenames (`cvs_Q3_2024.txt`, etc.)
- Create industry/company folders
- Move files with standardized naming (`Q3_2024.txt`)

## Troubleshooting

### Ollama Connection Errors
```bash
# Start Ollama
ollama serve

# Verify models are installed
ollama list
```

### Module Import Errors
```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### No Transcripts Found
```bash
# Check structure
python3 main.py --list-available

# Verify folder organization:
# transcripts/Industry/Company/Q#_YEAR.txt
```

### Batch Analysis Errors
```bash
# Must provide company + 2 quarters
python3 main.py --company CVS --quarters "Q3 2024" "Q4 2024"

# Use chat mode for flexibility
python3 chat.py --companies CVS
```

## Technical Details

### Architecture

- **Document Processing**: Recursive text splitting with overlap for context preservation
- **Vector Store**: ChromaDB with persistent storage
- **Embeddings**: Ollama nomic-embed-text (768-dim vectors)
- **LLM**: Qwen2.5:14b for analysis (better reasoning than llama)
- **Retrieval**: Semantic similarity search with metadata filtering
- **Paths**: Absolute paths using pathlib for cross-platform compatibility

### Metadata Structure

Each chunk includes:
```python
{
    "industry": "Healthcare",
    "company": "CVS",
    "quarter": "Q3 2024",
    "year": "2024",
    "quarter_code": "Q3",
    "source": "/absolute/path/to/transcripts/Healthcare/CVS/Q3_2024.txt"
}
```

### Filtering Logic

- **Single-value filters**: Passed directly to ChromaDB (fast)
- **Multi-value filters**: Post-filtering after retrieval (e.g., 2 companies or multiple quarters)
- **Industry hierarchy**: Industry → Company → Quarter

## Performance

- **Vector store build**: ~5-10 seconds for 4 transcripts
- **Single question**: ~2-5 seconds with qwen2.5:14b
- **Batch analysis**: ~30-60 seconds for 10 questions
- **Chat response**: ~2-5 seconds per question

## Contributing

This is a personal project, but suggestions welcome:
- Open issues for bugs or feature requests
- Submit PRs with improvements
- Share your use cases and feedback

## License

[Your License Here]

## Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [Ollama](https://ollama.ai)
- Vector storage via [ChromaDB](https://www.trychroma.com/)
- PDFs generated with [ReportLab](https://www.reportlab.com/)
