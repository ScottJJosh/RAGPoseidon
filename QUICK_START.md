# Quick Start Guide

## Two Ways to Use This System

### 🤖 Interactive Chat (Recommended for Exploration)

**Use this when you want to:**
- Ask follow-up questions
- Explore topics interactively
- Get credit analyst perspective
- Have a conversation about the transcripts

**Start chatting:**
```bash
python chat.py
```

**Example questions:**
- "What are the main credit concerns?"
- "How is their free cash flow?"
- "What did management say about debt levels?"
- "Are there liquidity issues?"
- "What's the guidance for next quarter?"

---

### 📊 Batch Analysis (Best for Consistent Reports)

**Use this when you want to:**
- Answer the same 10 questions every time
- Generate reports in multiple formats
- Compare results across different quarters/companies
- Get prompts to use in Claude or other LLMs

**Run analysis:**
```bash
python main.py
```

**Output files** (in `outputs/run_YYYYMMDD_HHMMSS/`):
- `results_answers_only.pdf` - Clean Q&A report
- `results_with_chunks.pdf` - Report with source evidence
- `prompts_for_llm.txt` - Copy/paste into Claude
- `results.json` - Raw data

---

## Current Configuration

- **Model**: qwen2.5:14b (strong reasoning)
- **Chunks per question**: 20 (comprehensive context)
- **Total chunks in store**: 178 (from CVS Q3 & Q4 2024)
- **Context window usage**: ~39% (plenty of room to scale)

---

## Quick Tips

### For Interactive Chat:
- Conversation history is maintained - ask follow-ups naturally
- Type `reset` to start fresh conversation
- Type `history` to see what you've asked
- The chatbot thinks like a credit analyst - it focuses on financial health, liquidity, risk factors

### For Batch Analysis:
- First run: answer 'y' to build vector store (~30 seconds)
- Later runs: answer 'n' to reuse existing store (faster)
- Use `results_answers_only.pdf` for sharing with stakeholders
- Use `results_with_chunks.pdf` for verification and audit trail
- Use `prompts_for_llm.txt` to compare with Claude/GPT-4

---

## Adding More Transcripts

1. Add files to `transcripts/` directory
2. Update `main.py` line 40-41 with new file paths
3. Run `python main.py` and answer 'y' to rebuild vector store
4. Both modes will now include the new transcripts!
