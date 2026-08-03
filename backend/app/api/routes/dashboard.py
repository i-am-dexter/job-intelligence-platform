from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Application, ApplicationStatus, Company, Job, Preference, Profile, SavedJob
from app.schemas.dashboard import AnalyticsSummary, DashboardMetrics
from app.services.matching_engine import compute_match

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

STRONG_THRESHOLD = 75
MEDIUM_THRESHOLD = 50


def _match_buckets(db: Session) -> tuple[int, int, int]:
    profile = db.query(Profile).first()
    if not profile:
        return 0, 0, 0
    preference = db.query(Preference).first()

    strong = medium = weak = 0
    for job in db.query(Job).all():
        score = compute_match(profile, preference, job)["match_score"]
        if score >= STRONG_THRESHOLD:
            strong += 1
        elif score >= MEDIUM_THRESHOLD:
            medium += 1
        else:
            weak += 1
    return strong, medium, weak


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(db: Session = Depends(get_db)) -> DashboardMetrics:
    strong, medium, weak = _match_buckets(db)

    total_jobs = db.query(Job).count()
    applications = db.query(Application).count()
    interviews = db.query(Application).filter(Application.status == ApplicationStatus.interviewing.value).count()
    offers = db.query(Application).filter(Application.status == ApplicationStatus.offer.value).count()
    saved = db.query(SavedJob).count()
    companies = db.query(Company).count()
    sources = db.query(Job.source).distinct().count()

    return DashboardMetrics(
        total_jobs=total_jobs,
        strong_matches=strong,
        medium_matches=medium,
        weak_matches=weak,
        applications=applications,
        interviews=interviews,
        offers=offers,
        saved_jobs=saved,
        companies=companies,
        sources=sources,
    )


@router.get("/analytics", response_model=AnalyticsSummary)
def get_analytics(db: Session = Depends(get_db)) -> AnalyticsSummary:
    applications = db.query(Application).all()
    total = len(applications)
    interviewed = sum(1 for a in applications if a.status in {ApplicationStatus.interviewing.value, ApplicationStatus.offer.value})
    offered = sum(1 for a in applications if a.status == ApplicationStatus.offer.value)

    interview_rate = round(100 * interviewed / total, 1) if total else 0.0
    offer_rate = round(100 * offered / total, 1) if total else 0.0
    success_rate = offer_rate

    source_counts: dict[str, int] = {}
    source_applied: dict[str, int] = {}
    for application in applications:
        if not application.job:
            continue
        source_counts[application.job.source] = source_counts.get(application.job.source, 0) + 1
        if application.status in {ApplicationStatus.interviewing.value, ApplicationStatus.offer.value}:
            source_applied[application.job.source] = source_applied.get(application.job.source, 0) + 1

    source_effectiveness = {
        source: round(100 * source_applied.get(source, 0) / count, 1) for source, count in source_counts.items()
    }

    profile = db.query(Profile).first()
    top_matching_domains = profile.domain_expertise[:5] if profile else []

    top_paying = (
        db.query(Job)
        .filter(Job.salary_max.isnot(None))
        .order_by(Job.salary_max.desc())
        .limit(5)
        .all()
    )
    top_paying_roles = [
        {"title": job.title, "company": job.company_name, "salary_max": job.salary_max, "currency": job.currency}
        for job in top_paying
    ]

    return AnalyticsSummary(
        application_success_rate=success_rate,
        interview_rate=interview_rate,
        offer_rate=offer_rate,
        source_effectiveness=source_effectiveness,
        top_matching_domains=top_matching_domains,
        top_paying_roles=top_paying_roles,
    )
