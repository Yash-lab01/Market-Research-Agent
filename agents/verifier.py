import json
import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from graph.state import ResearchState

VERIFIER_PROMPT = """You are a fact-verification agent. Analyze the search results below for the query: "{query}"

Search Results:
{search_summary}

Extract 6-8 key factual claims. Assess confidence based on how many sources agree.

Return ONLY valid JSON:
{{
    "verified_claims": [
        {{
            "claim": "Specific factual statement",
            "confidence": "High",
            "sources": ["url1", "url2"],
            "category": "market_size"
        }}
    ]
}}

Categories: market_size, company, trend, challenge, technology, regulation"""


def _build_search_summary(state: ResearchState) -> str:
    parts = []
    for task, results in state["search_results"].items():
        parts.append(f"\n### {task}")
        for r in results[:3]:
            parts.append(f"- {r.get('title', '')}: {r.get('content', '')[:250]}")
            parts.append(f"  URL: {r.get('url', '')}")
    return "\n".join(parts)[:4000]


def verifier_node(state: ResearchState) -> dict:
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0,
        format="json",
    )
    prompt = ChatPromptTemplate.from_template(VERIFIER_PROMPT)
    chain = prompt | llm

    try:
        result = chain.invoke({
            "query": state["query"],
            "search_summary": _build_search_summary(state),
        })
        parsed = json.loads(result.content)
        verified_claims = parsed.get("verified_claims", [])
    except Exception as e:
        print(f"[Verifier] Parse error: {e}")
        verified_claims = []

    return {
        "verified_claims": verified_claims,
        "status": "🧩 Summarizer Agent: Synthesizing findings...",
    }
