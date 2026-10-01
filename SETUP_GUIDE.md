# Setup Guide – Multi-Agent Lead Generation System

## Prerequisites
- Python 3.10+ (3.11+ recommended)
- Node.js 18+ and npm
- (Optional) A Groq / OpenAI / OpenRouter API key, or Ollama locally. Without one, use `LLM_PROVIDER=mock`.

## 1. Unzip and enter the project
```bash
unzip multi_agent_lead_gen.zip -d multi_agent_lead_gen
cd multi_agent_lead_gen
```

## 2. Backend (Python)
```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
playwright install chromium        # needed for Google Maps scraping
```

## 3. Environment config
```bash
cp backend/.env.example backend/.env
```
Edit `backend/.env`:
- `LLM_PROVIDER` – `groq`, `ollama`, `openrouter`, `openai` or `mock` (no key needed)
- `LLM_API_KEY` – your provider key (not needed for `mock`/`ollama`)
- `SCHEDULE_INTERVAL_HOURS`, `MAX_SCRAPED_PER_RUN`, `SENDER_NAME` – tune as needed

## 4. Frontend (React + Vite)
```bash
npm install --prefix frontend
npm install                         # root: installs `concurrently`
```

## 5. Run
Option A – both servers at once:
```bash
npm start
```
Option B – separately:
```bash
# terminal 1
cd backend && ../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# terminal 2
cd frontend && npm run dev -- --host 0.0.0.0 --port 5173
```
Note: `run.sh` has a macOS-specific PATH line; edit or prefer `npm start` on other machines.

- Dashboard: http://localhost:5173
- API docs (Swagger): http://localhost:8000/docs

## 6. Run tests
```bash
npm test
# or: .venv/bin/pytest tests/ -v
```
Tests use an in-memory SQLite DB and a stubbed scraper, so no network or API key is needed.

## Troubleshooting
- **`.venv/bin/pytest: No such file`** – create the venv and install requirements (step 2) first.
- **Scraper fails** – run `playwright install chromium`; set `SCRAPER_HEADLESS=false` to debug.
- **LLM errors** – set `LLM_PROVIDER=mock` or keep `LLM_FALLBACK_TO_MOCK=true`.
- **Ports in use** – `npm run stop` frees 8000 and 5173.
- **Reset data** – delete `backend/leadgen.db`; it is recreated on start.
