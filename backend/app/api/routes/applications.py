from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.base import get_db
from app.db.models import Application, ApplicationStatus
from app.schemas.application import ApplicationCreate, ApplicationOut, ApplicationUpdate
from app.services.logging_service import log_event

router = APIRouter(prefix="/applications", tags=["applications"])

VALID_STATUSES = {s.value for s in ApplicationStatus}


@router.get("", response_model=list[ApplicationOut])
def list_applications(status: str | None = None, db: Session = Depends(get_db)) -> list[Application]:
    query = db.query(Application).options(joinedload(Application.job))
    if status:
        query = query.filter(Application.status == status)
    return query.order_by(Application.updated_at.desc()).all()


@router.post("", response_model=ApplicationOut)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)) -> Application:
    if payload.status not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status. Must be one of {sorted(VALID_STATUSES)}")

    existing = db.query(Application).filter(Application.job_id == payload.job_id).first()
    if existing:
        raise HTTPException(409, "An application for this job already exists")

    application = Application(
        job_id=payload.job_id,
        status=payload.status,
        notes=payload.notes,
        timeline=[{"status": payload.status, "at": datetime.now(timezone.utc).isoformat()}],
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    log_event(db, "application", f"Application created for job {payload.job_id} with status {payload.status}")
    return application


@router.patch("/{application_id}", response_model=ApplicationOut)
def update_application(application_id: str, payload: ApplicationUpdate, db: Session = Depends(get_db)) -> Application:
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(404, "Application not found")

    if payload.status is not None:
        if payload.status not in VALID_STATUSES:
            raise HTTPException(400, f"Invalid status. Must be one of {sorted(VALID_STATUSES)}")
        if payload.status != application.status:
            application.status = payload.status
            application.timeline = [
                *application.timeline,
                {"status": payload.status, "at": datetime.now(timezone.utc).isoformat()},
            ]

    if payload.notes is not None:
        application.notes = payload.notes

    db.commit()
    db.refresh(application)
    log_event(db, "application", f"Application {application_id} updated")
    return application


@router.delete("/{application_id}")
def delete_application(application_id: str, db: Session = Depends(get_db)) -> dict:
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(404, "Application not found")
    db.delete(application)
    db.commit()
    return {"deleted": True}
