import os
from tavily import TavilyClient
from graph.state import ResearchState


def search_node(state: ResearchState) -> dict:
    """Runs one Tavily search per sub-task. Uses basic depth to conserve free-tier credits."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    search_results: dict = {}

    for task in state["sub_tasks"]:
        try:
            query = f"{state['query']} - {task}"
            response = client.search(
                query=query,
                max_results=4,
                search_depth="basic",          # 1 credit per call
                include_raw_content=False,
            )
            search_results[task] = response.get("results", [])
        except Exception as e:
            print(f"[Search] Error for '{task}': {e}")
            search_results[task] = []

    return {
        "search_results": search_results,
        "status": "🕷️ Scraper Agent: Extracting page content...",
    }
