from datetime import datetime

import httpx

from app.services.scrapers.base import BaseScraper, JobRecord, html_to_text

BOARD_API = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs"


class GreenhouseScraper(BaseScraper):
    source_name = "greenhouse"

    def __init__(self, board_tokens: list[str]):
        self.board_tokens = board_tokens

    def discover_jobs(self) -> list[dict]:
        references = []
        for board in self.board_tokens:
            resp = httpx.get(BOARD_API.format(board=board), params={"content": "true"}, timeout=15)
            if resp.status_code != 200:
                continue
            for job in resp.json().get("jobs", []):
                references.append({"board": board, "job": job})
        return references

    def extract_job(self, reference: dict) -> dict:
        return reference

    def normalize_job(self, raw: dict) -> JobRecord:
        job = raw["job"]
        location_name = (job.get("location") or {}).get("name")
        remote = bool(location_name and "remote" in location_name.lower())

        return JobRecord(
            company=job.get("company_name") or raw["board"],
            title=job.get("title", ""),
            description=html_to_text(job.get("content")),
            requirements="",
            location=location_name,
            country=None,
            remote=remote,
            salary_min=None,
            salary_max=None,
            currency=None,
            employment_type=None,
            experience_required=None,
            source=self.source_name,
            url=job.get("absolute_url", ""),
            posted_date=_parse_date(job.get("first_published")),
        )


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
