# Quick Start Guide

Get started with the Earnings Transcript RAG System in 5 minutes.

## Prerequisites

1. **Python 3.8+** installed
2. **Ollama** running locally ([Install Ollama](https://ollama.ai))

## Setup

### 1. Install Dependencies

```bash
# Create and activate virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Install Ollama Models

```bash
ollama pull nomic-embed-text  # For embeddings
ollama pull qwen2.5:14b        # For analysis
```

### 3. Verify Folder Structure

Your transcripts should be organized as:
```
transcripts/
└── Healthcare/          # Industry
    ├── CVS/             # Company
    │   ├── Q3_2024.txt  # Quarter files
    │   └── Q4_2024.txt
    └── DVA/
        ├── Q3_2024.txt
        └── Q4_2024.txt
```

**If you have old flat structure:**
```bash
python3 src/migrate_transcripts.py
```

## Usage

### Option 1: Batch Analysis (Compare 2 Quarters)

**Purpose:** Answer 10 predefined questions for ONE company across TWO quarters

```bash
# Activate virtual environment
source venv/bin/activate

# List what's available
python3 main.py --list-available

# Compare CVS Q3 vs Q4 2024
python3 main.py --company CVS --quarters "Q3 2024" "Q4 2024"
```

**First run:** You'll be prompted to build the vector store (answer 'y')

**Output:** Results saved in `outputs/run_YYYYMMDD_HHMMSS/`
- `results_answers_only.pdf` - Clean report
- `results_with_chunks.pdf` - Full report with sources
- `results.json` - Complete data

### Option 2: Interactive Chat (Flexible Filtering)

**Purpose:** Ask custom questions with flexible filtering

```bash
# Activate virtual environment
source venv/bin/activate

# Chat with all transcripts
python3 chat.py

# Chat about Healthcare industry only
python3 chat.py --industry Healthcare

# Chat about CVS and DVA
python3 chat.py --companies CVS DVA

# Chat about Q4 2024 across all companies
python3 chat.py --quarters "Q4 2024"

# Combine filters
python3 chat.py --companies CVS --quarters "Q3 2024" "Q4 2024"
```

**Chat Commands:**
- Type your question and press Enter
- `history` - View conversation history
- `reset` - Clear conversation
- `exit` - Quit

**Citation Format:**
- Answers include specific paragraph references: `[CVS Q3 2024 ¶5]`
- The ¶ symbol indicates paragraph/chunk number (¶1, ¶2, etc.)
- This lets you verify which exact source each fact comes from

## Common Tasks

### Adding New Transcripts

1. **Create folders:**
   ```bash
   mkdir -p transcripts/YourIndustry/YourCompany
   ```

2. **Add file with correct naming:**
   ```
   transcripts/YourIndustry/YourCompany/Q1_2024.txt
   ```

3. **Rebuild vector store:**
   ```bash
   python3 main.py --rebuild
   ```

### Comparing Two Companies

```bash
# Chat mode allows up to 2 companies
python3 chat.py --companies CVS DVA --quarters "Q4 2024"
```

Then ask: "Which company had better cash flow?"

### Analyzing Industry Trends

```bash
# Filter by industry
python3 chat.py --industry Healthcare
```

Then ask: "What are common themes across all companies?"

### Batch Analysis for Different Company

```bash
# Analyze DVA instead of CVS
python3 main.py --company DVA --quarters "Q3 2024" "Q4 2024"
```

## Troubleshooting

### "ModuleNotFoundError"
**Solution:** Activate virtual environment
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### "Ollama connection error"
**Solution:** Start Ollama
```bash
ollama serve
```

### "No transcript files found"
**Solution:** Check folder structure
```bash
python3 main.py --list-available
```
Expected: `transcripts/industry/company/Q#_YEAR.txt`

### "Error: --company is required"
**Solution:** Batch analysis requires company + 2 quarters
```bash
python3 main.py --company CVS --quarters "Q3 2024" "Q4 2024"
```

Or use chat mode for flexibility:
```bash
python3 chat.py  # No filters required
```

### "Maximum 2 companies can be specified"
**Solution:** Chat mode allows max 2 companies
```bash
python3 chat.py --companies CVS DVA  # OK
python3 chat.py --companies CVS DVA UNH  # ERROR
```

## Project Structure

```
TranscriptQuestions/
├── README.md              # Full documentation
├── QUICKSTART.md          # This file
├── requirements.txt       # Python dependencies
├── config.py              # Configuration settings
├── 10Q.txt                # 10 predefined questions
│
├── src/                   # Source modules
│   ├── __init__.py
│   ├── document_processor.py  # Document loading and chunking
│   ├── vector_store.py        # Vector embeddings and retrieval
│   ├── qa_system.py           # Question answering logic
│   ├── interactive_chat.py    # Chat interface with filtering
│   ├── output_formatter.py    # Multi-format output generation
│   ├── migrate_transcripts.py # Migration utility for old files
│   └── test_chat_session.py   # Test/example chat session script
│
├── main.py                # Batch analysis script
├── chat.py                # Interactive chat script
│
├── transcripts/           # Your transcript data
│   └── Healthcare/        # Industry folder
│       ├── CVS/           # Company folder
│       │   ├── Q3_2024.txt
│       │   └── Q4_2024.txt
│       └── DVA/
│           ├── Q3_2024.txt
│           └── Q4_2024.txt
│
├── outputs/               # Generated analysis reports
│   └── run_YYYYMMDD_HHMMSS/
│       ├── results.json
│       ├── results_with_chunks.pdf
│       ├── results_answers_only.pdf
│       ├── prompts_for_llm.txt
│       └── run_metadata.json
│
├── chroma_db/             # Vector store database
└── venv/                  # Virtual environment
```

## Next Steps

1. **Explore Examples:**
   - See `README.md` for detailed documentation
   - Check `docs/` folder for guides

2. **Customize:**
   - Edit `config.py` for chunk size, model selection
   - Edit `10Q.txt` for different questions

3. **Scale:**
   - Add more companies and industries
   - Compare across quarters and companies

## Quick Reference

### Batch Analysis Commands
```bash
python3 main.py --list-available
python3 main.py --company CVS --quarters "Q3 2024" "Q4 2024"
python3 main.py --rebuild
```

### Chat Commands
```bash
python3 chat.py
python3 chat.py --industry Healthcare
python3 chat.py --companies CVS DVA
python3 chat.py --quarters "Q4 2024"
python3 chat.py --companies CVS --quarters "Q3 2024" "Q4 2024"
```

### Requirements
- **Batch:** 1 company + exactly 2 quarters
- **Chat:** Optional filters (industry, 1-2 companies, any quarters)

## Getting Help

- **Full Documentation:** See `README.md`
- **Filtering Guide:** See `docs/NEW_FILTERING_GUIDE.md`
- **Issues:** Check troubleshooting section above
