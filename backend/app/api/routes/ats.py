from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Job, Profile
from app.schemas.analysis import ATSResult
from app.services.ats_engine import analyze_ats

router = APIRouter(prefix="/jobs/{job_id}/ats", tags=["ats"])


@router.get("", response_model=ATSResult)
def get_ats_analysis(job_id: str, db: Session = Depends(get_db)) -> ATSResult:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(400, "Upload a resume first to run ATS analysis")
    return analyze_ats(profile, job)
