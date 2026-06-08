"""
Phase 1 — Download latest 10-K filings from SEC EDGAR using edgartools.
Saves each filing as a .txt file in data/filings/
"""
import edgar
import os

TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "TSLA", "NVDA", "JPM", "JNJ", "V"
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "filings")


def fetch_filings():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # SEC requires an identity — replace with your name and email
    edgar.set_identity("your_name your_email@example.com")

    for ticker in TICKERS:
        print(f"Fetching 10-K for {ticker}...")
        try:
            company = edgar.Company(ticker)
            filings = company.get_filings(form="10-K").latest(1)
            doc = filings.obj()
            text = doc.text if hasattr(doc, "text") else str(doc)
            path = os.path.join(OUTPUT_DIR, f"{ticker}_10K.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"  Saved to {path}")
        except Exception as e:
            print(f"  Failed for {ticker}: {e}")

    print("Done. All filings downloaded.")


if __name__ == "__main__":
    fetch_filings()
