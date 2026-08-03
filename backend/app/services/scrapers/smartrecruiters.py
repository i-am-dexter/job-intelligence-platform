from datetime import datetime

import httpx

from app.services.scrapers.base import BaseScraper, JobRecord, html_to_text

POSTINGS_API = "https://api.smartrecruiters.com/v1/companies/{company}/postings"
POSTING_DETAIL_API = "https://api.smartrecruiters.com/v1/companies/{company}/postings/{posting_id}"


class SmartRecruitersScraper(BaseScraper):
    source_name = "smartrecruiters"

    def __init__(self, companies: list[str]):
        self.companies = companies

    def discover_jobs(self) -> list[dict]:
        references = []
        for company in self.companies:
            resp = httpx.get(POSTINGS_API.format(company=company), timeout=15)
            if resp.status_code != 200:
                continue
            for posting in resp.json().get("content", []):
                references.append({"company": company, "posting_id": posting["id"]})
        return references

    def extract_job(self, reference: dict) -> dict:
        resp = httpx.get(
            POSTING_DETAIL_API.format(company=reference["company"], posting_id=reference["posting_id"]),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def normalize_job(self, raw: dict) -> JobRecord:
        sections = (raw.get("jobAd") or {}).get("sections", {})
        description = html_to_text(sections.get("jobDescription", {}).get("text"))
        requirements = html_to_text(sections.get("qualifications", {}).get("text"))

        location = raw.get("location", {}) or {}
        location_str = location.get("fullLocation") or location.get("city")
        employment = (raw.get("typeOfEmployment") or {}).get("label")
        experience = (raw.get("experienceLevel") or {}).get("label")

        return JobRecord(
            company=(raw.get("company") or {}).get("name", ""),
            title=raw.get("name", ""),
            description=description,
            requirements=requirements,
            location=location_str,
            country=location.get("country"),
            remote=bool(location.get("remote")),
            salary_min=None,
            salary_max=None,
            currency=None,
            employment_type=employment,
            experience_required=experience,
            source=self.source_name,
            url=raw.get("postingUrl", ""),
            posted_date=_parse_date(raw.get("releasedDate")),
        )


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
