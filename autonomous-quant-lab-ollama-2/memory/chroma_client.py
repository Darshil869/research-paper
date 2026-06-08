"""
Phase 3 — ChromaDB memory client.
Provides save and search functions for strategy storage.
"""
import chromadb
import os
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "chroma")

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="strategies")


def save_strategy(hypothesis: str, code: str, result: dict, verdict: str, reason: str):
    """Save a strategy attempt to ChromaDB. verdict: 'approved' or 'rejected'"""
    doc_id = str(uuid.uuid4())
    document = f"Hypothesis: {hypothesis}\nVerdict: {verdict}\nReason: {reason}"
    metadata = {
        "verdict": verdict,
        "reason": reason,
        "profit_pct": result.get("profit_pct", 0),
        "ticker": result.get("ticker", ""),
        "code_snippet": code[:500]
    }
    collection.add(documents=[document], metadatas=[metadata], ids=[doc_id])
    print(f"  Saved strategy to memory. Verdict: {verdict}")
    return doc_id


def search_similar(hypothesis: str, n_results: int = 3) -> list:
    """Search ChromaDB for strategies similar to the given hypothesis."""
    results = collection.query(query_texts=[hypothesis], n_results=n_results)
    return results.get("documents", [])


def get_all_approved() -> list:
    """Return all approved strategies from memory."""
    results = collection.get(where={"verdict": "approved"})
    return results.get("documents", [])


if __name__ == "__main__":
    save_strategy(
        hypothesis="Buy when inventory levels rise sharply.",
        code="class TestStrategy(bt.Strategy): pass",
        result={"profit_pct": 12.5, "ticker": "AAPL"},
        verdict="approved",
        reason="Sound economic logic."
    )
    similar = search_similar("high inventory risk strategy")
    print("Similar strategies found:", similar)
