from datetime import datetime, timezone

import httpx

from app.services.scrapers.base import BaseScraper, JobRecord, html_to_text

POSTINGS_API = "https://api.lever.co/v0/postings/{company}"


class LeverScraper(BaseScraper):
    source_name = "lever"

    def __init__(self, companies: list[str]):
        self.companies = companies

    def discover_jobs(self) -> list[dict]:
        references = []
        for company in self.companies:
            resp = httpx.get(POSTINGS_API.format(company=company), params={"mode": "json"}, timeout=15)
            if resp.status_code != 200:
                continue
            data = resp.json()
            if not isinstance(data, list):
                continue
            for posting in data:
                references.append({"company": company, "posting": posting})
        return references

    def extract_job(self, reference: dict) -> dict:
        return reference

    def normalize_job(self, raw: dict) -> JobRecord:
        posting = raw["posting"]
        categories = posting.get("categories", {}) or {}
        location = categories.get("location")
        remote = bool(
            posting.get("workplaceType") == "remote"
            or (location and "remote" in location.lower())
        )

        description = html_to_text(posting.get("description") or posting.get("descriptionPlain"))
        requirement_lists = [
            html_to_text(item.get("content"))
            for item in posting.get("lists", [])
            if "requirement" in (item.get("text") or "").lower()
        ]

        return JobRecord(
            company=raw["company"],
            title=posting.get("text", ""),
            description=description,
            requirements=" ".join(requirement_lists),
            location=location,
            country=None,
            remote=remote,
            salary_min=None,
            salary_max=None,
            currency=None,
            employment_type=categories.get("commitment"),
            experience_required=None,
            source=self.source_name,
            url=posting.get("hostedUrl", ""),
            posted_date=_parse_epoch_ms(posting.get("createdAt")),
        )


def _parse_epoch_ms(value) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (ValueError, TypeError):
        return None
