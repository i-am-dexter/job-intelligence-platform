from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.profile import ProfileOut


class ResumeVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    uploaded_at: datetime


class ResumeUploadResult(BaseModel):
    resume_version: ResumeVersionOut
    profile: ProfileOut
