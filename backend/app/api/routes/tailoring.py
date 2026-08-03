from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Job, Profile, ResumeVersion, TailoringSuggestion
from app.schemas.analysis import TailoringResult
from app.services.tailoring_engine import generate_tailoring

router = APIRouter(prefix="/jobs/{job_id}/tailoring", tags=["tailoring"])


@router.get("", response_model=TailoringResult | None)
def get_latest_tailoring(job_id: str, db: Session = Depends(get_db)) -> TailoringResult | None:
    suggestion = (
        db.query(TailoringSuggestion)
        .filter(TailoringSuggestion.job_id == job_id)
        .order_by(TailoringSuggestion.created_at.desc())
        .first()
    )
    if not suggestion:
        return None
    return TailoringResult(
        tailored_summary=suggestion.tailored_summary or "",
        tailored_bullets=suggestion.tailored_bullets,
        keyword_suggestions=suggestion.keyword_suggestions,
        project_recommendations=suggestion.project_recommendations,
        resume_improvements=suggestion.resume_improvements,
    )


@router.post("", response_model=TailoringResult)
def generate_tailoring_suggestion(job_id: str, db: Session = Depends(get_db)) -> TailoringResult:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(400, "Upload a resume first to generate tailoring suggestions")

    result = generate_tailoring(profile, job)

    latest_resume = db.query(ResumeVersion).order_by(ResumeVersion.uploaded_at.desc()).first()
    db.add(
        TailoringSuggestion(
            job_id=job_id,
            resume_version_id=latest_resume.id if latest_resume else None,
            tailored_summary=result.tailored_summary,
            tailored_bullets=result.tailored_bullets,
            keyword_suggestions=result.keyword_suggestions,
            project_recommendations=result.project_recommendations,
            resume_improvements=result.resume_improvements,
        )
    )
    db.commit()

    return result
