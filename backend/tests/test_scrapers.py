from datetime import datetime, timezone

import httpx

from app.db.models import Job
from app.services.scrapers.base import BaseScraper, JobRecord
from app.services.scrapers.greenhouse import GreenhouseScraper


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def _job_record(dedup_seed="acme-engineer-remote", **overrides):
    defaults = dict(
        company="Acme",
        title="Engineer",
        description="desc",
        requirements="reqs",
        location="Remote",
        country=None,
        remote=True,
        salary_min=None,
        salary_max=None,
        currency=None,
        employment_type=None,
        experience_required=None,
        source="testsource",
        url=f"https://example.com/{dedup_seed}",
        posted_date=None,
    )
    defaults.update(overrides)
    return JobRecord(**defaults)


class _DummyScraper(BaseScraper):
    source_name = "testsource"

    def discover_jobs(self):
        return []

    def extract_job(self, reference):
        return reference

    def normalize_job(self, raw):
        return raw["record"]


def test_greenhouse_normalize_job_maps_fields():
    scraper = GreenhouseScraper(board_tokens=["acme"])
    raw = {
        "board": "acme",
        "job": {
            "company_name": "Acme",
            "title": "Software Engineer",
            "content": "&lt;p&gt;Build things&lt;/p&gt;",
            "location": {"name": "Remote - US"},
            "absolute_url": "https://acme.com/jobs/123",
            "first_published": "2026-01-01T00:00:00-05:00",
        },
    }

    record = scraper.normalize_job(raw)

    assert record.company == "Acme"
    assert record.title == "Software Engineer"
    assert record.description == "Build things"
    assert record.remote is True
    assert record.url == "https://acme.com/jobs/123"


def test_greenhouse_discover_jobs_uses_httpx(monkeypatch):
    scraper = GreenhouseScraper(board_tokens=["acme"])

    def fake_get(url, params=None, timeout=None):
        return _FakeResponse(200, {"jobs": [{"id": 1, "title": "Engineer"}]})

    monkeypatch.setattr(httpx, "get", fake_get)

    references = scraper.discover_jobs()

    assert len(references) == 1
    assert references[0]["board"] == "acme"


def test_store_job_dedups_identical_jobs(db_session):
    scraper = _DummyScraper()
    record = _job_record()

    first = scraper.store_job(db_session, record)
    second = scraper.store_job(db_session, record)

    assert first is not None
    assert second is None
    assert db_session.query(Job).count() == 1


def test_run_recovers_after_duplicate_in_same_batch(db_session):
    scraper = _DummyScraper()
    record = _job_record()
    # Two references that normalize to the exact same dedup hash within one run() call.
    distinct_record = _job_record(dedup_seed="other", title="Different Role")
    references = [{"record": record}, {"record": record}, {"record": distinct_record}]

    def discover():
        return references

    scraper.discover_jobs = discover
    stored_count = scraper.run(db_session)

    assert stored_count == 2  # first duplicate stored, the repeat skipped, the distinct one stored
    assert db_session.query(Job).count() == 2


def test_run_continues_after_extract_failure(db_session):
    scraper = _DummyScraper()
    good_record = _job_record()

    def flaky_extract(reference):
        if reference.get("fail"):
            raise RuntimeError("network error")
        return reference

    scraper.discover_jobs = lambda: [{"fail": True}, {"record": good_record}]
    scraper.extract_job = flaky_extract

    stored_count = scraper.run(db_session)

    assert stored_count == 1
    assert db_session.query(Job).count() == 1
