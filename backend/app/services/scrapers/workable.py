from datetime import datetime

import httpx

from app.services.scrapers.base import BaseScraper, JobRecord, html_to_text

WIDGET_API = "https://apply.workable.com/api/v1/widget/accounts/{account}"


class WorkableScraper(BaseScraper):
    source_name = "workable"

    def __init__(self, accounts: list[str]):
        self.accounts = accounts

    def discover_jobs(self) -> list[dict]:
        references = []
        for account in self.accounts:
            resp = httpx.get(WIDGET_API.format(account=account), params={"details": "true"}, timeout=15)
            if resp.status_code != 200:
                continue
            for job in resp.json().get("jobs", []):
                references.append({"account": account, "job": job})
        return references

    def extract_job(self, reference: dict) -> dict:
        return reference

    def normalize_job(self, raw: dict) -> JobRecord:
        job = raw["job"]
        location = job.get("location", {}) or {}
        location_str = location.get("location_str") or ", ".join(
            filter(None, [location.get("city"), location.get("region"), location.get("country")])
        )
        remote = bool(location.get("remote") or (location_str and "remote" in location_str.lower()))

        description = html_to_text(job.get("description"))

        return JobRecord(
            company=raw["account"],
            title=job.get("title", ""),
            description=description,
            requirements=html_to_text(job.get("requirements")),
            location=location_str,
            country=location.get("country"),
            remote=remote,
            salary_min=None,
            salary_max=None,
            currency=None,
            employment_type=job.get("employment_type"),
            experience_required=None,
            source=self.source_name,
            url=job.get("url", ""),
            posted_date=_parse_date(job.get("published_on")),
        )


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
