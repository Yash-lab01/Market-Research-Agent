# Market Research Agent

Autonomous multi-agent market research system. Type a question → 5 AI agents search, verify, and synthesize → structured report + PDF.

---

## Stack

| Layer | Tech |
|---|---|
| Agents | LangGraph |
| Local LLM (Planner, Verifier) | Ollama — qwen2.5:7b |
| Synthesis LLM (Summarizer) | Groq — llama-3.3-70b-versatile |
| Search | Tavily API |
| Scraping | httpx + BeautifulSoup |
| Vector Store | ChromaDB |
| Database | SQLite |
| Charts | Plotly |
| PDF | ReportLab |
| Automation | n8n |
| Frontend | Streamlit |
| Backend | FastAPI |

---

## Setup (First Time Only)

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

```powershell
copy .env.example .env
```

Open `.env` and fill in:

```env
TAVILY_API_KEY=tvly-...        # https://app.tavily.com
GROQ_API_KEY=gsk_...           # https://console.groq.com
GEMINI_API_KEY=AIza...         # https://aistudio.google.com/app/apikey (optional fallback)
```

Ollama, SQLite, ChromaDB and Streamlit need no extra config — they run locally out of the box.

### 4. Make sure Ollama is running with the required model

Ollama auto-starts on Windows boot (system tray). Verify it's running:

```powershell
ollama list        # should show qwen2.5:7b
```

If the model isn't there yet:

```powershell
ollama pull qwen2.5:7b
```

---

## Running the App

Every time you want to use the app, open **two terminals** in the project folder.

**Terminal 1 — FastAPI backend:**

```powershell
venv\Scripts\activate
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Streamlit UI:**

```powershell
venv\Scripts\activate
streamlit run ui/app.py
```

Then open **http://localhost:8501** in your browser.

API docs (Swagger): **http://localhost:8000/docs**

---

## Running n8n (Automation — Optional)

Requires Docker Desktop installed and running.

Start n8n in detached mode:
```powershell
docker compose up -d n8n
```
*(This starts n8n in the background. Your workflows and settings are saved automatically in a persistent Docker volume, so they will start up in their last active state next time without manual execution.)*

Open **http://localhost:5678** → login: `admin` / `admin123`

Import workflows from the `n8n/` folder:
- `monitor_workflow.json` — daily re-research + Telegram alert
- `delivery_workflow.json` — auto-email PDF on completion
- `trigger_workflow.json` — start research via Telegram message
- `batch_workflow.json` — overnight batch queue summary email

For Telegram, webhooks, and email credential setup, see the [n8n Setup Guide](#n8n-credentials--webhook-setup) below.

---

## Architecture

```
Streamlit UI  ──►  FastAPI  ──►  LangGraph Workflow
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                      Planner        Search         Scraper
                     (Ollama)       (Tavily)     (httpx+BS4)
                         │
                      Verifier
                      (Ollama)
                         │
                     Summarizer
                  (Groq llama-3.3-70b)
                         │
                    Report Agent
                    (ReportLab PDF)
                         │
                  SQLite + ChromaDB
                         │
                      n8n Layer
              (Monitor / Notify / Batch)
```

---

## Project Structure

```
market-research-agent/
├── agents/
│   ├── planner.py       ← Breaks query into sub-tasks (Ollama)
│   ├── search.py        ← Tavily web search per sub-task
│   ├── scraper.py       ← Fetches and cleans page content
│   ├── verifier.py      ← Cross-checks claims (Ollama)
│   ├── summarizer.py    ← Synthesizes full report JSON (Groq)
│   └── report_agent.py  ← Triggers PDF generation
├── graph/
│   ├── state.py         ← Shared LangGraph state TypedDict
│   └── workflow.py      ← LangGraph StateGraph (agent wiring)
├── api/
│   └── main.py          ← FastAPI endpoints
├── db/
│   ├── sqlite_client.py ← Session, result, monitor job storage
│   └── chroma_client.py ← Vector store for follow-up chat
├── report/
│   └── pdf_builder.py   ← ReportLab PDF with styled layout
├── ui/
│   └── app.py           ← Streamlit UI (4 tabs)
├── n8n/                 ← Importable n8n workflow JSONs
├── .streamlit/
│   └── config.toml      ← Dark theme
├── .env.example         ← Environment variable template
└── requirements.txt
```

---

## n8n Credentials & Webhook Setup

### Telegram
1. Message **@BotFather** on Telegram → `/newbot` → copy the Bot Token
2. Send any message to your bot, then open:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
   Copy the `chat.id` number from the response
3. In n8n → Credentials → Add → **Telegram** → paste the Bot Token (do not use environment variable expressions here)

### Webhook Tunneling (Required for Telegram Trigger)
Telegram requires a public HTTPS URL to send webhook notifications to your local n8n instance.
1. Run a free secure tunnel in a new terminal window:
   ```powershell
   npx localtunnel --port 5678
   ```
2. Copy the generated URL (e.g., `https://xxxx.localtunnel.me`).
3. Add or update it in your `.env` file:
   ```env
   WEBHOOK_URL=https://xxxx.localtunnel.me
   ```
4. Recreate the n8n container to apply the environment configuration:
   ```powershell
   docker compose up -d n8n
   ```
5. In n8n, set the Telegram trigger workflow to **Active**.

### Email (Gmail)
1. Google Account → Security → 2-Step Verification must be ON
2. Search "App passwords" → generate one for Mail
3. In n8n → Credentials → Add → **SMTP**
   - Host: `smtp.gmail.com`
   - Port: `465`
   - Security: `SSL/TLS`
   - User: your Gmail
   - Password: the 16-char App Password

---

## API Keys — Where to Get Them

| Key | Where |
|---|---|
| `TAVILY_API_KEY` | https://app.tavily.com — free tier, 1000 credits |
| `GROQ_API_KEY` | https://console.groq.com — free tier, 14,400 req/day |
| `GEMINI_API_KEY` | https://aistudio.google.com/app/apikey — optional fallback |
