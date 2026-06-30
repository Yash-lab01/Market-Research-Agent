import os
from report.pdf_builder import build_pdf
from graph.state import ResearchState


def report_node(state: ResearchState) -> dict:
    """Generates the PDF report from the structured output."""
    try:
        pdf_path = build_pdf(
            session_id=state["session_id"],
            query=state["query"],
            output=state["structured_output"],
        )
    except Exception as e:
        print(f"[Report] PDF generation error: {e}")
        pdf_path = None

    return {
        "report_path": pdf_path,
        "status": "completed",
    }
