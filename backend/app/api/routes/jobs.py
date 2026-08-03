from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Job, Preference, Profile, SavedJob
from app.schemas.job import JobFilters, JobOut, RankedJobOut
from app.services.matching_engine import compute_match
from app.services.ranking import compute_final_score
from app.services.scrapers.registry import run_all_scrapers

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _rank_job(job: Job, profile: Profile | None, preference: Preference | None) -> RankedJobOut:
    if profile:
        match = compute_match(profile, preference, job)
        scores = compute_final_score(match["match_score"], preference, job)
    else:
        match = {"match_score": 0.0}
        scores = {"salary_score": 0.0, "company_score": 0.0, "remote_bonus": 0.0, "preference_bonus": 0.0, "final_score": 0.0}

    return RankedJobOut(
        **JobOut.model_validate(job).model_dump(),
        match_score=match["match_score"],
        salary_score=scores["salary_score"],
        company_score=scores["company_score"],
        remote_bonus=scores["remote_bonus"],
        preference_bonus=scores["preference_bonus"],
        final_score=scores["final_score"],
    )


@router.post("/aggregate")
def aggregate_jobs(db: Session = Depends(get_db)) -> dict:
    results = run_all_scrapers(db)
    return {"stored_by_source": results, "total_stored": sum(results.values())}


@router.get("", response_model=list[RankedJobOut])
def list_jobs(
    keyword: str | None = None,
    source: str | None = None,
    company: str | None = None,
    location: str | None = None,
    country: str | None = None,
    min_salary: float | None = None,
    remote: bool | None = None,
    min_score: float | None = None,
    employment_type: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[RankedJobOut]:
    filters = JobFilters(
        keyword=keyword,
        source=source,
        company=company,
        location=location,
        country=country,
        min_salary=min_salary,
        remote=remote,
        min_score=min_score,
        employment_type=employment_type,
    )

    query = db.query(Job)
    if filters.keyword:
        like = f"%{filters.keyword}%"
        query = query.filter((Job.title.ilike(like)) | (Job.description.ilike(like)))
    if filters.source:
        query = query.filter(Job.source == filters.source)
    if filters.company:
        query = query.filter(Job.company_name.ilike(f"%{filters.company}%"))
    if filters.location:
        query = query.filter(Job.location.ilike(f"%{filters.location}%"))
    if filters.country:
        query = query.filter(Job.country == filters.country)
    if filters.min_salary is not None:
        query = query.filter(Job.salary_max >= filters.min_salary)
    if filters.remote is not None:
        query = query.filter(Job.remote == filters.remote)
    if filters.employment_type:
        query = query.filter(Job.employment_type == filters.employment_type)

    jobs = query.order_by(Job.created_at.desc()).limit(limit).all()

    profile = db.query(Profile).first()
    preference = db.query(Preference).first()

    ranked = [_rank_job(job, profile, preference) for job in jobs]
    if filters.min_score is not None:
        ranked = [j for j in ranked if j.match_score >= filters.min_score]

    ranked.sort(key=lambda j: j.final_score, reverse=True)
    return ranked


@router.get("/saved/list", response_model=list[RankedJobOut])
def list_saved_jobs(db: Session = Depends(get_db)) -> list[RankedJobOut]:
    profile = db.query(Profile).first()
    preference = db.query(Preference).first()
    saved = db.query(SavedJob).all()
    return [_rank_job(s.job, profile, preference) for s in saved]


@router.get("/{job_id}", response_model=RankedJobOut)
def get_job(job_id: str, db: Session = Depends(get_db)) -> RankedJobOut:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    profile = db.query(Profile).first()
    preference = db.query(Preference).first()
    return _rank_job(job, profile, preference)


@router.post("/{job_id}/save")
def save_job(job_id: str, db: Session = Depends(get_db)) -> dict:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if not db.query(SavedJob).filter(SavedJob.job_id == job_id).first():
        db.add(SavedJob(job_id=job_id))
        db.commit()
    return {"saved": True}


@router.delete("/{job_id}/save")
def unsave_job(job_id: str, db: Session = Depends(get_db)) -> dict:
    saved = db.query(SavedJob).filter(SavedJob.job_id == job_id).first()
    if saved:
        db.delete(saved)
        db.commit()
    return {"saved": False}
