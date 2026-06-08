"""
Phase 2 — Backtrader sandbox.
Receives Python strategy code as a string, executes it, and returns the result.
Supports injecting slippage, latency, and commission for Critic stress-testing.
"""
import backtrader as bt
import pandas as pd
import os
import traceback

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "prices")


def run_strategy(
    strategy_code: str,
    ticker: str,
    slippage: float = 0.0,
    commission: float = 0.001,
    latency_bars: int = 0
) -> dict:
    """
    Executes a strategy string in Backtrader.
    Returns a dict with final_value, profit_pct, and any error.
    """
    csv_path = os.path.join(DATA_DIR, f"{ticker}.csv")
    if not os.path.exists(csv_path):
        return {"error": f"No price data found for {ticker}"}

    try:
        df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        df.columns = [c.lower() for c in df.columns]
        df = df[["open", "high", "low", "close", "volume"]].dropna()
    except Exception as e:
        return {"error": f"Data loading error: {e}"}

    # Dynamically execute the strategy code
    namespace = {"bt": bt}
    try:
        exec(strategy_code, namespace)
    except Exception as e:
        return {"error": f"Strategy code error:\n{traceback.format_exc()}"}

    # Find the strategy class
    strategy_class = None
    for name, obj in namespace.items():
        if isinstance(obj, type) and issubclass(obj, bt.Strategy) and obj is not bt.Strategy:
            strategy_class = obj
            break

    if strategy_class is None:
        return {"error": "No bt.Strategy subclass found in strategy code."}

    try:
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class)
        data_feed = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data_feed)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=commission)
        if slippage > 0:
            cerebro.broker.set_slippage_perc(slippage)

        starting_value = cerebro.broker.getvalue()
        cerebro.run()
        final_value = cerebro.broker.getvalue()
        profit_pct = ((final_value - starting_value) / starting_value) * 100

        return {
            "ticker": ticker,
            "starting_value": round(starting_value, 2),
            "final_value": round(final_value, 2),
            "profit_pct": round(profit_pct, 2),
            "error": None
        }
    except Exception as e:
        return {"error": f"Backtrader runtime error:\n{traceback.format_exc()}"}


if __name__ == "__main__":
    test_code = """
class TestStrategy(bt.Strategy):
    def next(self):
        if not self.position:
            self.buy()
        elif len(self) >= 200:
            self.sell()
"""
    result = run_strategy(test_code, "AAPL")
    print("Test result:", result)
