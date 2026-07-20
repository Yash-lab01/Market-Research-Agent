"""
Streamlit UI for the Autonomous Market Research Agent.
Polls FastAPI for status and results. Full premium UI rewrite.
"""
import os
import time
import html as html_mod
import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Market Research Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Master CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    box-sizing: border-box;
}

/* ─── App background ─── */
.stApp {
    background-color: #050a14;
    background-image:
        radial-gradient(ellipse 80% 50% at 10% -10%, rgba(6,182,212,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 110%, rgba(139,92,246,0.12) 0%, transparent 60%);
    background-attachment: fixed;
}
.block-container { padding-top: 0.5rem !important; padding-bottom: 4rem !important; }

/* ─── Hide default Streamlit header/toolbar so tabs are fully visible ─── */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
}
#MainMenu { visibility: hidden !important; }
.stDeployButton { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #1e2d3d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #06b6d4; }

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {
    background: rgba(8,12,24,0.95) !important;
    border-right: 1px solid rgba(6,182,212,0.12) !important;
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem !important; }

/* ─── Animations ─── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-10px) rotate(1deg); }
}
@keyframes orb-pulse {
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.05); }
}
@keyframes pulse-dot {
    0%, 100% { box-shadow: 0 0 0 0 rgba(6,182,212,0.5); }
    50% { box-shadow: 0 0 0 6px rgba(6,182,212,0); }
}
@keyframes line-fill {
    from { width: 0%; }
    to   { width: 100%; }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(13,17,28,0.8);
    padding: 5px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 8px;
}
.stTabs [data-baseweb="tab"] {
    height: 40px;
    border-radius: 8px;
    color: #6b7280;
    border: none;
    padding: 0 18px;
    font-weight: 500;
    font-size: 0.88rem;
    transition: all 0.2s ease;
    background: transparent;
}
.stTabs [data-baseweb="tab"]:hover { color: #e5e7eb; background: rgba(255,255,255,0.04); }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(6,182,212,0.2), rgba(139,92,246,0.2)) !important;
    color: #22d3ee !important;
    border: 1px solid rgba(6,182,212,0.35) !important;
    box-shadow: 0 2px 12px rgba(6,182,212,0.15);
}
.stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 4px; }

/* ─── Buttons ─── */
div.stButton > button {
    background: linear-gradient(135deg, #06b6d4, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 10px 22px !important;
    box-shadow: 0 4px 16px rgba(6,182,212,0.25) !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.01em !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #0891b2, #7c3aed) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(6,182,212,0.35) !important;
}
div.stButton > button:active { transform: translateY(0px) !important; }

/* ─── Inputs ─── */
.stTextArea textarea, .stTextInput input {
    background: rgba(13,17,28,0.8) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #e5e7eb !important;
    font-size: 0.95rem !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: rgba(6,182,212,0.6) !important;
    box-shadow: 0 0 0 3px rgba(6,182,212,0.08), 0 0 20px rgba(6,182,212,0.1) !important;
    outline: none !important;
}

/* ─── Select boxes ─── */
.stSelectbox [data-baseweb="select"] > div {
    background: rgba(13,17,28,0.8) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #e5e7eb !important;
}

/* ─── Dataframes ─── */
.stDataFrame { border-radius: 12px !important; overflow: hidden; border: 1px solid rgba(255,255,255,0.06) !important; }
.stDataFrame table { background: rgba(13,17,28,0.8) !important; }
.stDataFrame th { background: rgba(6,182,212,0.08) !important; color: #22d3ee !important; font-weight: 600 !important; }
.stDataFrame td { color: #d1d5db !important; border-color: rgba(255,255,255,0.04) !important; }
.stDataFrame tr:hover td { background: rgba(6,182,212,0.04) !important; }

/* ─── Dividers ─── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 24px 0 !important; }

/* ─── Alerts ─── */
.stAlert { border-radius: 10px !important; border-left-width: 3px !important; }
.stSuccess { border-left-color: #10b981 !important; background: rgba(16,185,129,0.08) !important; }
.stError { border-left-color: #f43f5e !important; background: rgba(244,63,94,0.08) !important; }
.stWarning { border-left-color: #f59e0b !important; background: rgba(245,158,11,0.08) !important; }
.stInfo { border-left-color: #06b6d4 !important; background: rgba(6,182,212,0.08) !important; }

/* ─── Chat messages ─── */
.stChatMessage { background: rgba(13,17,28,0.6) !important; border: 1px solid rgba(255,255,255,0.05) !important; border-radius: 12px !important; }

/* ─── Custom component classes ─── */

/* Landing orb effect */
.landing-orb {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 400px; height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(6,182,212,0.06) 0%, rgba(139,92,246,0.04) 50%, transparent 70%);
    animation: orb-pulse 4s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}
.landing-wrapper {
    position: relative;
    text-align: center;
    padding: 48px 24px 40px;
    max-width: 720px;
    margin: 0 auto;
    animation: fadeInUp 0.5s ease forwards;
}
.landing-icon { font-size: 4rem; animation: float 5s ease-in-out infinite; display: block; margin-bottom: 20px; }
.landing-title {
    font-size: 2.6rem; font-weight: 800; line-height: 1.15;
    background: linear-gradient(135deg, #22d3ee 0%, #818cf8 50%, #d8b4fe 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shimmer 4s linear infinite;
    margin-bottom: 14px;
}
.landing-sub { color: #6b7280; font-size: 1.05rem; line-height: 1.65; margin-bottom: 28px; max-width: 560px; margin-left: auto; margin-right: auto; }
.feature-tags { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 28px; }
.feature-tag {
    padding: 5px 14px; border-radius: 20px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    color: #9ca3af; font-size: 0.82rem; font-weight: 500;
}
.feature-tag .tag-icon { margin-right: 5px; }

/* Pipeline stepper */
.pipeline-wrap {
    padding: 20px 0 8px;
    animation: fadeIn 0.4s ease forwards;
}
.pipeline-steps {
    display: flex; align-items: flex-start;
    gap: 0; width: 100%; position: relative;
}
.pipeline-step {
    flex: 1; text-align: center; position: relative;
    padding: 14px 6px 12px;
    border-radius: 12px;
    transition: all 0.3s ease;
}
.pipeline-step.done {
    background: rgba(16,185,129,0.07);
    border: 1px solid rgba(16,185,129,0.2);
}
.pipeline-step.active {
    background: linear-gradient(135deg, rgba(6,182,212,0.12), rgba(139,92,246,0.12));
    border: 1px solid rgba(6,182,212,0.4);
    box-shadow: 0 0 20px rgba(6,182,212,0.15);
}
.pipeline-step.pending {
    background: rgba(13,17,28,0.4);
    border: 1px solid rgba(255,255,255,0.05);
}
.pipeline-connector {
    flex: 0 0 24px; height: 2px; margin-top: 28px; position: relative;
    background: rgba(255,255,255,0.06); border-radius: 1px;
}
.pipeline-connector.done { background: rgba(16,185,129,0.5); }
.pipeline-connector.active { background: linear-gradient(90deg, rgba(16,185,129,0.5), rgba(6,182,212,0.5)); }
.step-emoji { font-size: 1.5rem; display: block; margin-bottom: 6px; }
.step-name { font-size: 0.75rem; font-weight: 600; color: #9ca3af; }
.pipeline-step.done .step-name { color: #34d399; }
.pipeline-step.active .step-name { color: #22d3ee; }
.step-status-dot {
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    margin-top: 4px; background: #374151;
}
.pipeline-step.done .step-status-dot { background: #10b981; }
.pipeline-step.active .step-status-dot {
    background: #06b6d4;
    animation: pulse-dot 1.2s ease infinite;
}

/* Live status banner */
.status-banner {
    margin-top: 16px; padding: 12px 18px;
    background: rgba(6,182,212,0.05); border: 1px solid rgba(6,182,212,0.15);
    border-radius: 10px; display: flex; align-items: center; gap: 12px;
    animation: fadeIn 0.3s ease;
}
.status-banner-dot {
    width: 10px; height: 10px; border-radius: 50%;
    background: #06b6d4; flex-shrink: 0;
    animation: pulse-dot 1s ease infinite;
}
.status-banner-text { color: #94a3b8; font-size: 0.88rem; }
.status-banner-text b { color: #e5e7eb; }

/* Executive summary block */
.exec-summary {
    background: linear-gradient(135deg, rgba(6,182,212,0.05), rgba(139,92,246,0.05));
    border: 1px solid rgba(6,182,212,0.15);
    border-radius: 16px; padding: 22px 26px;
    color: #d1d5db; font-size: 1.0rem; line-height: 1.75;
    animation: fadeInUp 0.4s ease forwards;
}

/* Analyst verdict */
.verdict-block {
    background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(6,182,212,0.06));
    border: 1px solid rgba(16,185,129,0.25); border-radius: 14px;
    padding: 18px 22px; margin: 16px 0;
    display: flex; align-items: flex-start; gap: 14px;
    animation: fadeInUp 0.5s ease forwards;
}
.verdict-icon { font-size: 1.5rem; flex-shrink: 0; margin-top: 2px; }
.verdict-text { color: #d1d5db; font-size: 0.97rem; line-height: 1.6; }
.verdict-label { color: #34d399; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }

/* Analysis narrative */
.narrative-block {
    background: rgba(13,17,28,0.5); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 20px 24px;
    color: #c4c9d4; font-size: 0.95rem; line-height: 1.8;
    animation: fadeInUp 0.45s ease forwards;
}
.narrative-block p { margin: 0 0 14px 0; }
.narrative-block p:last-child { margin-bottom: 0; }

/* Section header */
.sec-header {
    font-size: 1.0rem; font-weight: 700; color: #e5e7eb;
    border-bottom: 1px solid rgba(6,182,212,0.15);
    padding-bottom: 8px; margin: 28px 0 14px;
    display: flex; align-items: center; gap: 8px;
}
.sec-header .sh-icon { font-size: 1.1rem; }

/* Finding cards */
.finding-card {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 14px 18px; margin: 8px 0;
    background: rgba(13,17,28,0.5); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px; transition: all 0.25s ease;
    animation: fadeInUp 0.4s ease forwards;
}
.finding-card:hover {
    border-color: rgba(6,182,212,0.3); background: rgba(6,182,212,0.04);
    transform: translateX(3px);
}
.finding-num {
    flex-shrink: 0; width: 26px; height: 26px; border-radius: 6px;
    background: linear-gradient(135deg, #06b6d4, #8b5cf6);
    color: white; font-size: 0.75rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
}
.finding-text { color: #d1d5db; font-size: 0.92rem; line-height: 1.55; }

/* KPI metric tiles */
.kpi-tile {
    background: rgba(13,17,28,0.7); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 18px 16px;
    text-align: center; transition: all 0.25s ease;
    animation: fadeInUp 0.4s ease forwards;
}
.kpi-tile:hover {
    border-color: rgba(6,182,212,0.3);
    box-shadow: 0 8px 24px rgba(6,182,212,0.1);
    transform: translateY(-2px);
}
.kpi-val {
    font-size: 1.45rem; font-weight: 800; line-height: 1.2;
    background: linear-gradient(135deg, #22d3ee, #d8b4fe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.kpi-label { color: #6b7280; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 7px; }

/* Trend cards */
.trend-card {
    background: rgba(13,17,28,0.5); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 14px 16px; margin: 8px 0;
    transition: all 0.25s ease; animation: fadeInUp 0.4s ease forwards;
    display: flex; flex-direction: column; gap: 6px;
}
.trend-card:hover { border-color: rgba(139,92,246,0.3); transform: translateY(-2px); }
.trend-card-header { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.trend-name { font-weight: 600; color: #e5e7eb; font-size: 0.92rem; }
.trend-desc { color: #9ca3af; font-size: 0.85rem; line-height: 1.5; }
.trend-meta { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }
.badge {
    display: inline-flex; align-items: center; padding: 3px 10px;
    border-radius: 20px; font-size: 0.72rem; font-weight: 600;
}
.badge-growing { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.25); }
.badge-declining { background: rgba(244,63,94,0.12); color: #fda4af; border: 1px solid rgba(244,63,94,0.25); }
.badge-emerging { background: rgba(139,92,246,0.12); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.25); }
.badge-nearterm { background: rgba(6,182,212,0.10); color: #67e8f9; border: 1px solid rgba(6,182,212,0.2); }
.badge-midterm { background: rgba(245,158,11,0.10); color: #fcd34d; border: 1px solid rgba(245,158,11,0.2); }
.badge-longterm { background: rgba(139,92,246,0.10); color: #a78bfa; border: 1px solid rgba(139,92,246,0.2); }
.badge-high { background: rgba(16,185,129,0.10); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.2); }
.badge-medium { background: rgba(245,158,11,0.10); color: #fde68a; border: 1px solid rgba(245,158,11,0.2); }
.badge-low { background: rgba(156,163,175,0.10); color: #9ca3af; border: 1px solid rgba(156,163,175,0.2); }

/* Company cards */
.company-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; margin: 12px 0; }
.company-card {
    background: rgba(13,17,28,0.6); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 16px; transition: all 0.25s ease;
    animation: fadeInUp 0.4s ease forwards;
}
.company-card:hover { border-color: rgba(6,182,212,0.25); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
.company-name { font-weight: 700; color: #e5e7eb; font-size: 0.97rem; margin-bottom: 5px; }
.company-desc { color: #9ca3af; font-size: 0.83rem; line-height: 1.5; margin-bottom: 8px; }
.company-meta { display: flex; flex-wrap: wrap; gap: 5px; }
.badge-leader { background: rgba(6,182,212,0.12); color: #22d3ee; border: 1px solid rgba(6,182,212,0.25); }
.badge-challenger { background: rgba(139,92,246,0.12); color: #a78bfa; border: 1px solid rgba(139,92,246,0.25); }
.badge-niche { background: rgba(100,116,139,0.12); color: #94a3b8; border: 1px solid rgba(100,116,139,0.2); }
.company-notable { color: #6b7280; font-size: 0.78rem; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px; }

/* SWOT cards */
.swot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 12px 0; }
.swot-card {
    border-radius: 12px; padding: 16px 18px;
    animation: fadeInUp 0.45s ease forwards;
}
.swot-s { background: rgba(16,185,129,0.05); border: 1px solid rgba(16,185,129,0.2); }
.swot-w { background: rgba(245,158,11,0.05); border: 1px solid rgba(245,158,11,0.2); }
.swot-o { background: rgba(6,182,212,0.05); border: 1px solid rgba(6,182,212,0.2); }
.swot-t { background: rgba(244,63,94,0.05); border: 1px solid rgba(244,63,94,0.2); }
.swot-title { font-weight: 700; font-size: 0.88rem; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
.swot-s .swot-title { color: #34d399; }
.swot-w .swot-title { color: #fbbf24; }
.swot-o .swot-title { color: #22d3ee; }
.swot-t .swot-title { color: #f87171; }
.swot-list { list-style: none; padding: 0; margin: 0; }
.swot-list li { color: #c4c9d4; font-size: 0.84rem; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.04); line-height: 1.5; }
.swot-list li:last-child { border-bottom: none; }
.swot-list li::before { content: "•"; margin-right: 6px; opacity: 0.5; }

/* Citation cards */
.citation-card {
    background: rgba(13,17,28,0.5); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px; padding: 12px 16px; margin: 6px 0;
    transition: all 0.2s ease;
}
.citation-card:hover { border-color: rgba(16,185,129,0.3); }
.citation-claim { color: #d1d5db; font-size: 0.87rem; line-height: 1.5; margin-bottom: 5px; }
.citation-source { display: flex; align-items: center; gap: 6px; }
.citation-source a { color: #34d399; font-size: 0.78rem; font-weight: 600; text-decoration: none; }
.citation-source a:hover { text-decoration: underline; }
.citation-dot { width: 4px; height: 4px; border-radius: 50%; background: #374151; }

/* History cards */
.history-card {
    background: rgba(13,17,28,0.5); border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px; padding: 14px 16px; margin: 6px 0;
    transition: all 0.2s ease; cursor: pointer;
}
.history-card:hover { border-color: rgba(6,182,212,0.25); background: rgba(6,182,212,0.03); }
.history-query { color: #e5e7eb; font-size: 0.9rem; font-weight: 500; margin-bottom: 4px; }
.history-meta { color: #6b7280; font-size: 0.78rem; }

/* Report query header */
.report-header {
    background: linear-gradient(135deg, rgba(6,182,212,0.06), rgba(139,92,246,0.06));
    border: 1px solid rgba(6,182,212,0.15); border-radius: 14px;
    padding: 18px 22px; margin-bottom: 20px;
    display: flex; align-items: center; justify-content: space-between;
}
.report-query { color: #e5e7eb; font-size: 1.05rem; font-weight: 600; }
.report-category-badge {
    padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;
    background: rgba(139,92,246,0.15); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.3);
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in {
    "session_id": None,
    "polling": False,
    "result": None,
    "history": [],
    "chat_history": [],
    "jump_to_research": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 4px 0 16px;'>
        <div style='font-size:1.4rem; font-weight:800; background: linear-gradient(135deg,#22d3ee,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
            📊 Research Agent
        </div>
        <div style='color:#4b5563; font-size:0.78rem; margin-top:4px;'>Powered by LangGraph · Groq · Tavily</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='color:#6b7280; font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:10px;'>Agent Pipeline</div>", unsafe_allow_html=True)

    agents = [
        ("🧠", "Planner", "Breaks query into targeted sub-tasks"),
        ("🔎", "Search", "Advanced Tavily web search (6 results/task)"),
        ("🕷️", "Scraper", "Extracts full page content (18 URLs)"),
        ("✅", "Verifier", "Cross-checks facts against all sources"),
        ("🧩", "Summarizer", "Synthesizes decisive intelligence report"),
        ("📄", "Report", "Generates downloadable PDF"),
    ]
    for emoji, name, desc in agents:
        st.markdown(f"""
        <div style='padding:8px 10px; border-radius:8px; margin:3px 0; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.04);'>
            <div style='display:flex; align-items:center; gap:8px;'>
                <span style='font-size:1rem;'>{emoji}</span>
                <span style='color:#d1d5db; font-size:0.83rem; font-weight:600;'>{name}</span>
            </div>
            <div style='color:#4b5563; font-size:0.74rem; margin-top:3px; margin-left:26px;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("↻ Refresh History", use_container_width=True):
        try:
            r = requests.get(f"{API}/api/history", timeout=5)
            st.session_state.history = r.json()
        except Exception:
            st.error("API not reachable")

    if st.session_state.result:
        st.markdown("---")
        if st.button("＋ New Research", use_container_width=True):
            st.session_state.result = None
            st.session_state.session_id = None
            st.session_state.polling = False
            st.session_state.chat_history = []
            st.rerun()

# ── Pipeline progress helper ───────────────────────────────────────────────────
AGENT_STEPS = [
    ("🧠", "Planner",    "planner agent"),
    ("🔎", "Search",     "search agent"),
    ("🕷️", "Scraper",    "scraper agent"),
    ("✅", "Verifier",   "verifier agent"),
    ("🧩", "Summarizer", "summarizer agent"),
    ("📄", "Report",     "report agent"),
]

def _step_state(status: str, trigger: str) -> str:
    sl = status.lower()
    if "completed" in sl or "error" in sl:
        return "done"
    if trigger in sl:
        return "active"
    return "pending"


def render_pipeline(status: str):
    parts = ["<div class='pipeline-steps'>"]
    for i, (emoji, name, trigger) in enumerate(AGENT_STEPS):
        state = _step_state(status, trigger)
        parts.append(f"""
        <div class='pipeline-step {state}'>
            <span class='step-emoji'>{emoji}</span>
            <div class='step-name'>{name}</div>
            <div class='step-status-dot'></div>
        </div>""")
        if i < len(AGENT_STEPS) - 1:
            conn_cls = "done" if state == "done" else ("active" if state == "active" else "")
            parts.append(f"<div class='pipeline-connector {conn_cls}'></div>")
    parts.append("</div>")
    st.markdown(f"<div class='pipeline-wrap'>{''.join(parts)}</div>", unsafe_allow_html=True)


# ── Section header helper ─────────────────────────────────────────────────────
def sec(icon: str, title: str):
    st.markdown(f"<div class='sec-header'><span class='sh-icon'>{icon}</span>{title}</div>", unsafe_allow_html=True)


# ── Rendering helpers ─────────────────────────────────────────────────────────
def render_findings(findings: list):
    for i, f in enumerate(findings):
        safe_f = html_mod.escape(str(f))
        st.markdown(f"""
        <div class='finding-card'>
            <div class='finding-num'>{i+1}</div>
            <div class='finding-text'>{safe_f}</div>
        </div>""", unsafe_allow_html=True)


def render_trends(trends: list):
    dir_cls = {"Growing": "badge-growing", "Declining": "badge-declining", "Emerging": "badge-emerging"}
    time_cls = {"Near-term": "badge-nearterm", "Mid-term": "badge-midterm", "Long-term": "badge-longterm"}
    conf_cls = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}

    for t in trends:
        d  = t.get("direction", "Growing")
        th = t.get("time_horizon", "")
        cf = t.get("confidence", "")
        d_cls  = dir_cls.get(d, "badge-emerging")
        th_cls = time_cls.get(th, "badge-midterm")
        cf_cls = conf_cls.get(cf, "badge-medium")
        safe_name = html_mod.escape(str(t.get("name", "")))
        safe_desc = html_mod.escape(str(t.get("description", "")))
        safe_d    = html_mod.escape(d)
        safe_th   = html_mod.escape(th)
        safe_cf   = html_mod.escape(cf)
        badges = f"<span class='badge {d_cls}'>{safe_d}</span>"
        if th:
            badges += f" <span class='badge {th_cls}'>{safe_th}</span>"
        if cf:
            badges += f" <span class='badge {cf_cls}'>{safe_cf} confidence</span>"

        st.markdown(f"""
        <div class='trend-card'>
            <div class='trend-card-header'>
                <span class='trend-name'>{safe_name}</span>
            </div>
            <div class='trend-meta'>{badges}</div>
            <div class='trend-desc'>{safe_desc}</div>
        </div>""", unsafe_allow_html=True)


def render_companies(companies: list):
    pos_cls = {"Leader": "badge-leader", "Challenger": "badge-challenger", "Niche Player": "badge-niche"}
    out = "<div class='company-grid'>"
    for c in companies:
        pos     = c.get("market_position", "")
        rev     = c.get("revenue_estimate", "")
        notable = c.get("notable", "")
        pos_badge = pos_cls.get(pos, "badge-niche")
        safe_name    = html_mod.escape(str(c.get("name", "")))
        safe_desc    = html_mod.escape(str(c.get("description", "")))
        safe_pos     = html_mod.escape(pos)
        safe_rev     = html_mod.escape(str(rev))
        safe_notable = html_mod.escape(str(notable))
        rev_html     = f"<span class='badge badge-niche'>{safe_rev}</span>" if rev and rev != "Private/Unknown" else ""
        notable_html = f"<div class='company-notable'>💡 {safe_notable}</div>" if notable else ""
        out += f"""
        <div class='company-card'>
            <div class='company-name'>{safe_name}</div>
            <div class='company-desc'>{safe_desc}</div>
            <div class='company-meta'>
                <span class='badge {pos_badge}'>{safe_pos}</span>
                {rev_html}
            </div>
            {notable_html}
        </div>"""
    out += "</div>"
    st.markdown(out, unsafe_allow_html=True)


def render_swot(swot: dict):
    def card(css, icon, title, key):
        items = swot.get(key, [])
        lis = "".join(f"<li>{html_mod.escape(str(item))}</li>" for item in items)
        return f"<div class='swot-card {css}'><div class='swot-title'>{icon} {title}</div><ul class='swot-list'>{lis}</ul></div>"

    html = "<div class='swot-grid'>"
    html += card("swot-s", "💪", "Strengths",    "strengths")
    html += card("swot-w", "⚠️", "Weaknesses",   "weaknesses")
    html += card("swot-o", "🚀", "Opportunities","opportunities")
    html += card("swot-t", "🔴", "Threats",      "threats")
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_citations(citations: list):
    for c in citations[:15]:
        url = c.get("url","")
        source = c.get("source", url[:40] if url else "Source")
        link = f'<a href="{url}" target="_blank">{source} ↗</a>' if url else f'<span style="color:#6b7280">{source}</span>'
        st.markdown(f"""
        <div class='citation-card'>
            <div class='citation-claim'>{c.get("claim","")}</div>
            <div class='citation-source'><span class='citation-dot'></span>{link}</div>
        </div>""", unsafe_allow_html=True)


def render_charts(output: dict):
    companies = output.get("companies", [])
    trends    = output.get("trends", [])
    swot      = output.get("swot", {})

    c1, c2, c3 = st.columns(3)

    # Chart 1: Companies by market position (horizontal bar, color-coded)
    with c1:
        if companies:
            pos_color = {"Leader": "#06b6d4", "Challenger": "#8b5cf6", "Niche Player": "#475569"}
            fig = go.Figure()
            for comp in companies[:8]:
                pos = comp.get("market_position","Niche Player")
                fig.add_trace(go.Bar(
                    y=[comp.get("name","")],
                    x=[1],
                    orientation="h",
                    marker_color=pos_color.get(pos, "#475569"),
                    text=pos,
                    textposition="inside",
                    insidetextanchor="middle",
                    hovertemplate=f"<b>{comp.get('name','')}</b><br>{pos}<br>{comp.get('description','')[:80]}<extra></extra>",
                ))
            fig.update_layout(
                title=dict(text="Competitive Landscape", font=dict(color="#e5e7eb", size=13)),
                paper_bgcolor="#050a14", plot_bgcolor="#050a14",
                font_color="#9ca3af", showlegend=False,
                xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                yaxis=dict(tickfont=dict(size=11, color="#d1d5db")),
                margin=dict(l=0, r=8, t=36, b=8), height=240,
                bargap=0.25,
            )
            st.plotly_chart(fig, use_container_width=True)

    # Chart 2: SWOT Radar spider chart
    with c2:
        if any(swot.values()):
            cats = ["Strengths", "Opportunities", "Weaknesses", "Threats"]
            vals = [
                len(swot.get("strengths", [])),
                len(swot.get("opportunities", [])),
                len(swot.get("weaknesses", [])),
                len(swot.get("threats", [])),
            ]
            fig = go.Figure(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=cats + [cats[0]],
                fill="toself",
                fillcolor="rgba(6,182,212,0.12)",
                line=dict(color="#06b6d4", width=2),
                marker=dict(color="#06b6d4", size=6),
                hovertemplate="%{theta}: %{r} items<extra></extra>",
            ))
            fig.update_layout(
                title=dict(text="SWOT Balance", font=dict(color="#e5e7eb", size=13)),
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, max(vals)+1], gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#6b7280", size=9)),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#d1d5db", size=11)),
                ),
                paper_bgcolor="#050a14", font_color="#9ca3af",
                margin=dict(l=24, r=24, t=40, b=16), height=240,
            )
            st.plotly_chart(fig, use_container_width=True)

    # Chart 3: Trend scatter (time_horizon vs confidence, colored by direction)
    with c3:
        if trends:
            th_map  = {"Near-term": 1, "Mid-term": 2, "Long-term": 3}
            cf_map  = {"High": 3, "Medium": 2, "Low": 1}
            dir_col = {"Growing": "#10b981", "Declining": "#f43f5e", "Emerging": "#8b5cf6"}
            xs, ys, texts, colors = [], [], [], []
            for t in trends:
                xs.append(th_map.get(t.get("time_horizon","Mid-term"), 2))
                ys.append(cf_map.get(t.get("confidence","Medium"), 2))
                texts.append(t.get("name","")[:22])
                colors.append(dir_col.get(t.get("direction","Emerging"), "#8b5cf6"))
            fig = go.Figure(go.Scatter(
                x=xs, y=ys, mode="markers+text",
                text=texts, textposition="top center",
                marker=dict(color=colors, size=14, opacity=0.85, line=dict(width=1, color="rgba(255,255,255,0.15)")),
                hovertemplate="%{text}<br>Horizon: %{x}<br>Confidence: %{y}<extra></extra>",
            ))
            fig.update_layout(
                title=dict(text="Trend Map", font=dict(color="#e5e7eb", size=13)),
                paper_bgcolor="#050a14", plot_bgcolor="#050a14",
                font_color="#9ca3af",
                xaxis=dict(tickvals=[1,2,3], ticktext=["Near-term","Mid-term","Long-term"], gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="#9ca3af",size=9)),
                yaxis=dict(tickvals=[1,2,3], ticktext=["Low","Medium","High"], gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="#9ca3af",size=9)),
                margin=dict(l=8, r=8, t=36, b=8), height=240,
            )
            st.plotly_chart(fig, use_container_width=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_research, tab_report, tab_monitor, tab_history = st.tabs(
    ["🔍 Research", "📊 Report", "🔔 Monitor", "🕐 History"]
)

# Auto-switch to Research tab after history restore
if st.session_state.get("jump_to_research"):
    st.session_state.jump_to_research = False
    st.markdown("""
    <script>
    (function() {
        // Wait for Streamlit to finish rendering then click the first tab
        function clickFirstTab() {
            var tabList = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
            if (tabList.length > 0) {
                tabList[0].click();
            } else {
                setTimeout(clickFirstTab, 100);
            }
        }
        setTimeout(clickFirstTab, 150);
    })();
    </script>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 1 — RESEARCH
# ═══════════════════════════════════════════════════════════════════
with tab_research:

    # ── Landing ──
    if not st.session_state.polling and not st.session_state.result:
        with st.container(key="landing_view"):
            st.write("")
            _, col_c, _ = st.columns([1, 5, 1])
            with col_c:
                st.markdown("""
                <div class='landing-wrapper'>
                    <span class='landing-icon'>📊</span>
                    <div class='landing-title'>Autonomous Market Intelligence</div>
                    <div class='landing-sub'>
                        Ask any market question. Six specialized AI agents will search, scrape, verify,
                        and synthesize a decisive intelligence report with sourced data.
                    </div>
                    <div class='feature-tags'>
                        <span class='feature-tag'><span class='tag-icon'>⚡</span>6 AI Agents</span>
                        <span class='feature-tag'><span class='tag-icon'>🌐</span>Advanced Web Search</span>
                        <span class='feature-tag'><span class='tag-icon'>🔬</span>Fact Verified</span>
                        <span class='feature-tag'><span class='tag-icon'>🎯</span>Decisive Analysis</span>
                        <span class='feature-tag'><span class='tag-icon'>📄</span>PDF Export</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                query = st.text_area(
                    "Research Question",
                    placeholder="e.g., Best upcoming IPOs in India 2026... or Analyze the EV charging market in Southeast Asia...",
                    height=100,
                    label_visibility="collapsed",
                    key="landing_query_input",
                )
                _, btn_col, _ = st.columns([1, 3, 1])
                with btn_col:
                    start = st.button("🚀 Start Research", type="primary", use_container_width=True)

                if start and query.strip():
                    try:
                        r = requests.post(f"{API}/api/research", json={"query": query.strip()}, timeout=10)
                        data = r.json()
                        st.session_state.session_id = data["session_id"]
                        st.session_state.polling    = True
                        st.session_state.result     = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not reach API: {e}")

    # ── Active session header ──
    else:
        with st.container(key="active_header"):
            active_query = ""
            category     = ""
            if st.session_state.result:
                active_query = st.session_state.result.get("query", "")
                category     = st.session_state.result.get("output", {}).get("query_category", "")
            elif st.session_state.polling:
                active_query = "Research in progress..."

            cat_badge = f"<span class='report-category-badge'>{category.title()}</span>" if category else ""
            st.markdown(f"""
            <div class='report-header'>
                <div class='report-query'>🔍 {active_query}</div>
                {cat_badge}
            </div>""", unsafe_allow_html=True)

    # ── Polling loop ──
    if st.session_state.polling and st.session_state.session_id:
        with st.container(key="polling_view"):
            sid = st.session_state.session_id
            try:
                r    = requests.get(f"{API}/api/research/{sid}", timeout=5)
                data = r.json()
                status = data.get("status", "")

                sec("⚡", "Agent Pipeline")
                render_pipeline(status)

                st.markdown(f"""
                <div class='status-banner'>
                    <div class='status-banner-dot'></div>
                    <div class='status-banner-text'><b>Live:</b> {status}</div>
                </div>""", unsafe_allow_html=True)

                if status == "completed":
                    st.session_state.polling = False
                    st.session_state.result  = data
                    st.rerun()
                elif status.startswith("error"):
                    st.session_state.polling = False
                    st.error(f"Research failed: {status}")
                else:
                    time.sleep(2)
                    st.rerun()

            except Exception as e:
                st.error(f"Polling error: {e}")
                st.session_state.polling = False

    # ── Results ──
    if st.session_state.result:
        with st.container(key="results_view"):
            output = st.session_state.result.get("output", {})
            if not output:
                st.warning("No structured findings returned. Please retry.")
            else:
                # Executive summary
                sec("📋", "Executive Summary")
                st.markdown(f"<div class='exec-summary'>{output.get('executive_summary','')}</div>", unsafe_allow_html=True)

                # Analyst verdict
                rec = output.get("strategic_recommendation", "")
                if rec:
                    sec("🎯", "Analyst Verdict")
                    st.markdown(f"""
                    <div class='verdict-block'>
                        <div class='verdict-icon'>🎯</div>
                        <div>
                            <div class='verdict-label'>Strategic Recommendation</div>
                            <div class='verdict-text'>{rec}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                # Analysis narrative
                narrative = output.get("analysis_narrative", "")
                if narrative:
                    sec("🧠", "Market Analysis")
                    paras = [p.strip() for p in narrative.split("\n") if p.strip()]
                    para_html = "".join(f"<p>{p}</p>" for p in paras)
                    st.markdown(f"<div class='narrative-block'>{para_html}</div>", unsafe_allow_html=True)

                # KPI metrics
                md = output.get("market_data", {})
                if any(md.values()):
                    sec("📈", "Market Metrics")
                    kpi_cols = st.columns(4)
                    kpis = [
                        ("Market Size",    md.get("market_size","N/A")),
                        ("CAGR",           md.get("growth_rate","N/A")),
                        ("Forecast Year",  md.get("forecast_year","N/A")),
                        ("Key Region",     md.get("key_geography","N/A")),
                    ]
                    for col, (label, val) in zip(kpi_cols, kpis):
                        col.markdown(f"<div class='kpi-tile'><div class='kpi-val'>{val}</div><div class='kpi-label'>{label}</div></div>", unsafe_allow_html=True)

                # Key findings
                findings = output.get("key_findings", [])
                if findings:
                    sec("💡", f"Key Findings ({len(findings)})")
                    render_findings(findings)

                # Companies
                companies = output.get("companies", [])
                if companies:
                    sec("🏢", f"Company Landscape ({len(companies)} companies)")
                    render_companies(companies)

                # Trends
                trends = output.get("trends", [])
                if trends:
                    sec("📡", f"Industry Trends ({len(trends)} identified)")
                    render_trends(trends)

                st.divider()

                # Follow-up chat
                sec("💬", "Follow-up Chat")
                st.caption("Ask follow-up questions — chat history is maintained for this session.")
                if st.session_state.chat_history:
                    if st.button("🗑️ Clear chat", key="clear_chat_research"):
                        st.session_state.chat_history = []
                        st.rerun()
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                user_q = st.chat_input("Ask a follow-up question...")
                if user_q:
                    st.session_state.chat_history.append({"role": "user", "content": user_q})
                    with st.chat_message("user"):
                        st.markdown(user_q)
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            try:
                                cr = requests.post(f"{API}/api/chat", json={
                                    "session_id": st.session_state.session_id,
                                    "message": user_q,
                                }, timeout=30)
                                answer = cr.json().get("answer", "Sorry, couldn't get an answer.")
                            except Exception as e:
                                answer = f"Chat error: {e}"
                        st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})


# ═══════════════════════════════════════════════════════════════════
# TAB 2 — REPORT
# ═══════════════════════════════════════════════════════════════════
with tab_report:
    if not st.session_state.result:
        st.markdown("""
        <div style='text-align:center; padding: 60px 20px; color:#4b5563;'>
            <div style='font-size:3rem; margin-bottom:16px;'>📊</div>
            <div style='font-size:1.1rem; font-weight:600; color:#6b7280;'>No report yet</div>
            <div style='font-size:0.88rem; margin-top:8px;'>Run a research query first to see the full report here.</div>
        </div>""", unsafe_allow_html=True)
    else:
        output = st.session_state.result.get("output", {})
        sid    = st.session_state.session_id
        query  = st.session_state.result.get("query", "")
        cat    = output.get("query_category", "")

        cat_badge = f"<span class='report-category-badge'>{cat.title()}</span>" if cat else ""
        st.markdown(f"""
        <div class='report-header'>
            <div class='report-query'>📊 {query}</div>
            {cat_badge}
        </div>""", unsafe_allow_html=True)

        col_dl, _ = st.columns([1, 4])
        with col_dl:
            if st.button("⬇️ Download PDF Report", type="primary", use_container_width=True):
                try:
                    pr = requests.get(f"{API}/api/reports/{sid}/pdf", timeout=10)
                    st.download_button(
                        "💾 Save PDF", data=pr.content,
                        file_name=f"report_{sid[:8]}.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"PDF error: {e}")

        st.divider()

        # Visual charts
        sec("📈", "Visual Intelligence")
        render_charts(output)

        st.divider()

        # SWOT
        swot = output.get("swot", {})
        if any(swot.values()):
            sec("🔲", "SWOT Analysis")
            render_swot(swot)

        # Full company table
        companies = output.get("companies", [])
        if companies:
            sec("🏢", "Company Details")
            safe_cols = [c for c in ["name","market_position","revenue_estimate","description","notable"] if any(c in comp for comp in companies)]
            try:
                df = pd.DataFrame(companies)[safe_cols]
                st.dataframe(df, use_container_width=True, hide_index=True)
            except Exception:
                st.dataframe(pd.DataFrame(companies), use_container_width=True, hide_index=True)

        # Citations
        citations = output.get("citations", [])
        if citations:
            sec("📚", f"Sources & Citations ({len(citations)})")
            render_citations(citations)


# ═══════════════════════════════════════════════════════════════════
# TAB 3 — MONITOR
# ═══════════════════════════════════════════════════════════════════
with tab_monitor:
    sec("🔔", "Scheduled Market Monitoring")
    st.markdown("<div style='color:#6b7280; font-size:0.88rem; margin-bottom:20px;'>Save a query to run automatically. n8n handles scheduling and sends notifications.</div>", unsafe_allow_html=True)

    with st.form("monitor_form"):
        mq = st.text_input("Query to monitor", placeholder="e.g., EV charging market in India")
        ms = st.selectbox("Schedule", ["daily", "weekly"])
        submitted = st.form_submit_button("➕ Add Monitor Job", type="primary")

    if submitted and mq.strip():
        try:
            r = requests.post(f"{API}/api/monitor", json={"query": mq.strip(), "schedule": ms}, timeout=5)
            st.success(f"✅ Monitor job created: `{r.json().get('job_id','')[:8]}...`")
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()
    sec("📋", "Active Monitor Jobs")
    try:
        jobs = requests.get(f"{API}/api/monitor", timeout=5).json()
        if jobs:
            df = pd.DataFrame(jobs)[["id","query","schedule","last_run_id","created_at"]]
            df["id"] = df["id"].str[:8] + "..."
            st.dataframe(df, use_container_width=True, hide_index=True)
            del_id = st.text_input("Delete job by ID prefix (first 8 chars):")
            if st.button("🗑️ Delete Job") and del_id:
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
    sec("⚡", "Batch Research")
    st.markdown("<div style='color:#6b7280; font-size:0.88rem; margin-bottom:12px;'>Queue multiple queries to run in the background.</div>", unsafe_allow_html=True)
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
    sec("🕐", "Research History")
    try:
        history = requests.get(f"{API}/api/history", timeout=5).json()
        if history:
            options = {
                f"{h['query'][:70]}  ({h['created_at'][:16]})": h['id']
                for h in history if h.get('query')
            }
            selected = st.selectbox("Restore a past report:", ["— Choose —"] + list(options.keys()))
            if selected != "— Choose —":
                if st.button("🔄 Restore & View Report", type="primary"):
                    with st.spinner("Restoring..."):
                        try:
                            r = requests.get(f"{API}/api/research/{options[selected]}", timeout=5)
                            data = r.json()
                            st.session_state.session_id     = options[selected]
                            st.session_state.polling        = False
                            st.session_state.result         = data
                            st.session_state.chat_history   = []
                            st.session_state.jump_to_research = True
                            st.rerun()
                        except Exception as err:
                            st.error(f"Failed to restore: {err}")

            st.divider()

            # Rich history cards
            for h in history[:20]:
                status_color = "#10b981" if h.get("status") == "completed" else "#f59e0b"
                st.markdown(f"""
                <div class='history-card'>
                    <div class='history-query'>{h.get("query","")[:80]}</div>
                    <div class='history-meta'>
                        <span style='color:{status_color}; font-weight:600;'>● {h.get("status","")}</span>
                        &nbsp;·&nbsp; {h.get("created_at","")[:16]}
                        &nbsp;·&nbsp; <span style='color:#374151; font-size:0.72rem;'>{h.get("id","")[:8]}...</span>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No research sessions yet. Run your first query to get started.")
    except Exception as e:
        st.error(f"Could not load history: {e}")
