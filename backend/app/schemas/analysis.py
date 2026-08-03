from pydantic import BaseModel


class MatchComponents(BaseModel):
    skill_match: float
    experience_match: float
    preference_match: float
    domain_match: float
    location_match: float
    salary_match: float
    ats_match: float


class MatchResult(BaseModel):
    match_score: float
    components: MatchComponents


class ATSResult(BaseModel):
    ats_score: float
    keyword_coverage: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    recommendations: list[str]


class GapResult(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    suggested_skills: list[str]
    learning_priorities: list[str]
    recommended_certifications: list[str]
    recommended_projects: list[str]


class TailoringResult(BaseModel):
    tailored_summary: str
    tailored_bullets: list[str]
    keyword_suggestions: list[str]
    project_recommendations: list[str]
    resume_improvements: list[str]
