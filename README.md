# Market Research Agent

Autonomous multi-agent market research system powered by LangGraph, Gemini, and Tavily.

## Quick Start (Local, no Docker)

```bash
# 1. Clone and install
cd market-research-agent
pip install -r requirements.txt

# 2. Configure environment
copy .env.example .env
# Edit .env and fill in TAVILY_API_KEY and GEMINI_API_KEY

# 3. Make sure Ollama is running with qwen2.5:7b
ollama pull qwen2.5:7b
ollama serve

# 4. Start the API (terminal 1)
uvicorn api.main:app --reload --port 8000

# 5. Start the UI (terminal 2)
streamlit run ui/app.py
```

Open http://localhost:8501

## With Docker

```bash
copy .env.example .env   # fill in API keys
docker-compose up --build
```

- UI:  http://localhost:8501
- API: http://localhost:8000/docs
- n8n: http://localhost:5678  (admin / admin123)

## n8n Workflows

Import the JSON files from `n8n/` into n8n:
- `monitor_workflow.json`  — Scheduled re-research + alerts
- `trigger_workflow.json`  — Telegram trigger
- `delivery_workflow.json` — Auto email report on completion
- `batch_workflow.json`    — Overnight batch queue

## Architecture

```
Streamlit UI ──► FastAPI ──► LangGraph Workflow
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
                 Planner     Search       Scraper
                 (Ollama)   (Tavily)   (httpx+BS4)
                    │
                 Verifier
                 (Ollama)
                    │
                 Summarizer
                 (Gemini 2.0 Flash)
                    │
                 Report Agent
                 (ReportLab PDF)
                    │
              SQLite + ChromaDB
                    │
                  n8n Layer
          (Monitor / Notify / Batch)
```

## Stack

| Layer | Tech |
|---|---|
| Agents | LangGraph |
| Local LLM | Ollama qwen2.5:7b |
| Synthesis LLM | Gemini 2.0 Flash |
| Search | Tavily API |
| Scraping | httpx + BeautifulSoup |
| Vector Store | ChromaDB |
| Database | SQLite |
| Charts | Plotly |
| PDF | ReportLab |
| Automation | n8n |
| Frontend | Streamlit |
| Backend | FastAPI |
