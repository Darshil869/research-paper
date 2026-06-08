[WINDOWS_SETUP.md](https://github.com/user-attachments/files/28693619/WINDOWS_SETUP.md)
# Autonomous Quant Lab — Windows Setup Guide

Runs 100% locally. No API keys. No cost. All AI runs on your machine via Ollama.

---

## Prerequisites

### 1. Install Python
- Go to https://www.python.org/downloads/
- Download Python 3.11 or above
- During installation, **check the box that says "Add Python to PATH"**
- Open Command Prompt and verify:
```
python --version
```

### 2. Install Git
- Go to https://git-scm.com/download/win
- Download and install Git
- Open Command Prompt and verify:
```
git --version
```

### 3. Install Ollama
- Go to https://ollama.com
- Download the Windows installer and install it
- Open Command Prompt and verify:
```
ollama --version
```

### 4. Download the Mistral model
- In Command Prompt run:
```
ollama pull mistral
```
- This downloads the Mistral AI model (~4.4 GB). One-time only.
- Wait for it to fully complete before moving on.

---

## Project Setup

### 5. Clone the repository
```
git clone https://github.com/your-username/autonomous-quant-lab.git
cd autonomous-quant-lab
```

### 6. Create a virtual environment
```
python -m venv venv
venv\Scripts\activate
```
You should see `(venv)` appear at the start of your terminal line.

### 7. Install dependencies
```
pip install -r requirements.txt
```
Wait for all packages to finish installing.

---

## Running the Project

### 8. Start Ollama
Open a **new** Command Prompt window and run:
```
ollama serve
```
Leave this window open the entire time you use the project.

### 9. Download stock price data (Phase 1)
Go back to your first Command Prompt window and run:
```
python scripts\fetch_prices.py
```
This downloads 10 years of stock price data for 10 S&P 500 companies.
Saves them as CSV files inside the `data\prices\` folder.

### 10. Download SEC filings (Phase 1)
First open `scripts\fetch_filings.py` in any text editor (Notepad is fine).
Find this line:
```
edgar.set_identity("your_name your_email@example.com")
```
Replace it with your actual name and email — for example:
```
edgar.set_identity("John Smith johnsmith@gmail.com")
```
Save the file. Then run:
```
python scripts\fetch_filings.py
```
This downloads the latest 10-K filings from the SEC website.

### 11. Test the sandbox (Phase 2)
```
python sandbox\backtrader_runner.py
```
You should see output like:
```
Test result: {'ticker': 'AAPL', 'starting_value': 100000.0, 'final_value': 99842.29, 'profit_pct': -0.16, 'error': None}
```
The small loss is normal — it is just a dummy test strategy.
If you see no error, the simulator is working correctly.

### 12. Test the memory database (Phase 3)
```
python memory\chroma_client.py
```
The first time you run this, ChromaDB will download a small model (~60MB).
Wait for it to finish. When complete you should see:
```
Saved strategy to memory. Verdict: approved
Similar strategies found: [...]
```
This confirms the memory database is working.

### 13. Run the full pipeline
```
python main.py
```
You will see all three agents working live in the terminal:
- Creator reads a filing and writes a strategy
- Critic stress-tests it with market friction
- Judge approves or rejects based on economic logic
- Approved strategies are saved to the database

### 14. View the dashboard
Open a **third** Command Prompt window and run:
```
uvicorn dashboard.app:app --reload
```
Then open your browser and go to:
```
http://localhost:8000
```
This shows live metrics — how many strategies were proposed, passed the Critic, and approved by the Judge.

---

## Folder Structure

```
autonomous-quant-lab/
├── scripts/
│   ├── fetch_prices.py       <- downloads stock price data
│   └── fetch_filings.py      <- downloads SEC 10-K filings
├── sandbox/
│   └── backtrader_runner.py  <- trading strategy simulator
├── memory/
│   └── chroma_client.py      <- ChromaDB memory database
├── agents/
│   ├── creator.py            <- Creator agent (Mistral via Ollama)
│   ├── critic.py             <- Critic agent (pure Python)
│   └── judge.py              <- Judge agent (Mistral via Ollama)
├── pipeline/
│   └── orchestrator.py       <- connects all agents in a loop
├── dashboard/
│   └── app.py                <- FastAPI web dashboard
├── data/
│   ├── prices/               <- downloaded stock CSVs go here
│   └── filings/              <- downloaded 10-K text files go here
├── database/
│   └── chroma/               <- ChromaDB stores its files here
├── requirements.txt
└── main.py                   <- entry point, run this to start
```

---

## How It Works

1. **Creator agent** reads a 10-K filing and writes a Python trading strategy
2. Strategy runs in **Backtrader** against 10 years of historical price data
3. **Critic agent** re-runs it with slippage, latency, and higher fees
4. **Judge agent** checks if the logic is economically sound
5. Approved strategies are saved to **ChromaDB** memory
6. The loop repeats for every filing in your data folder

All AI calls go to your local Ollama instance running Mistral.
Nothing leaves your machine.

---

## Troubleshooting

**`python` not recognized**
Make sure you checked "Add Python to PATH" during installation.
Try restarting Command Prompt after installing Python.

**`ollama` not recognized**
Restart Command Prompt after installing Ollama.

**ChromaDB stuck downloading**
Just wait — it is downloading a 60MB model for the first time.
It only happens once.

**`venv\Scripts\activate` not working**
Run this first in Command Prompt:
```
Set-ExecutionPolicy Unrestricted -Scope Process
```
Then try activating again.

**Backtrader TypeError on CSV data**
Make sure you are using the updated `backtrader_runner.py` which handles
multi-level column headers from newer versions of yfinance.

**Port 8000 already in use**
Run the dashboard on a different port:
```
uvicorn dashboard.app:app --reload --port 8001
```
Then open http://localhost:8001

---

## Summary of Commands (Quick Reference)

```
# One-time setup
ollama pull mistral
git clone https://github.com/your-username/autonomous-quant-lab.git
cd autonomous-quant-lab
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Every time you use the project (3 terminal windows)
# Window 1 — keep running
ollama serve

# Window 2 — run the pipeline
python scripts\fetch_prices.py
python scripts\fetch_filings.py
python sandbox\backtrader_runner.py
python memory\chroma_client.py
python main.py

# Window 3 — dashboard
uvicorn dashboard.app:app --reload
```
