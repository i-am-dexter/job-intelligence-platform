from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_jobs: int
    strong_matches: int
    medium_matches: int
    weak_matches: int
    applications: int
    interviews: int
    offers: int
    saved_jobs: int
    companies: int
    sources: int


class AnalyticsSummary(BaseModel):
    application_success_rate: float
    interview_rate: float
    offer_rate: float
    source_effectiveness: dict[str, float]
    top_matching_domains: list[str]
    top_paying_roles: list[dict]
