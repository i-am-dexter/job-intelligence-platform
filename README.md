# Job Intelligence Platform

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered job intelligence platform — not a job board. It parses your resume, builds a
profile, aggregates jobs from ATS providers, ranks them against your preferences, analyzes
ATS/keyword fit and skill gaps, generates tailored resume suggestions, and tracks your
applications through to offer.

Supports any profession (software, data/AI, product, design, devops/cloud, cybersecurity,
sales, marketing, finance, consulting, operations).

**100% usable for free.** The AI features run on a bundled, local [Ollama](https://ollama.com)
model by default — no API key, no signup, no cost. A free-tier cloud option (Groq) and a paid
option (Anthropic) are available as drop-in swaps if you want them; see
[LLM Providers](DEPLOYMENT.md#llm-providers).

## Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic (Python 3.12), PostgreSQL (SQLite for local dev)
- **Frontend**: Next.js (App Router) + TypeScript + Tailwind CSS
- **AI**: pluggable LLM for resume extraction and tailoring — Ollama (free, local, default),
  Groq (free tier), or Anthropic (paid); falls back to rule-based extraction/templates if none
  are configured or reachable
- **Job sources (v1)**: Greenhouse, Lever, Ashby, SmartRecruiters, Workable public ATS APIs

## Quick start

See [DEPLOYMENT.md](DEPLOYMENT.md) for full setup (Docker and local, Windows and Unix).

```bash
cp .env.example .env
docker compose up --build
```

No API key needed — this also pulls a free local LLM (Ollama) automatically.

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

## Project layout

```
backend/    FastAPI app, database models/migrations, scrapers, matching/ATS/gap/tailoring engines
frontend/   Next.js app (resume, profile, preferences, jobs, applications, dashboard)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for how the pieces fit together.

## Scope of this version

This is a single-user (no login) v1. Job aggregation currently pulls from the five ATS
providers listed above via a small configurable seed list of companies (`app/core/config.py`).
Additional sources (RemoteOK, Wellfound, company career pages, etc.), multi-user accounts, and
the platform's other listed "Future Features" (interview prep, recruiter CRM, browser agents,
etc.) are intentionally out of scope for this version.
