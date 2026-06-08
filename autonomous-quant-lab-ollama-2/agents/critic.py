"""
Phase 5 — Critic Agent.
Re-runs the Creator's strategy with harsher market conditions.
"""
from sandbox.backtrader_runner import run_strategy

STRESS_SLIPPAGE = 0.005
STRESS_COMMISSION = 0.003
STRESS_LATENCY = 1
PROFIT_SURVIVAL_THRESHOLD = 0.5


def run_critic(code: str, ticker: str, original_result: dict) -> dict:
    """Stress-tests a strategy by injecting market friction."""
    print("  Critic running stress test...")

    stress_result = run_strategy(
        strategy_code=code,
        ticker=ticker,
        slippage=STRESS_SLIPPAGE,
        commission=STRESS_COMMISSION,
        latency_bars=STRESS_LATENCY
    )

    if stress_result.get("error"):
        return {
            "passed": False,
            "reason": f"Strategy crashed under stress: {stress_result['error'][:200]}",
            "original_result": original_result,
            "stress_result": stress_result
        }

    original_profit = original_result.get("profit_pct", 0)
    stress_profit = stress_result.get("profit_pct", 0)

    if original_profit <= 0:
        passed, reason = False, "Original strategy was not profitable."
    elif stress_profit <= 0:
        passed, reason = False, f"Strategy wiped out under friction. Original: {original_profit}%, Stress: {stress_profit}%"
    else:
        survival_rate = stress_profit / original_profit
        if survival_rate >= PROFIT_SURVIVAL_THRESHOLD:
            passed, reason = True, f"Survived stress test. Profit held at {round(survival_rate*100)}% of original."
        else:
            passed, reason = False, f"Profit collapsed under friction. Original: {original_profit}%, Stress: {stress_profit}%"

    print(f"  Critic verdict: {'PASS' if passed else 'FAIL'} — {reason}")
    return {"passed": passed, "reason": reason, "original_result": original_result, "stress_result": stress_result}
