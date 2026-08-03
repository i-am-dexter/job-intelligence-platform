import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.base import get_db
from app.db.models import Profile, ResumeVersion
from app.schemas.resume import ResumeUploadResult, ResumeVersionOut
from app.services.logging_service import log_event
from app.services.resume_parser import extract_text, parse_resume_to_profile

router = APIRouter(prefix="/resume", tags=["resume"])

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/upload", response_model=ResumeUploadResult)
def upload_resume(file: UploadFile, db: Session = Depends(get_db)) -> ResumeUploadResult:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Supported: PDF, DOCX.")

    settings = get_settings()
    storage_dir = Path(settings.resume_storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid.uuid4()}{ext}"
    file_path = storage_dir / stored_name
    with file_path.open("wb") as f:
        f.write(file.file.read())

    try:
        text = extract_text(str(file_path))
    except Exception as exc:
        log_event(db, "error", f"Resume parse failed for {file.filename}: {exc}")
        raise HTTPException(422, f"Could not parse resume: {exc}") from exc

    extracted = parse_resume_to_profile(text)

    resume_version = ResumeVersion(
        filename=file.filename or stored_name,
        file_path=str(file_path),
        parsed_text=text,
        extracted_profile_snapshot=extracted,
    )
    db.add(resume_version)

    profile = db.query(Profile).first()
    if not profile:
        profile = Profile()
        db.add(profile)

    for field, value in extracted.items():
        if hasattr(profile, field) and value not in (None, [], ""):
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    db.refresh(resume_version)

    log_event(db, "application", f"Resume uploaded and profile updated from {resume_version.filename}")

    return ResumeUploadResult(
        resume_version=ResumeVersionOut.model_validate(resume_version),
        profile=profile,
    )


@router.get("/versions", response_model=list[ResumeVersionOut])
def list_resume_versions(db: Session = Depends(get_db)) -> list[ResumeVersion]:
    return db.query(ResumeVersion).order_by(ResumeVersion.uploaded_at.desc()).all()
