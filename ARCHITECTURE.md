# Architecture

## High-level flow

```
Resume Upload -> Resume Parsing -> Profile Generation -> Preference Selection
  -> Job Aggregation -> Job Normalization -> Job Ranking -> ATS Analysis
  -> Gap Analysis -> Resume Tailoring -> Application Tracking -> Apply Link
```

## Backend (`backend/app`)

- **`main.py`** — FastAPI app, CORS, router registration, scheduler lifespan.
- **`core/config.py`** — `pydantic-settings` config, including scraper seed company lists.
- **`db/models.py`** — SQLAlchemy models for all 10 tables (`profiles`, `preferences`,
  `companies`, `jobs`, `job_skills`, `applications`, `saved_jobs`, `resume_versions`,
  `tailoring_suggestions`, `system_logs`).
- **`api/routes/`** — one router per domain area (resume, profile, preferences, jobs, ats,
  gaps, tailoring, applications, dashboard).
- **`services/`**
  - `llm.py` — pluggable LLM access behind one `complete_json()` entry point. Provider is
    chosen via `LLM_PROVIDER`: `ollama` (free, local, default), `groq` (free tier, cloud),
    `anthropic` (paid), or `none`. Callers never know which provider is active.
  - `resume_parser.py` — PDF/DOCX text extraction, then LLM-assisted structured extraction
    into a profile shape via `llm.py`, with a rule-based (regex + skills taxonomy) fallback
    when no LLM is configured or the call fails.
  - `scrapers/` — `base.py` defines the `discover_jobs -> extract_job -> normalize_job ->
    validate_job -> store_job` pipeline every scraper implements, producing a shared
    `JobRecord`. One module per ATS source (`greenhouse.py`, `lever.py`, `ashby.py`,
    `smartrecruiters.py`, `workable.py`), wired together in `registry.py`.
  - `dedup.py` — SHA256(company + title + location) is the job uniqueness key, enforced both
    by a pre-insert lookup and a DB unique constraint (races within a batch are caught and
    skipped rather than crashing the whole scrape).
  - `matching_engine.py` — weighted composite of skill/experience/preference/domain/
    location/salary/ATS match into a single 0–100 match score.
  - `ats_engine.py` — keyword/skill extraction from the job text vs. the profile, producing
    coverage %, matched/missing keywords, and recommendations.
  - `gap_engine.py` — matched/missing/suggested skills plus a small curated map of
    skill -> certification/project suggestions.
  - `ranking.py` — `Final Score = match_score + salary_score + company_score + remote_bonus +
    preference_bonus`, used to sort job listings.
  - `tailoring_engine.py` — LLM-generated (via `llm.py`) tailored summary/bullets/keywords/
    improvements for a specific job, with a template-based fallback; results are stored in
    `tailoring_suggestions` and never overwrite the original resume.
  - `skills_taxonomy.py` — the flat, profession-spanning keyword list shared by the ATS,
    matching, and gap engines. Extraction is word-boundary-aware (not naive substring
    matching) to avoid false positives like "java" matching inside "javascript".
- **`tasks/scheduler.py`** — APScheduler background job that re-runs aggregation on an
  interval (`ENABLE_SCHEDULER` / `SCHEDULER_INTERVAL_HOURS`).

## Frontend (`frontend/src`)

- **`lib/api.ts`** — typed fetch client against the backend, one function per endpoint.
- **`lib/types.ts`** — TypeScript types mirroring the backend Pydantic schemas.
- **`app/*`** — one route per feature: `resume`, `profile`, `preferences`, `jobs` (list +
  `[id]` detail), `applications`, `dashboard`.

## Data model notes

- Single-user for v1: `profiles` and `preferences` are singleton tables (first row wins),
  no `user_id` scoping. Multi-user support would mean adding an auth layer and a `user_id`
  foreign key across these tables — deliberately deferred.
- `analytics` is computed on read from `jobs` + `applications` (dashboard endpoints) rather
  than maintained as a separate table, so it's always consistent with current data.
- `job_skills` is populated automatically at scrape time by running the skills taxonomy over
  each job's requirements (-> `required`) and description (-> `preferred`) text.

## Why ATS APIs only (not Indeed/LinkedIn/etc.) in v1

Greenhouse, Lever, Ashby, SmartRecruiters, and Workable expose public or semi-public JSON job
feeds intended for embedding job boards, so no scraping/ToS risk. Indeed, Naukri, Google Jobs,
and LinkedIn-adjacent boards actively block scraping or require paid partner APIs — adding them
is possible within the same `BaseScraper` interface, but was out of scope for this version.
