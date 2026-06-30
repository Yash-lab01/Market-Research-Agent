import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from graph.state import ResearchState

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


def summarizer_node(state: ResearchState) -> dict:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1,
    )
    prompt = ChatPromptTemplate.from_template(SUMMARIZER_PROMPT)
    chain = prompt | llm

    try:
        result = chain.invoke({
            "query": state["query"],
            "claims": _build_claims_text(state),
            "search_summary": _build_search_summary(state),
        })
        # Gemini may wrap in markdown code block
        content = result.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        structured_output = json.loads(content)
    except Exception as e:
        print(f"[Summarizer] Parse error: {e}")
        structured_output = {
            "executive_summary": "Summary generation failed. Please retry.",
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
