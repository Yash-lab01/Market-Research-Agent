"""
Streamlit UI for the Autonomous Market Research Agent.
Polls FastAPI (http://localhost:8000) for status and results.
"""
import time
import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API = "http://localhost:8000"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Research Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.agent-card {
    background: #1a1a2e;
    border: 1px solid #2d2d4e;
    border-radius: 12px;
    padding: 12px 16px;
    margin: 6px 0;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.3s ease;
}
.agent-card.active {
    border-color: #6366f1;
    background: linear-gradient(135deg, #1a1a2e, #1e1b4b);
    box-shadow: 0 0 16px rgba(99,102,241,0.2);
}
.agent-card.done { border-color: #10b981; }

.metric-card {
    background: linear-gradient(135deg, #1a1a2e, #1e1b4b);
    border: 1px solid #3730a3;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.metric-value { font-size: 1.4rem; font-weight: 700; color: #a5b4fc; }
.metric-label { font-size: 0.75rem; color: #94a3b8; margin-top: 4px; }

.finding-item {
    background: #1a1a2e;
    border-left: 3px solid #6366f1;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.9rem;
    color: #e2e8f0;
}
.trend-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 3px;
}
.badge-growing    { background: #064e3b; color: #6ee7b7; }
.badge-declining  { background: #450a0a; color: #fca5a5; }
.badge-emerging   { background: #1e1b4b; color: #a5b4fc; }

.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #a5b4fc;
    border-bottom: 1px solid #3730a3;
    padding-bottom: 8px;
    margin: 20px 0 12px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in {
    "session_id": None,
    "polling": False,
    "result": None,
    "history": [],
    "chat_history": [],   # list of {"role": "user"|"assistant", "content": str}
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Market Research Agent")
    st.markdown("*Powered by LangGraph + Groq + Tavily*")
    st.divider()
    st.markdown("**Agent Pipeline**")
    for agent in ["🧠 Planner", "🔎 Search", "🕷️ Scraper", "✅ Verifier", "🧩 Summarizer", "📄 Report"]:
        st.markdown(f"→ {agent}")
    st.divider()
    if st.button("🕐 Refresh History", use_container_width=True):
        try:
            r = requests.get(f"{API}/api/history", timeout=5)
            st.session_state.history = r.json()
        except Exception:
            st.error("API not reachable")

# ── Helper functions ──────────────────────────────────────────────────────────

AGENT_STEPS = [
    ("🧠", "Planner",    "🧠 Planner Agent"),
    ("🔎", "Search",     "🔎 Search Agent"),
    ("🕷️", "Scraper",    "🕷️ Scraper Agent"),
    ("✅", "Verifier",   "✅ Verifier Agent"),
    ("🧩", "Summarizer", "🧩 Summarizer Agent"),
    ("📄", "Report",     "📄 Report Agent"),
]

def _agent_step(current_status: str, emoji: str, name: str, trigger: str) -> str:
    if "completed" in current_status or "error" in current_status:
        return "done"
    if trigger.lower() in current_status.lower():
        return "active"
    return "pending"


def render_agent_progress(status: str):
    cols = st.columns(len(AGENT_STEPS))
    for i, (emoji, name, trigger) in enumerate(AGENT_STEPS):
        state = _agent_step(status, emoji, name, trigger)
        icon = "✅" if state == "done" else ("⚡" if state == "active" else "⏳")
        bg = "#064e3b" if state == "done" else ("#1e1b4b" if state == "active" else "#111827")
        border = "#10b981" if state == "done" else ("#6366f1" if state == "active" else "#374151")
        cols[i].markdown(
            f"""<div style='background:{bg};border:1px solid {border};
            border-radius:10px;padding:10px;text-align:center;'>
            <div style='font-size:1.4rem'>{icon}</div>
            <div style='font-size:0.75rem;color:#94a3b8;margin-top:4px'>{name}</div>
            </div>""",
            unsafe_allow_html=True,
        )


def render_swot(swot: dict):
    labels = [("💪 Strengths","#064e3b","#6ee7b7"),("⚠️ Weaknesses","#451a03","#fcd34d"),
              ("🚀 Opportunities","#1e1b4b","#a5b4fc"),("🔴 Threats","#450a0a","#fca5a5")]
    keys   = ["strengths","weaknesses","opportunities","threats"]
    cols   = st.columns(2)
    for i, (label, bg, color) in enumerate(labels):
        with cols[i % 2]:
            items = swot.get(keys[i], [])
            html  = f"<div style='background:{bg};border-radius:10px;padding:14px;margin:6px 0;'>"
            html += f"<b style='color:{color}'>{label}</b><ul style='margin:8px 0 0 0;padding-left:16px;color:#e2e8f0;font-size:0.85rem;'>"
            for item in items:
                html += f"<li style='margin:4px 0'>{item}</li>"
            html += "</ul></div>"
            st.markdown(html, unsafe_allow_html=True)


def render_charts(output: dict):
    companies  = output.get("companies", [])
    trends     = output.get("trends", [])

    c1, c2 = st.columns(2)

    with c1:
        if companies:
            fig = px.bar(
                x=[c["name"] for c in companies[:7]],
                y=list(range(len(companies[:7]), 0, -1)),
                labels={"x": "Company", "y": "Relative Prominence"},
                title="Company Landscape",
                color_discrete_sequence=["#6366f1"],
            )
            fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e",
                              font_color="#e2e8f0", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if trends:
            direction_counts = {}
            for t in trends:
                d = t.get("direction", "Other")
                direction_counts[d] = direction_counts.get(d, 0) + 1
            fig = go.Figure(go.Pie(
                labels=list(direction_counts.keys()),
                values=list(direction_counts.values()),
                marker_colors=["#10b981", "#ef4444", "#6366f1", "#f59e0b"],
                hole=0.45,
            ))
            fig.update_layout(title="Trend Directions", paper_bgcolor="#1a1a2e",
                              font_color="#e2e8f0")
            st.plotly_chart(fig, use_container_width=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_research, tab_report, tab_monitor, tab_history = st.tabs(
    ["🔍 Research", "📊 Report", "🔔 Monitor", "🕐 History"]
)

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — RESEARCH
# ═══════════════════════════════════════════════════════════════════
with tab_research:
    st.markdown("## 🔍 Research a Market")
    st.markdown("Ask any market question. All 5 agents will work in sequence to produce a full report.")

    query = st.text_area(
        "Research Question",
        placeholder="e.g. Analyze the EV charging market in India",
        height=90,
        label_visibility="collapsed",
    )

    col_btn, col_status = st.columns([1, 3])
    with col_btn:
        start = st.button("🚀 Start Research", type="primary", use_container_width=True)

    if start and query.strip():
        try:
            r = requests.post(f"{API}/api/research", json={"query": query.strip()}, timeout=10)
            data = r.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.polling    = True
            st.session_state.result     = None
        except Exception as e:
            st.error(f"Could not reach API: {e}")

    # ── Polling loop ──────────────────────────────────────────────
    if st.session_state.polling and st.session_state.session_id:
        sid = st.session_state.session_id
        try:
            r    = requests.get(f"{API}/api/research/{sid}", timeout=5)
            data = r.json()
            status = data.get("status", "")

            st.markdown("### Agent Progress")
            render_agent_progress(status)
            st.info(f"**Status:** {status}")

            if status == "completed":
                st.session_state.polling = False
                st.session_state.result  = data
                st.success("✅ Research complete! See the Report tab for full details.")

            elif status.startswith("error"):
                st.session_state.polling = False
                st.error(f"Research failed: {status}")

            else:
                time.sleep(2)
                st.rerun()

        except Exception as e:
            st.error(f"Polling error: {e}")
            st.session_state.polling = False

    # ── Results preview ───────────────────────────────────────────
    if st.session_state.result:
        output = st.session_state.result.get("output", {})
        if not output:
            st.warning("No output yet.")
        else:
            st.divider()
            st.markdown("### 📋 Executive Summary")
            st.markdown(f"> {output.get('executive_summary', '')}")

            st.markdown('<div class="section-header">Key Findings</div>', unsafe_allow_html=True)
            for f in output.get("key_findings", []):
                st.markdown(f'<div class="finding-item">• {f}</div>', unsafe_allow_html=True)

            # Market data metrics
            md = output.get("market_data", {})
            if any(md.values()):
                st.markdown('<div class="section-header">Market Data</div>', unsafe_allow_html=True)
                mc1, mc2, mc3, mc4 = st.columns(4)
                for col, label, key in [
                    (mc1,"Market Size","market_size"), (mc2,"Growth Rate","growth_rate"),
                    (mc3,"Forecast Year","forecast_year"), (mc4,"Key Region","key_geography")
                ]:
                    col.markdown(
                        f'<div class="metric-card"><div class="metric-value">'
                        f'{md.get(key,"N/A")}</div>'
                        f'<div class="metric-label">{label}</div></div>',
                        unsafe_allow_html=True,
                    )

            # Trends
            trends = output.get("trends", [])
            if trends:
                st.markdown('<div class="section-header">Trends</div>', unsafe_allow_html=True)
                badge_class = {"Growing":"badge-growing","Declining":"badge-declining","Emerging":"badge-emerging"}
                for t in trends:
                    cls = badge_class.get(t.get("direction",""), "badge-emerging")
                    st.markdown(
                        f'<span class="trend-badge {cls}">{t.get("direction","")}</span>'
                        f' <b>{t.get("name","")}</b> — {t.get("description","")}',
                        unsafe_allow_html=True,
                    )

            # Follow-up chat
            st.divider()
            st.markdown("### 💬 Follow-up Chat")
            st.caption("Ask multiple questions about this research. Chat history is kept for the session.")

            # Clear chat button
            if st.session_state.chat_history:
                if st.button("🗑️ Clear chat", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()

            # Render full chat history
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Chat input — always visible, clears automatically after submit
            user_q = st.chat_input("Ask a follow-up question...")
            if user_q:
                # Add user message to history and display it
                st.session_state.chat_history.append({"role": "user", "content": user_q})
                with st.chat_message("user"):
                    st.markdown(user_q)

                # Get answer from API
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            cr = requests.post(f"{API}/api/chat", json={
                                "session_id": st.session_state.session_id,
                                "message": user_q,
                            }, timeout=30)
                            answer = cr.json().get("answer", "Sorry, I couldn't get an answer.")
                        except Exception as e:
                            answer = f"Chat error: {e}"
                    st.markdown(answer)

                # Store assistant reply in history
                st.session_state.chat_history.append({"role": "assistant", "content": answer})


# ═══════════════════════════════════════════════════════════════════
# TAB 2 — REPORT
# ═══════════════════════════════════════════════════════════════════
with tab_report:
    st.markdown("## 📊 Full Report")

    if not st.session_state.result:
        st.info("Run a research query first to see the full report here.")
    else:
        output = st.session_state.result.get("output", {})
        sid    = st.session_state.session_id

        # PDF download button
        col_dl, _ = st.columns([1, 3])
        with col_dl:
            if st.button("⬇️ Download PDF Report", type="primary", use_container_width=True):
                try:
                    pr = requests.get(f"{API}/api/reports/{sid}/pdf", timeout=10)
                    st.download_button(
                        "Save PDF", data=pr.content,
                        file_name=f"report_{sid[:8]}.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"PDF error: {e}")

        st.divider()

        # Charts
        st.markdown("### 📈 Visual Analysis")
        render_charts(output)

        # Companies table
        companies = output.get("companies", [])
        if companies:
            st.markdown("### 🏢 Company Landscape")
            df = pd.DataFrame(companies)[["name","market_position","description","notable"] if "notable" in companies[0] else ["name","market_position","description"]]
            st.dataframe(df, use_container_width=True, hide_index=True)

        # SWOT
        swot = output.get("swot", {})
        if any(swot.values()):
            st.markdown("### 🔲 SWOT Analysis")
            render_swot(swot)

        # Citations
        citations = output.get("citations", [])
        if citations:
            st.markdown("### 📚 Sources")
            for c in citations[:12]:
                st.markdown(
                    f"- {c.get('claim','')} — [*{c.get('source','')}*]({c.get('url','')})"
                )


# ═══════════════════════════════════════════════════════════════════
# TAB 3 — MONITOR
# ═══════════════════════════════════════════════════════════════════
with tab_monitor:
    st.markdown("## 🔔 Scheduled Monitoring")
    st.markdown("Save a research query to run automatically. n8n handles the scheduling and sends notifications.")

    with st.form("monitor_form"):
        mq = st.text_input("Query to monitor", placeholder="EV charging market India")
        ms = st.selectbox("Schedule", ["daily", "weekly"])
        submitted = st.form_submit_button("➕ Add Monitor Job", type="primary")

    if submitted and mq.strip():
        try:
            r = requests.post(f"{API}/api/monitor", json={"query": mq.strip(), "schedule": ms}, timeout=5)
            st.success(f"✅ Monitor job created: `{r.json().get('job_id','')[:8]}...`")
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()
    st.markdown("### Active Monitor Jobs")
    try:
        jobs = requests.get(f"{API}/api/monitor", timeout=5).json()
        if jobs:
            df = pd.DataFrame(jobs)[["id","query","schedule","last_run_id","created_at"]]
            df["id"] = df["id"].str[:8] + "..."
            st.dataframe(df, use_container_width=True, hide_index=True)

            del_id = st.text_input("Delete job by ID prefix (first 8 chars):")
            if st.button("🗑️ Delete Job") and del_id:
                # find full ID
                full_id = next((j["id"] for j in jobs if j["id"].startswith(del_id)), None)
                if full_id:
                    requests.delete(f"{API}/api/monitor/{full_id}", timeout=5)
                    st.success("Deleted.")
                    st.rerun()
        else:
            st.info("No active monitor jobs yet.")
    except Exception as e:
        st.error(f"Could not load jobs: {e}")

    st.divider()
    st.markdown("### 🔄 Batch Research")
    st.markdown("Queue multiple queries to run in the background.")
    batch_input = st.text_area(
        "Queries (one per line)",
        placeholder="EV charging market India\nSolar panel market India\nGreen hydrogen market India",
        height=100,
    )
    if st.button("🚀 Run Batch", type="secondary"):
        queries = [q.strip() for q in batch_input.splitlines() if q.strip()]
        if queries:
            try:
                r = requests.post(f"{API}/api/batch", json={"queries": queries}, timeout=10)
                data = r.json()
                st.success(f"Batch `{data['batch_id'][:8]}...` started with {len(queries)} jobs.")
            except Exception as e:
                st.error(f"Batch error: {e}")
        else:
            st.warning("Enter at least one query.")


# ═══════════════════════════════════════════════════════════════════
# TAB 4 — HISTORY
# ═══════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown("## 🕐 Research History")
    try:
        history = requests.get(f"{API}/api/history", timeout=5).json()
        if history:
            df = pd.DataFrame(history)[["id","query","status","created_at"]]
            df["id"]    = df["id"].str[:8] + "..."
            df["query"] = df["query"].str[:70]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No research sessions yet.")
    except Exception as e:
        st.error(f"Could not load history: {e}")
