"""
Phase 1 — Download 10 years of stock price data for S&P 500 tickers.
Saves each ticker as a CSV file in data/prices/
"""
import yfinance as yf
import os

TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "TSLA", "NVDA", "JPM", "JNJ", "V"
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "prices")


def fetch_prices():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for ticker in TICKERS:
        print(f"Downloading {ticker}...")
        df = yf.download(ticker, period="10y", interval="1d", auto_adjust=True)
        if df.empty:
            print(f"  No data for {ticker}, skipping.")
            continue
        path = os.path.join(OUTPUT_DIR, f"{ticker}.csv")
        df.to_csv(path)
        print(f"  Saved to {path}")
    print("Done. All price data downloaded.")


if __name__ == "__main__":
    fetch_prices()
