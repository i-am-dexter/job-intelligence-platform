from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Job, Profile
from app.schemas.analysis import GapResult
from app.services.gap_engine import analyze_gaps

router = APIRouter(prefix="/jobs/{job_id}/gaps", tags=["gaps"])


@router.get("", response_model=GapResult)
def get_gap_analysis(job_id: str, db: Session = Depends(get_db)) -> GapResult:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    profile = db.query(Profile).first()
    if not profile:
        raise HTTPException(400, "Upload a resume first to run gap analysis")
    return analyze_gaps(profile, job)
