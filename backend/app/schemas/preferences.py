from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PreferenceBase(BaseModel):
    preferred_titles: list[str] = []
    preferred_locations: list[str] = []
    remote_only: bool = False
    hybrid_ok: bool = True
    onsite_ok: bool = True
    countries: list[str] = []
    min_salary: float | None = None
    max_salary: float | None = None
    salary_currency: str = "USD"
    employment_type: list[str] = []
    seniority: list[str] = []
    industries: list[str] = []
    company_size: list[str] = []


class PreferenceUpdate(PreferenceBase):
    pass


class PreferenceOut(PreferenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
