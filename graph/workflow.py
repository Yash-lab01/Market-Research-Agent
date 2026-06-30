from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from agents.planner import planner_node
from agents.search import search_node
from agents.scraper import scraper_node
from agents.verifier import verifier_node
from agents.summarizer import summarizer_node
from agents.report_agent import report_node


def create_workflow():
    workflow = StateGraph(ResearchState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("search", search_node)
    workflow.add_node("scraper", scraper_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("report", report_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "search")
    workflow.add_edge("search", "scraper")
    workflow.add_edge("scraper", "verifier")
    workflow.add_edge("verifier", "summarizer")
    workflow.add_edge("summarizer", "report")
    workflow.add_edge("report", END)

    return workflow.compile()


# Single compiled instance — imported by api/main.py
research_app = create_workflow()
