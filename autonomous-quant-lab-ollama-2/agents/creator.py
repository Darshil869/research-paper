"""
Phase 4 — Creator Agent (Ollama local version).
Reads a 10-K filing excerpt and generates a trading strategy using Ollama (llama3).
Passes the strategy to Backtrader and returns the result.
No API key needed — runs 100% locally.
"""
import ollama
import json
from sandbox.backtrader_runner import run_strategy
from memory.chroma_client import search_similar

MODEL = "mistral"

CREATOR_PROMPT = """
You are a quantitative trading researcher. You will be given an excerpt from a company's SEC 10-K filing.

Your job:
1. Read the filing and identify one clear economic insight or risk signal.
2. Write a plain-English hypothesis (1-2 sentences) explaining the trading opportunity.
3. Write a complete, executable Python trading strategy using the Backtrader library (bt).
   - The strategy MUST be a class called GeneratedStrategy that extends bt.Strategy.
   - It must implement the next() method with clear buy/sell logic.
   - Do NOT include any imports — bt is already available.

Return your response in this exact JSON format:
{{
  "hypothesis": "your hypothesis here",
  "code": "class GeneratedStrategy(bt.Strategy):\\n    def next(self):\\n        ..."
}}

Return ONLY the JSON. No explanation, no markdown, no backticks.

Past similar strategies that were rejected (avoid repeating these):
{past_attempts}

10-K Filing Excerpt:
{filing_text}
"""

MAX_RETRIES = 3


def call_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the response text."""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


def run_creator(filing_text: str, ticker: str) -> dict:
    """Runs the Creator agent on a filing excerpt."""
    past = search_similar(filing_text[:500], n_results=3)
    past_text = "\n".join([str(p) for p in past]) if past else "None"

    prompt = CREATOR_PROMPT.format(
        filing_text=filing_text[:3000],
        past_attempts=past_text
    )

    for attempt in range(MAX_RETRIES):
        print(f"  Creator attempt {attempt + 1}...")
        try:
            raw = call_ollama(prompt)
            # Strip any accidental markdown fences
            raw = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            hypothesis = parsed["hypothesis"]
            code = parsed["code"]
        except Exception as e:
            print(f"  Creator parse error: {e}")
            continue

        result = run_strategy(code, ticker)

        if result.get("error"):
            print(f"  Backtrader error: {result['error'][:200]}")
            prompt += f"\n\nYour previous code failed with this error:\n{result['error'][:500]}\nPlease fix it and return only the JSON."
            continue

        print(f"  Strategy profit: {result['profit_pct']}%")
        return {"hypothesis": hypothesis, "code": code, "result": result}

    return {"error": "Creator failed after max retries."}
