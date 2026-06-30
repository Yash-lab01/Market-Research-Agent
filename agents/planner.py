import json
import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from graph.state import ResearchState

PLANNER_PROMPT = """You are a market research planning expert.
Break the following research question into exactly 4 focused sub-tasks that together give comprehensive market intelligence.

Research Question: {query}

Return ONLY valid JSON, no explanation:
{{
    "sub_tasks": [
        "Key players, companies and competitive landscape",
        "Market size, growth rate and financial projections",
        "Recent trends, innovations and emerging technologies",
        "Challenges, risks and market barriers"
    ]
}}"""


def planner_node(state: ResearchState) -> dict:
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
        format="json",
    )
    prompt = ChatPromptTemplate.from_template(PLANNER_PROMPT)
    chain = prompt | llm

    try:
        result = chain.invoke({"query": state["query"]})
        parsed = json.loads(result.content)
        sub_tasks = parsed.get("sub_tasks", [])
    except Exception:
        sub_tasks = [
            f"Key players and companies in: {state['query']}",
            f"Market size and growth rate for: {state['query']}",
            f"Trends and innovations in: {state['query']}",
            f"Challenges and barriers in: {state['query']}",
        ]

    return {
        "sub_tasks": sub_tasks,
        "status": "🔎 Search Agent: Gathering web data...",
    }
