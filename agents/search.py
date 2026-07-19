import os
from tavily import TavilyClient
from graph.state import ResearchState


def search_node(state: ResearchState) -> dict:
    """Runs one Tavily search per sub-task with advanced depth for richer content."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    search_results: dict = {}

    for task in state["sub_tasks"]:
        try:
            query = f"{state['query']} - {task}"
            response = client.search(
                query=query,
                max_results=6,
                search_depth="advanced",       # richer content, ~5 credits per call
                include_raw_content=True,      # pull actual page text
                include_answer=True,           # include Tavily's synthesized answer
            )
            results = response.get("results", [])
            # Attach Tavily's synthesized answer as an extra result entry if available
            tavily_answer = response.get("answer", "")
            if tavily_answer:
                results.insert(0, {
                    "title": "Tavily Synthesized Answer",
                    "url": "",
                    "content": tavily_answer,
                    "raw_content": tavily_answer,
                    "score": 1.0,
                })
            search_results[task] = results
        except Exception as e:
            print(f"[Search] Error for '{task}': {e}")
            search_results[task] = []

    return {
        "search_results": search_results,
        "status": "🕷️ Scraper Agent: Extracting page content...",
    }
