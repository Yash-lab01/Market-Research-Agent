import os
import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from graph.state import ResearchState

PLANNER_PROMPT = """You are a senior market research strategist. Your job is to design a targeted research plan.

Research Question: {query}

First, classify the query into one of these categories:
- "investment": asking about stocks, IPOs, funds, returns, financial assets
- "technology": asking about tech products, platforms, software, AI, hardware
- "geography": focused on a specific country/region's market
- "competitive": asking about companies, market share, competitors
- "general": broad market analysis

Then, generate 5 to 7 focused sub-tasks that together produce a comprehensive and decisive intelligence report.
Sub-tasks should be SPECIFIC to this query — do NOT use generic buckets like "Market size" or "Trends" unless they are the best fit.

For "investment" queries, good sub-tasks include:
- Specific companies/instruments and their financials
- Risk factors and regulatory environment  
- Historical performance and valuation metrics
- Expert sentiment and analyst ratings

For "technology" queries, good sub-tasks include:
- Technology architecture and differentiation
- Developer ecosystem and adoption metrics
- Funding and M&A activity
- Enterprise vs consumer use-case penetration

For "competitive" queries, good sub-tasks include:
- Market share breakdown by player
- Pricing strategies and business models
- Geographic expansion plans
- Recent product launches and patents

Return ONLY valid JSON:
{{
    "query_category": "investment",
    "sub_tasks": [
        "Specific focused sub-task 1",
        "Specific focused sub-task 2",
        "Specific focused sub-task 3",
        "Specific focused sub-task 4",
        "Specific focused sub-task 5"
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
        query_category = parsed.get("query_category", "general")
        # Clamp to 5-7 sub-tasks
        sub_tasks = sub_tasks[:7] if len(sub_tasks) > 7 else sub_tasks
        if len(sub_tasks) < 3:
            raise ValueError("Too few sub-tasks generated")
    except Exception:
        query_category = "general"
        sub_tasks = [
            f"Key players, companies and competitive landscape for: {state['query']}",
            f"Market size, growth rate and financial data for: {state['query']}",
            f"Recent trends, innovations and emerging technologies in: {state['query']}",
            f"Risks, challenges and regulatory environment for: {state['query']}",
            f"Strategic outlook and expert forecasts for: {state['query']}",
        ]

    return {
        "sub_tasks": sub_tasks,
        "query_category": query_category,
        "status": "🔎 Search Agent: Gathering web data...",
    }
