import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "data/research.db")


def _conn():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS research_sessions (
            id          TEXT PRIMARY KEY,
            query       TEXT NOT NULL,
            status      TEXT DEFAULT 'pending',
            batch_id    TEXT,
            created_at  TEXT,
            updated_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS research_results (
            session_id  TEXT PRIMARY KEY,
            output_json TEXT,
            created_at  TEXT,
            FOREIGN KEY (session_id) REFERENCES research_sessions(id)
        );

        CREATE TABLE IF NOT EXISTS monitor_jobs (
            id          TEXT PRIMARY KEY,
            query       TEXT NOT NULL,
            schedule    TEXT NOT NULL,
            last_run_id TEXT,
            active      INTEGER DEFAULT 1,
            created_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS reports (
            session_id  TEXT PRIMARY KEY,
            pdf_path    TEXT,
            created_at  TEXT
        );
    """)
    conn.commit()
    conn.close()


# ── Sessions ──────────────────────────────────────────────────────────────────

def create_session(session_id: str, query: str, batch_id: str = None):
    now = datetime.now().isoformat()
    conn = _conn()
    conn.execute(
        "INSERT INTO research_sessions (id, query, status, batch_id, created_at, updated_at) "
        "VALUES (?, ?, 'pending', ?, ?, ?)",
        (session_id, query, batch_id, now, now),
    )
    conn.commit()
    conn.close()


def update_session_status(session_id: str, status: str):
    conn = _conn()
    conn.execute(
        "UPDATE research_sessions SET status=?, updated_at=? WHERE id=?",
        (status, datetime.now().isoformat(), session_id),
    )
    conn.commit()
    conn.close()


def get_session(session_id: str) -> dict | None:
    conn = _conn()
    row = conn.execute(
        "SELECT s.*, r.output_json "
        "FROM research_sessions s "
        "LEFT JOIN research_results r ON s.id = r.session_id "
        "WHERE s.id=?",
        (session_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    if data.get("output_json"):
        data["output"] = json.loads(data["output_json"])
    return data


def get_all_sessions() -> list:
    conn = _conn()
    rows = conn.execute(
        "SELECT * FROM research_sessions ORDER BY created_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Results & Reports ─────────────────────────────────────────────────────────

def save_result(session_id: str, output: dict):
    conn = _conn()
    conn.execute(
        "INSERT OR REPLACE INTO research_results (session_id, output_json, created_at) "
        "VALUES (?, ?, ?)",
        (session_id, json.dumps(output), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def save_report(session_id: str, pdf_path: str):
    conn = _conn()
    conn.execute(
        "INSERT OR REPLACE INTO reports (session_id, pdf_path, created_at) VALUES (?, ?, ?)",
        (session_id, pdf_path, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_report_path(session_id: str) -> str | None:
    conn = _conn()
    row = conn.execute(
        "SELECT pdf_path FROM reports WHERE session_id=?", (session_id,)
    ).fetchone()
    conn.close()
    return row["pdf_path"] if row else None


# ── Monitor Jobs ──────────────────────────────────────────────────────────────

def create_monitor_job(job_id: str, query: str, schedule: str):
    conn = _conn()
    conn.execute(
        "INSERT INTO monitor_jobs (id, query, schedule, active, created_at) VALUES (?, ?, ?, 1, ?)",
        (job_id, query, schedule, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_monitor_jobs() -> list:
    conn = _conn()
    rows = conn.execute(
        "SELECT * FROM monitor_jobs WHERE active=1 ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_monitor_last_run(job_id: str, session_id: str):
    conn = _conn()
    conn.execute(
        "UPDATE monitor_jobs SET last_run_id=? WHERE id=?", (session_id, job_id)
    )
    conn.commit()
    conn.close()


def delete_monitor_job(job_id: str):
    conn = _conn()
    conn.execute("UPDATE monitor_jobs SET active=0 WHERE id=?", (job_id,))
    conn.commit()
    conn.close()
