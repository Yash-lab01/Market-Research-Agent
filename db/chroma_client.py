import os
import chromadb
from pathlib import Path

CHROMA_PATH = os.getenv("CHROMA_PATH", "data/chroma")
COLLECTION_NAME = "research_sessions"


def _get_collection():
    Path(CHROMA_PATH).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def store_research(session_id: str, query: str, executive_summary: str):
    """Store research summary as an embedding for follow-up chat context."""
    try:
        col = _get_collection()
        doc = f"Research Query: {query}\n\nSummary: {executive_summary}"
        col.upsert(
            documents=[doc],
            metadatas=[{"session_id": session_id, "query": query}],
            ids=[session_id],
        )
    except Exception as e:
        print(f"[ChromaDB] Store error: {e}")


def get_similar_research(query: str, n: int = 3) -> list[str]:
    """Retrieve past research summaries similar to the current query (for follow-up chat)."""
    try:
        col = _get_collection()
        count = col.count()
        if count == 0:
            return []
        results = col.query(query_texts=[query], n_results=min(n, count))
        return results.get("documents", [[]])[0]
    except Exception as e:
        print(f"[ChromaDB] Query error: {e}")
        return []
