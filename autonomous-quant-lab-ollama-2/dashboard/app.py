"""
Phase 6 — FastAPI dashboard.
Run with: uvicorn dashboard.app:app --reload
Then open http://localhost:8000
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from memory.chroma_client import collection

app = FastAPI(title="Autonomous Quant Lab Dashboard")


@app.get("/", response_class=HTMLResponse)
def home():
    all_docs = collection.get()
    metadatas = all_docs.get("metadatas", [])
    total = len(metadatas)
    approved = sum(1 for m in metadatas if m.get("verdict") == "approved")
    rejected = total - approved

    rows = "".join([
        f"<div style='border:1px solid #333;padding:16px;margin:8px 0;border-radius:8px;'>"
        f"<p><strong>Ticker:</strong> {m.get('ticker','?')}</p>"
        f"<p><strong>Profit:</strong> {m.get('profit_pct','?')}%</p>"
        f"<p><strong>Reason:</strong> {m.get('reason','?')}</p></div>"
        for m in metadatas if m.get("verdict") == "approved"
    ]) or "<p>No approved strategies yet.</p>"

    return f"""
    <html><body style="font-family:sans-serif;padding:40px;background:#0a0a0a;color:#fff;">
    <h1>Autonomous Quant Lab</h1><hr>
    <h2>Pipeline Metrics</h2>
    <p>Total tested: <strong>{total}</strong></p>
    <p>Approved: <strong style="color:#4ade80">{approved}</strong></p>
    <p>Rejected: <strong style="color:#f87171">{rejected}</strong></p>
    <hr><h2>Approved Strategies</h2>{rows}
    </body></html>
    """


@app.get("/metrics")
def metrics():
    all_docs = collection.get()
    metadatas = all_docs.get("metadatas", [])
    total = len(metadatas)
    approved = sum(1 for m in metadatas if m.get("verdict") == "approved")
    return {"total": total, "approved": approved, "rejected": total - approved}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
