from datetime import datetime

import httpx

from app.services.scrapers.base import BaseScraper, JobRecord, html_to_text

JOB_BOARD_API = "https://api.ashbyhq.com/posting-api/job-board/{org}"


class AshbyScraper(BaseScraper):
    source_name = "ashby"

    def __init__(self, org_slugs: list[str]):
        self.org_slugs = org_slugs

    def discover_jobs(self) -> list[dict]:
        references = []
        for org in self.org_slugs:
            resp = httpx.get(JOB_BOARD_API.format(org=org), params={"includeCompensation": "true"}, timeout=15)
            if resp.status_code != 200:
                continue
            for job in resp.json().get("jobs", []):
                references.append({"org": org, "job": job})
        return references

    def extract_job(self, reference: dict) -> dict:
        return reference

    def normalize_job(self, raw: dict) -> JobRecord:
        job = raw["job"]

        return JobRecord(
            company=raw["org"],
            title=(job.get("title") or "").strip(),
            description=html_to_text(job.get("descriptionHtml")),
            requirements="",
            location=job.get("location"),
            country=None,
            remote=bool(job.get("isRemote")),
            salary_min=None,
            salary_max=None,
            currency=None,
            employment_type=job.get("employmentType"),
            experience_required=None,
            source=self.source_name,
            url=job.get("jobUrl", ""),
            posted_date=_parse_date(job.get("publishedAt")),
        )


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
