import json
import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from graph.state import ResearchState

VERIFIER_PROMPT = """You are a rigorous fact-verification analyst. Review all evidence below for the research question: "{query}"

Search Results:
{search_summary}

Scraped Page Content (additional context):
{scraped_summary}

Extract 8-12 key factual claims. Prioritize claims that:
- Contain specific numbers, percentages, or dates
- Are confirmed by 2+ independent sources
- Are directly relevant and decisive (not vague generalizations)

Rate confidence:
- "High": claim appears in 2+ sources with consistent data
- "Medium": single credible source or slightly inconsistent data  
- "Low": inferred or from a single low-confidence source

Return ONLY valid JSON:
{{
    "verified_claims": [
        {{
            "claim": "Specific factual statement with numbers/data",
            "confidence": "High",
            "sources": ["url1", "url2"],
            "category": "market_size"
        }}
    ]
}}

Categories: market_size, company, trend, challenge, technology, regulation, financial, strategic"""


def _build_search_summary(state: ResearchState) -> str:
    parts = []
    for task, results in state["search_results"].items():
        parts.append(f"\n### Sub-task: {task}")
        for r in results[:4]:
            title = r.get("title", "")
            content = r.get("content", "")[:600]
            url = r.get("url", "")
            parts.append(f"- **{title}**: {content}")
            if url:
                parts.append(f"  URL: {url}")
    return "\n".join(parts)[:6000]


def _build_scraped_summary(state: ResearchState) -> str:
    parts = []
    scraped = state.get("scraped_data", {})
    for url, text in list(scraped.items())[:8]:
        if text and len(text) > 100:
            parts.append(f"\n[Source: {url[:80]}]\n{text[:800]}")
    return "\n".join(parts)[:5000] or "No additional scraped content available."


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
            "scraped_summary": _build_scraped_summary(state),
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
