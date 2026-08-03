from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import applications, ats, dashboard, gaps, jobs, preferences, profile, resume, tailoring
from app.core.config import get_settings
from app.tasks.scheduler import start_scheduler, stop_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.enable_scheduler:
        start_scheduler(settings.scheduler_interval_hours)
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_name, version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router)
app.include_router(profile.router)
app.include_router(preferences.router)
app.include_router(jobs.router)
app.include_router(ats.router)
app.include_router(gaps.router)
app.include_router(tailoring.router)
app.include_router(applications.router)
app.include_router(dashboard.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
