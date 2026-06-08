"""
Phase 5 — Judge Agent (Ollama local version).
Evaluates whether the Creator's hypothesis has sound economic logic.
Runs 100% locally using Ollama (llama3). No API key needed.
"""
import ollama
import json
from pydantic import BaseModel

MODEL = "mistral"


class JudgeVerdict(BaseModel):
    approved: bool
    reason: str


JUDGE_PROMPT = """
You are a Chief Risk Officer and quantitative research auditor.

You will be given:
1. A trading hypothesis
2. The original backtest profit
3. The stress-tested profit (with slippage, latency, and higher fees)
4. The Critic's assessment

Reject the strategy if:
- The hypothesis relies on coincidence with no real economic foundation
- The reasoning mentions arbitrary patterns like day of week or month
- The stress test profit collapsed entirely
- The logic is circular or vague

Approve only if:
- There is a clear, real-world economic reason why this signal predicts price movement
- The strategy survived stress testing with reasonable profit retention

Return ONLY this JSON — no markdown, no backticks, no explanation:
{{
  "approved": true or false,
  "reason": "one clear sentence explaining your decision"
}}

Hypothesis: {hypothesis}
Original profit: {original_profit}%
Stress-tested profit: {stress_profit}%
Critic assessment: {critic_reason}
"""


def run_judge(hypothesis: str, original_result: dict, stress_result: dict, critic_reason: str) -> JudgeVerdict:
    """Runs the Judge agent to perform a semantic audit using Ollama."""
    print("  Judge performing semantic audit...")

    prompt = JUDGE_PROMPT.format(
        hypothesis=hypothesis,
        original_profit=original_result.get("profit_pct", 0),
        stress_profit=stress_result.get("profit_pct", 0),
        critic_reason=critic_reason
    )

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response["message"]["content"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        verdict = JudgeVerdict(**parsed)
    except Exception as e:
        print(f"  Judge error: {e}")
        verdict = JudgeVerdict(approved=False, reason=f"Judge failed to parse response: {e}")

    print(f"  Judge verdict: {'APPROVED' if verdict.approved else 'REJECTED'} — {verdict.reason}")
    return verdict
