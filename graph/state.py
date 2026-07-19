from typing import TypedDict, Optional, List, Dict, Any


class ResearchState(TypedDict):
    query: str
    session_id: str
    query_category: Optional[str]            # investment | technology | geography | competitive | general
    sub_tasks: List[str]
    search_results: Dict[str, List[Dict]]    # sub_task -> [{title, url, content, raw_content}]
    scraped_data: Dict[str, str]             # url -> cleaned text
    verified_claims: List[Dict[str, Any]]    # [{claim, confidence, sources, category}]
    structured_output: Dict[str, Any]        # final synthesized JSON
    report_path: Optional[str]               # absolute path to generated PDF
    status: str                              # human-readable current step
    error: Optional[str]
