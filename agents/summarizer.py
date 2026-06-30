import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from graph.state import ResearchState


def _get_llm():
    """Groq primary (14,400 req/day free), Gemini as fallback."""
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=groq_key,
            temperature=0.1,
        )
    # Fallback: Gemini
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1,
    )

SUMMARIZER_PROMPT = """You are a senior market research analyst. Synthesize all findings below into a comprehensive report for: "{query}"

Verified Claims:
{claims}

Search Results Summary:
{search_summary}

Return ONLY valid JSON with this exact structure:
{{
    "executive_summary": "3-5 sentence high-level overview of the market",
    "key_findings": [
        "Finding 1 with specific data",
        "Finding 2 with specific data",
        "Finding 3 with specific data",
        "Finding 4 with specific data",
        "Finding 5 with specific data"
    ],
    "companies": [
        {{
            "name": "Company Name",
            "description": "What they do in this market",
            "market_position": "Leader/Challenger/Niche Player",
            "notable": "One key differentiating fact"
        }}
    ],
    "trends": [
        {{
            "name": "Trend Name",
            "direction": "Growing",
            "description": "Brief explanation with data if available"
        }}
    ],
    "swot": {{
        "strengths": ["strength1", "strength2", "strength3"],
        "weaknesses": ["weakness1", "weakness2"],
        "opportunities": ["opportunity1", "opportunity2", "opportunity3"],
        "threats": ["threat1", "threat2"]
    }},
    "market_data": {{
        "market_size": "$X billion (year)",
        "growth_rate": "X% CAGR",
        "forecast_year": "20XX",
        "key_geography": "Primary market region"
    }},
    "citations": [
        {{"claim": "Specific claim text", "source": "Source name", "url": "https://..."}}
    ]
}}"""


def _build_claims_text(state: ResearchState) -> str:
    lines = []
    for c in state.get("verified_claims", []):
        lines.append(
            f"- [{c.get('confidence', '?')}] {c.get('claim', '')} "
            f"(Sources: {', '.join(c.get('sources', [])[:2])})"
        )
    return "\n".join(lines) or "No verified claims available."


def _build_search_summary(state: ResearchState) -> str:
    parts = []
    for task, results in state["search_results"].items():
        parts.append(f"\n### {task}")
        for r in results[:3]:
            parts.append(f"- {r.get('title', '')}: {r.get('content', '')[:300]}")
    return "\n".join(parts)[:5000]


def _parse_json(content: str) -> dict:
    """Strip markdown code fences and parse JSON."""
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])  # remove first/last fence lines
    return json.loads(content)


def summarizer_node(state: ResearchState) -> dict:
    llm = _get_llm()
    prompt = ChatPromptTemplate.from_template(SUMMARIZER_PROMPT)
    chain = prompt | llm

    try:
        result = chain.invoke({
            "query": state["query"],
            "claims": _build_claims_text(state),
            "search_summary": _build_search_summary(state),
        })
        structured_output = _parse_json(result.content)
    except Exception as e:
        print(f"[Summarizer] Error: {e}")
        structured_output = {
            "executive_summary": f"Summary failed: {str(e)[:120]}. Please retry.",
            "key_findings": [],
            "companies": [],
            "trends": [],
            "swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
            "market_data": {},
            "citations": [],
        }

    return {
        "structured_output": structured_output,
        "status": "📄 Report Agent: Building PDF...",
    }
