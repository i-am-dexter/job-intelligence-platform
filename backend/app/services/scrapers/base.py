import html
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Company, Job, JobSkill
from app.services.dedup import compute_dedup_hash
from app.services.logging_service import log_event
from app.services.skills_taxonomy import extract_skills_from_text

_TAG_RE = re.compile(r"<[^>]+>")


def html_to_text(raw_html: str | None) -> str:
    """Unescape HTML entities and strip tags, for job descriptions delivered as HTML."""
    if not raw_html:
        return ""
    unescaped = html.unescape(raw_html)
    # Some ATS APIs (e.g. Greenhouse) double-escape entities.
    unescaped = html.unescape(unescaped)
    no_tags = _TAG_RE.sub(" ", unescaped)
    return re.sub(r"\s+", " ", no_tags).strip()


@dataclass
class JobRecord:
    """Normalized job schema every scraper must produce."""

    company: str
    title: str
    description: str
    requirements: str
    location: str | None
    country: str | None
    remote: bool
    salary_min: float | None
    salary_max: float | None
    currency: str | None
    employment_type: str | None
    experience_required: str | None
    source: str
    url: str
    posted_date: datetime | None


class BaseScraper(ABC):
    """Every scraper implements this pipeline: discover -> extract -> normalize -> validate -> store."""

    source_name: str

    @abstractmethod
    def discover_jobs(self) -> list[dict]:
        """Return a list of lightweight references (e.g. job id/url) to fetch."""

    @abstractmethod
    def extract_job(self, reference: dict) -> dict:
        """Fetch the raw job payload for one discovered reference."""

    @abstractmethod
    def normalize_job(self, raw: dict) -> JobRecord:
        """Map a raw payload into the shared JobRecord schema."""

    def validate_job(self, record: JobRecord) -> bool:
        return bool(record.company and record.title and record.url)

    def store_job(self, db: Session, record: JobRecord) -> Job | None:
        if not self.validate_job(record):
            return None

        dedup_hash = compute_dedup_hash(record.company, record.title, record.location)
        existing = db.query(Job).filter(Job.dedup_hash == dedup_hash).first()
        if existing:
            return None

        company = db.query(Company).filter(Company.name == record.company).first()
        if not company:
            company = Company(name=record.company)
            db.add(company)
            db.flush()

        job = Job(
            company_id=company.id,
            company_name=record.company,
            title=record.title,
            description=record.description,
            requirements=record.requirements,
            location=record.location,
            country=record.country,
            remote=record.remote,
            salary_min=record.salary_min,
            salary_max=record.salary_max,
            currency=record.currency,
            employment_type=record.employment_type,
            experience_required=record.experience_required,
            source=record.source,
            url=record.url,
            posted_date=record.posted_date,
            dedup_hash=dedup_hash,
        )
        db.add(job)
        try:
            db.flush()
        except IntegrityError:
            # Two references in the same batch normalized to the same dedup_hash.
            db.rollback()
            return None

        self._tag_skills(db, job, record)

        db.commit()
        db.refresh(job)
        return job

    def _tag_skills(self, db: Session, job: Job, record: JobRecord) -> None:
        required = set(extract_skills_from_text(record.requirements))
        preferred = set(extract_skills_from_text(record.description)) - required
        for skill in required:
            db.add(JobSkill(job_id=job.id, skill=skill, kind="required"))
        for skill in preferred:
            db.add(JobSkill(job_id=job.id, skill=skill, kind="preferred"))

    def run(self, db: Session) -> int:
        stored = 0
        try:
            references = self.discover_jobs()
        except Exception as exc:
            log_event(db, "scraper", f"{self.source_name} discover_jobs failed: {exc}")
            return 0

        for reference in references:
            try:
                raw = self.extract_job(reference)
                record = self.normalize_job(raw)
                job = self.store_job(db, record)
                if job:
                    stored += 1
            except Exception as exc:
                db.rollback()
                log_event(db, "scraper", f"{self.source_name} failed on {reference}: {exc}")

        log_event(db, "scraper", f"{self.source_name} stored {stored} new jobs")
        return stored
