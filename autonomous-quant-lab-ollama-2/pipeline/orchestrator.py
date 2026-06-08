"""
Phase 6 — Orchestrator.
Runs the full Creator -> Critic -> Judge -> Memory loop.
"""
import os
import time
import json
from agents.creator import run_creator
from agents.critic import run_critic
from agents.judge import run_judge
from memory.chroma_client import save_strategy

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "filings")

metrics = {"total_proposed": 0, "passed_critic": 0, "approved_by_judge": 0}


def load_filings() -> list:
    filings = []
    if not os.path.exists(DATA_DIR):
        print("No filings found. Run scripts/fetch_filings.py first.")
        return []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".txt"):
            ticker = fname.replace("_10K.txt", "")
            with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
                text = f.read()
            filings.append({"ticker": ticker, "text": text})
    return filings


def run_pipeline():
    filings = load_filings()
    if not filings:
        return

    print(f"Loaded {len(filings)} filings. Starting pipeline...\n")

    for filing in filings:
        ticker = filing["ticker"]
        text = filing["text"]

        print(f"\n{'='*50}")
        print(f"Processing: {ticker}")
        print(f"{'='*50}")

        metrics["total_proposed"] += 1

        # Phase 4 — Creator
        creator_output = run_creator(text, ticker)
        if "error" in creator_output:
            print(f"  Creator failed: {creator_output['error']}")
            continue

        hypothesis = creator_output["hypothesis"]
        code = creator_output["code"]
        original_result = creator_output["result"]

        if original_result.get("profit_pct", 0) <= 0:
            print("  Strategy not profitable. Skipping.")
            save_strategy(hypothesis, code, original_result, "rejected", "Not profitable in base backtest.")
            continue

        # Phase 5 — Critic
        critic_output = run_critic(code, ticker, original_result)
        if not critic_output["passed"]:
            save_strategy(hypothesis, code, original_result, "rejected", critic_output["reason"])
            continue

        metrics["passed_critic"] += 1

        # Phase 5 — Judge
        verdict = run_judge(
            hypothesis=hypothesis,
            original_result=original_result,
            stress_result=critic_output["stress_result"],
            critic_reason=critic_output["reason"]
        )

        final_verdict = "approved" if verdict.approved else "rejected"
        save_strategy(hypothesis, code, original_result, final_verdict, verdict.reason)

        if verdict.approved:
            metrics["approved_by_judge"] += 1
            print(f"\n  ✓ STRATEGY APPROVED FOR {ticker}")

        print(f"\n  Metrics: Proposed={metrics['total_proposed']} | Critic Pass={metrics['passed_critic']} | Approved={metrics['approved_by_judge']}")
        time.sleep(1)

    print("\nPipeline complete.")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    run_pipeline()
