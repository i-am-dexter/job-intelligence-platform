from apscheduler.schedulers.background import BackgroundScheduler

from app.db.base import SessionLocal
from app.services.scrapers.registry import run_all_scrapers

_scheduler: BackgroundScheduler | None = None


def _run_aggregation_job() -> None:
    db = SessionLocal()
    try:
        run_all_scrapers(db)
    finally:
        db.close()


def start_scheduler(interval_hours: int = 6) -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(_run_aggregation_job, "interval", hours=interval_hours, id="job_aggregation")
    _scheduler.start()
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
