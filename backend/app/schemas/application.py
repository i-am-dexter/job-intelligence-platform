from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.job import JobOut


class ApplicationCreate(BaseModel):
    job_id: str
    status: str = "Saved"
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    status: str
    notes: str | None
    timeline: list = []
    created_at: datetime
    updated_at: datetime
    job: JobOut | None = None
