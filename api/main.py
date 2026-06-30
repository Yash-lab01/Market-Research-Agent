import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import research_app
from graph.state import ResearchState
from db import sqlite_client
from db import chroma_client

# ── Startup ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    sqlite_client.init_db()
    yield

app = FastAPI(title="Market Research Agent", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Background task ───────────────────────────────────────────────────────────

def run_research_workflow(session_id: str, query: str):
    """Runs synchronously inside a background thread (FastAPI BackgroundTask)."""
    try:
        sqlite_client.update_session_status(session_id, "🧠 Planner Agent: Breaking down question...")

        initial_state: ResearchState = {
            "query": query,
            "session_id": session_id,
            "sub_tasks": [],
            "search_results": {},
            "scraped_data": {},
            "verified_claims": [],
            "structured_output": {},
            "report_path": None,
            "status": "starting",
            "error": None,
        }

        # Stream through each node — update DB status after each step
        accumulated = dict(initial_state)
        for chunk in research_app.stream(initial_state):
            node_output = list(chunk.values())[0]
            accumulated.update(node_output)
            status = node_output.get("status", "")
            if status:
                sqlite_client.update_session_status(session_id, status)

        # Persist final result
        output = accumulated.get("structured_output", {})
        sqlite_client.save_result(session_id, output)

        if accumulated.get("report_path"):
            sqlite_client.save_report(session_id, accumulated["report_path"])

        # Store in ChromaDB for follow-up chat
        summary = output.get("executive_summary", "")
        if summary:
            chroma_client.store_research(session_id, query, summary)

        sqlite_client.update_session_status(session_id, "completed")

    except Exception as e:
        sqlite_client.update_session_status(session_id, f"error: {str(e)}")


# ── Models ────────────────────────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    query: str

class MonitorRequest(BaseModel):
    query: str
    schedule: str  # "daily" | "weekly"

class BatchRequest(BaseModel):
    queries: list[str]

class ChatRequest(BaseModel):
    session_id: str
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/api/research")
async def start_research(req: ResearchRequest, background_tasks: BackgroundTasks):
    session_id = str(uuid.uuid4())
    sqlite_client.create_session(session_id, req.query)
    background_tasks.add_task(run_research_workflow, session_id, req.query)
    return {"session_id": session_id, "status": "started"}


@app.get("/api/research/{session_id}")
async def get_research(session_id: str):
    session = sqlite_client.get_session(session_id)
    if not session:
        return {"error": "Session not found"}
    return session


@app.get("/api/history")
async def get_history():
    return sqlite_client.get_all_sessions()


@app.get("/api/reports/{session_id}/pdf")
async def download_pdf(session_id: str):
    path = sqlite_client.get_report_path(session_id)
    if not path:
        return {"error": "Report not found"}
    return FileResponse(path, media_type="application/pdf",
                        filename=f"report_{session_id[:8]}.pdf")


@app.post("/api/monitor")
async def create_monitor(req: MonitorRequest):
    job_id = str(uuid.uuid4())
    sqlite_client.create_monitor_job(job_id, req.query, req.schedule)
    return {"job_id": job_id, "message": "Monitor job created"}


@app.get("/api/monitor")
async def list_monitor_jobs():
    return sqlite_client.get_monitor_jobs()


@app.delete("/api/monitor/{job_id}")
async def delete_monitor(job_id: str):
    sqlite_client.delete_monitor_job(job_id)
    return {"message": "Monitor job deleted"}


@app.post("/api/batch")
async def start_batch(req: BatchRequest, background_tasks: BackgroundTasks):
    batch_id = str(uuid.uuid4())
    session_ids = []
    for query in req.queries:
        session_id = str(uuid.uuid4())
        sqlite_client.create_session(session_id, query, batch_id=batch_id)
        background_tasks.add_task(run_research_workflow, session_id, query)
        session_ids.append({"query": query, "session_id": session_id})
    return {"batch_id": batch_id, "jobs": session_ids}


@app.post("/api/chat")
async def follow_up_chat(req: ChatRequest):
    """Follow-up Q&A using Groq + ChromaDB context from past research."""
    import os
    from langchain_groq import ChatGroq

    context_docs = chroma_client.get_similar_research(req.message, n=2)
    session = sqlite_client.get_session(req.session_id)
    current_output = session.get("output", {}) if session else {}

    system = f"""You are a market research assistant. Answer concisely based on:

Research Summary: {current_output.get('executive_summary', 'No summary available.')}

Related Context: {' '.join(context_docs)}

Cite specific facts where possible."""

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
    )
    response = llm.invoke(f"{system}\n\nUser: {req.message}")
    return {"answer": response.content}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
