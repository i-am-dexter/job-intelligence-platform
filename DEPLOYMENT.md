# Deployment

## Option A — Docker Compose (recommended)

Requires Docker + Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

That's it — no API key required. This starts Postgres, a bundled [Ollama](https://ollama.com)
container (pulls the free `llama3.2` model on first run), runs `alembic upgrade head`, then
starts the backend on `localhost:8000` and the frontend on `localhost:3000`. The first startup
will take a few minutes while the model downloads (~2GB); resume parsing/tailoring will fall
back to rule-based/template output until the pull finishes.

Everything works with zero configuration and zero cost. See [LLM Providers](#llm-providers)
below if you'd rather use a cloud option instead of running a local model.

## Option B — Local processes (no Docker)

On Windows, `.\setup.ps1` (one-time) then `.\run.ps1` automate everything in this section.

### LLM (optional but recommended)

For free, local resume parsing/tailoring assistance without Docker:

```bash
# https://ollama.com/download
ollama pull llama3.2
ollama serve   # usually already running as a background service after install
```

If you skip this, the app still works — resume parsing and tailoring fall back to rule-based
extraction and templates instead of LLM-generated output.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Uses SQLite by default (no Postgres needed) — see app/core/config.py.
export DATABASE_URL="sqlite:///./job_intelligence.db"   # Windows: $env:DATABASE_URL
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
```

## LLM Providers

Resume parsing and resume tailoring can optionally use an LLM for higher-quality output. Every
option is free except Anthropic, and the app degrades gracefully to rule-based extraction /
template-based tailoring if no LLM is reachable — nothing breaks either way.

| `LLM_PROVIDER` | Cost | Setup |
|---|---|---|
| `ollama` (default) | Free | Nothing, in Docker — bundled and auto-pulled. Outside Docker: `ollama pull llama3.2 && ollama serve`. |
| `groq` | Free tier | Get a free key at [console.groq.com](https://console.groq.com) (no credit card), set `GROQ_API_KEY`. |
| `anthropic` | Paid | `pip install anthropic`, set `ANTHROPIC_API_KEY`. Highest quality; only needed if you want to pay for it. |
| `none` | Free | Always uses rule-based extraction / template tailoring, no LLM calls at all. |

Switch providers by setting `LLM_PROVIDER` in `.env` and restarting the backend — no code
changes needed.

## Environment variables

See `.env.example` for the full list. Key ones:

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | Postgres (Docker) or SQLite (local) connection string | Postgres in Docker, SQLite locally |
| `LLM_PROVIDER` | Which LLM backs resume parsing/tailoring — see [LLM Providers](#llm-providers) | `ollama` |
| `OLLAMA_MODEL` | Model to pull/use when `LLM_PROVIDER=ollama` | `llama3.2` |
| `ENABLE_SCHEDULER` | Background job re-aggregates jobs on an interval | `true` |
| `SCHEDULER_INTERVAL_HOURS` | Aggregation interval | `6` |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend -> backend base URL | `http://localhost:8000` |

## Running tests

```bash
cd backend
source .venv/bin/activate
pytest
```

## Database migrations

```bash
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Triggering job aggregation manually

The scheduler re-runs aggregation automatically, but you can also trigger it on demand
(also exposed as the "Fetch new jobs" button on the Jobs page in the UI):

```bash
curl -X POST http://localhost:8000/jobs/aggregate
```

## Configuring which companies to scrape

Seed company lists per ATS provider live in `backend/app/core/config.py`
(`scraper_seed_greenhouse`, `scraper_seed_lever`, etc.) — override via environment variables
of the same name (JSON array) to track different companies.
