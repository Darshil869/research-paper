# Autonomous Quant Lab — Local Ollama Version

Runs 100% locally. No API keys. No cost.

---

## Setup

### 1. Install Ollama
Go to https://ollama.com and download Ollama for your OS.

### 2. Pull the model
Open your terminal and run:
```
ollama pull llama3
```
This downloads the llama3 model locally (~4GB). One-time setup.

### 3. Start Ollama
```
ollama serve
```
Keep this running in a separate terminal while you use the project.

### 4. Install Python dependencies
```
pip install -r requirements.txt
```

### 5. Download data (Phase 1)
```
python scripts/fetch_prices.py
python scripts/fetch_filings.py
```

For fetch_filings.py, open the file and replace:
  your_name your_email@example.com
with your actual name and email (SEC requires this).

### 6. Test the sandbox (Phase 2)
```
python sandbox/backtrader_runner.py
```
Should print a test result with a profit number.

### 7. Test the memory (Phase 3)
```
python memory/chroma_client.py
```
Should save and retrieve a test strategy.

### 8. Run the full pipeline
```
python main.py
```

### 9. View the dashboard
In a second terminal:
```
uvicorn dashboard.app:app --reload
```
Then open http://localhost:8000 in your browser.

---

## Folder Structure

```
autonomous-quant-lab/
├── scripts/         <- Phase 1: download data
├── sandbox/         <- Phase 2: Backtrader simulator
├── memory/          <- Phase 3: ChromaDB memory
├── agents/          <- Phases 4-5: Creator, Critic, Judge
├── pipeline/        <- Phase 6: orchestrator loop
├── dashboard/       <- Phase 6: FastAPI web dashboard
├── data/            <- downloaded stock prices and filings
├── database/        <- ChromaDB storage
├── requirements.txt
└── main.py          <- entry point
```

---

## How it works

1. Creator agent reads a 10-K filing and writes a trading strategy
2. Strategy runs in Backtrader against 10 years of historical data
3. Critic re-runs it with slippage, latency, and higher fees
4. Judge checks if the logic is economically sound
5. Approved strategies are saved to ChromaDB memory
6. The loop repeats for every filing in your data folder

All AI calls go to your local Ollama instance. Nothing leaves your machine.
