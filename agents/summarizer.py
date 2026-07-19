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
            temperature=0.2,
        )
    # Fallback: Gemini
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2,
    )

SUMMARIZER_PROMPT = """You are a senior market research analyst writing for sophisticated investors and executives.
Synthesize all findings below into a comprehensive, decisive intelligence report for: "{query}"
Query Category: {query_category}

Verified Claims (high-confidence facts):
{claims}

Full Research Data:
{search_summary}

Additional Evidence:
{scraped_summary}

Write a thorough, opinionated, data-rich report. Be decisive — avoid hedging everything with "may" or "could".
Use specific numbers wherever the data provides them. If the data is ambiguous, say so explicitly rather than guessing.

Return ONLY valid JSON with this structure:
{{
    "executive_summary": "4-6 sentences. Lead with the most important finding. Include at least 2 specific data points. End with the strategic implication.",
    
    "analysis_narrative": "Write 2-3 focused paragraphs of flowing analysis. This is NOT a bullet list. Reason about what the data means, what the underlying dynamics are, and where this market is headed. Be specific and opinionated.",
    
    "strategic_recommendation": "One decisive sentence that a CEO or investor could act on. Start with a verb: 'Enter this market now because...', 'Avoid short-term positions because...', 'Focus capital on [X] because [Y]...'",
    
    "key_findings": [
        "Finding with specific data point and source context",
        "Finding with specific data point and source context",
        "... (6-10 findings total, each substantive)"
    ],
    
    "companies": [
        {{
            "name": "Company Name",
            "description": "What they do in this market",
            "market_position": "Leader",
            "revenue_estimate": "$X billion or 'Private/Unknown'",
            "notable": "One key differentiating fact with specifics"
        }}
    ],
    
    "trends": [
        {{
            "name": "Trend Name",
            "direction": "Growing",
            "time_horizon": "Near-term",
            "confidence": "High",
            "description": "Explanation with data. What's driving it, what's its magnitude."
        }}
    ],
    
    "swot": {{
        "strengths": ["Specific strength with evidence", "..."],
        "weaknesses": ["Specific weakness with evidence", "..."],
        "opportunities": ["Specific opportunity with market context", "..."],
        "threats": ["Specific threat with evidence", "..."]
    }},
    
    "market_data": {{
        "market_size": "$X billion (year) or estimated range",
        "growth_rate": "X% CAGR or description",
        "forecast_year": "20XX",
        "key_geography": "Primary market region"
    }},
    
    "citations": [
        {{"claim": "Specific claim text", "source": "Source name", "url": "https://..."}}
    ]
}}

Direction values must be exactly: "Growing", "Declining", or "Emerging"
Time horizon values must be exactly: "Near-term", "Mid-term", or "Long-term"  
Confidence values must be exactly: "High", "Medium", or "Low"
Market position values must be exactly: "Leader", "Challenger", or "Niche Player"
"""


def _build_claims_text(state: ResearchState) -> str:
    lines = []
    for c in state.get("verified_claims", []):
        conf = c.get("confidence", "?")
        claim = c.get("claim", "")
        sources = c.get("sources", [])[:2]
        cat = c.get("category", "")
        lines.append(f"[{conf}] [{cat}] {claim} (Sources: {', '.join(sources)})")
    return "\n".join(lines) or "No pre-verified claims — synthesize from raw data below."


def _build_search_summary(state: ResearchState) -> str:
    parts = []
    for task, results in state["search_results"].items():
        parts.append(f"\n### {task}")
        for r in results[:4]:
            title = r.get("title", "")
            content = r.get("content", "")[:500]
            parts.append(f"- {title}: {content}")
    return "\n".join(parts)[:8000]


def _build_scraped_summary(state: ResearchState) -> str:
    parts = []
    scraped = state.get("scraped_data", {})
    for url, text in list(scraped.items())[:6]:
        if text and len(text) > 100:
            parts.append(f"[{url[:60]}]: {text[:1000]}")
    return "\n".join(parts)[:6000] or "No additional scraped content."


def _parse_json(content: str) -> dict:
    """Strip markdown code fences and parse JSON."""
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])
    return json.loads(content)


def summarizer_node(state: ResearchState) -> dict:
    llm = _get_llm()
    prompt = ChatPromptTemplate.from_template(SUMMARIZER_PROMPT)
    chain = prompt | llm

    try:
        result = chain.invoke({
            "query": state["query"],
            "query_category": state.get("query_category", "general"),
            "claims": _build_claims_text(state),
            "search_summary": _build_search_summary(state),
            "scraped_summary": _build_scraped_summary(state),
        })
        structured_output = _parse_json(result.content)
    except Exception as e:
        print(f"[Summarizer] Error: {e}")
        structured_output = {
            "executive_summary": f"Summary failed: {str(e)[:120]}. Please retry.",
            "analysis_narrative": "",
            "strategic_recommendation": "",
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
