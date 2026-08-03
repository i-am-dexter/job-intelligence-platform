from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    portfolio: str | None = None
    experience: list = []
    education: list = []
    skills: list[str] = []
    certifications: list[str] = []
    projects: list = []
    technologies: list[str] = []
    domain_expertise: list[str] = []
    preferred_roles: list[str] = []
    preferred_locations: list[str] = []
    total_experience_years: float | None = None


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
