# Graph Report - .  (2026-07-19)

## Corpus Check
- 34 files · ~77,992 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 102 nodes · 183 edges · 23 communities (12 shown, 11 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.66)
- Token cost: 13,612 input · 1,761 output

## Community Hubs (Navigation)
- Research Workflow Agents
- API Endpoints
- Database and Job Management
- PDF Report Generation
- LLM Summarization Service
- Community 5
- Community 6
- Community 10
- Community 12
- Community 13
- Community 14
- Community 15
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22

## God Nodes (most connected - your core abstractions)
1. `ResearchState` - 24 edges
2. `_conn()` - 13 edges
3. `build_pdf()` - 10 edges
4. `summarizer_node()` - 8 edges
5. `run_research_workflow()` - 8 edges
6. `create_workflow()` - 8 edges
7. `report_node()` - 6 edges
8. `scraper_node()` - 6 edges
9. `search_node()` - 5 edges
10. `verifier_node()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `create_workflow()` --indirect_call--> `summarizer_node()`  [INFERRED]
  graph/workflow.py → agents/summarizer.py
- `ResearchRequest` --uses--> `ResearchState`  [INFERRED]
  api/main.py → graph/state.py
- `MonitorRequest` --uses--> `ResearchState`  [INFERRED]
  api/main.py → graph/state.py
- `BatchRequest` --uses--> `ResearchState`  [INFERRED]
  api/main.py → graph/state.py
- `ChatRequest` --uses--> `ResearchState`  [INFERRED]
  api/main.py → graph/state.py

## Import Cycles
- None detected.

## Communities (23 total, 11 thin omitted)

### Community 0 - "Research Workflow Agents"
Cohesion: 0.26
Nodes (13): planner_node(), Generates the PDF report from the structured output., report_node(), clean_html(), Fetches and cleans HTML from unique URLs found in search results., scraper_node(), Runs one Tavily search per sub-task. Uses basic depth to conserve free-tier cred, search_node() (+5 more)

### Community 1 - "API Endpoints"
Cohesion: 0.15
Nodes (17): BatchRequest, ChatRequest, create_monitor(), delete_monitor(), download_pdf(), follow_up_chat(), get_history(), get_research() (+9 more)

### Community 2 - "Database and Job Management"
Cohesion: 0.23
Nodes (16): Runs synchronously inside a background thread (FastAPI BackgroundTask)., run_research_workflow(), start_batch(), _conn(), create_monitor_job(), create_session(), delete_monitor_job(), get_all_sessions() (+8 more)

### Community 3 - "PDF Report Generation"
Cohesion: 0.40
Nodes (9): build_pdf(), _bullet_list(), _company_table(), _cover(), Returns flowables for a coloured cover block., _section(), _styles(), _swot_table() (+1 more)

### Community 4 - "LLM Summarization Service"
Cohesion: 0.39
Nodes (7): _build_claims_text(), _build_search_summary(), _get_llm(), _parse_json(), Groq primary (14,400 req/day free), Gemini as fallback., Strip markdown code fences and parse JSON., summarizer_node()

### Community 5 - "Community 5"
Cohesion: 0.47
Nodes (5): _get_collection(), get_similar_research(), Store research summary as an embedding for follow-up chat context., Retrieve past research summaries similar to the current query (for follow-up cha, store_research()

### Community 6 - "Community 6"
Cohesion: 0.40
Nodes (3): _agent_step(), Streamlit UI for the Autonomous Market Research Agent. Polls FastAPI (http://loc, render_agent_progress()

## Knowledge Gaps
- **11 isolated node(s):** `Market Research Agent README`, `Docker Compose Configuration`, `Python Dependencies`, `n8n Automation Layer`, `Ollama (Local LLM)` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ResearchState` connect `Research Workflow Agents` to `API Endpoints`, `LLM Summarization Service`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Why does `build_pdf()` connect `PDF Report Generation` to `Research Workflow Agents`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `report_node()` connect `Research Workflow Agents` to `PDF Report Generation`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ResearchState` (e.g. with `BatchRequest` and `ChatRequest`) actually correct?**
  _`ResearchState` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `run_research_workflow()` (e.g. with `start_batch()` and `start_research()`) actually correct?**
  _`run_research_workflow()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Market Research Agent README`, `Docker Compose Configuration`, `Python Dependencies` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `API Endpoints` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._