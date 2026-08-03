from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobSkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill: str
    kind: str


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_name: str
    title: str
    description: str | None
    requirements: str | None
    location: str | None
    country: str | None
    remote: bool
    salary_min: float | None
    salary_max: float | None
    currency: str | None
    salary_confidence: str | None
    employment_type: str | None
    experience_required: str | None
    source: str
    url: str
    posted_date: datetime | None
    created_at: datetime
    skills: list[JobSkillOut] = []


class RankedJobOut(JobOut):
    match_score: float
    salary_score: float
    company_score: float
    remote_bonus: float
    preference_bonus: float
    final_score: float


class JobFilters(BaseModel):
    keyword: str | None = None
    source: str | None = None
    company: str | None = None
    location: str | None = None
    country: str | None = None
    min_salary: float | None = None
    remote: bool | None = None
    min_score: float | None = None
    industry: str | None = None
    experience_required: str | None = None
    employment_type: str | None = None
