from app.db.models import Job, JobSkill, Preference, Profile
from app.services.matching_engine import compute_match


def _job(db, **overrides):
    defaults = dict(
        company_name="Acme",
        title="Backend Engineer",
        description="",
        requirements="",
        location="New York",
        country="us",
        remote=False,
        salary_min=100_000,
        salary_max=150_000,
        currency="USD",
        employment_type="full_time",
        experience_required="3+ years",
        source="greenhouse",
        url="https://example.com/job",
        posted_date=None,
        dedup_hash="hash1",
    )
    defaults.update(overrides)
    job = Job(**defaults)
    db.add(job)
    db.flush()
    return job


def test_full_skill_overlap_scores_highly(db_session):
    profile = Profile(skills=["python", "sql"], total_experience_years=5, domain_expertise=[])
    job = _job(db_session)
    db_session.add(JobSkill(job_id=job.id, skill="python", kind="required"))
    db_session.add(JobSkill(job_id=job.id, skill="sql", kind="required"))
    db_session.flush()
    db_session.refresh(job)

    result = compute_match(profile, None, job)

    assert result["components"]["skill_match"] == 100.0
    assert result["match_score"] > 50


def test_no_skill_overlap_scores_low(db_session):
    profile = Profile(skills=["excel"], total_experience_years=5, domain_expertise=[])
    job = _job(db_session, dedup_hash="hash2")
    db_session.add(JobSkill(job_id=job.id, skill="python", kind="required"))
    db_session.add(JobSkill(job_id=job.id, skill="kubernetes", kind="required"))
    db_session.flush()
    db_session.refresh(job)

    result = compute_match(profile, None, job)

    assert result["components"]["skill_match"] == 0.0


def test_remote_only_preference_rejects_onsite_job(db_session):
    profile = Profile(skills=[], total_experience_years=None, domain_expertise=[])
    preference = Preference(remote_only=True)
    job = _job(db_session, dedup_hash="hash3", remote=False)
    db_session.flush()
    db_session.refresh(job)

    result = compute_match(profile, preference, job)

    assert result["components"]["location_match"] == 0.0


def test_salary_out_of_range_scores_zero(db_session):
    profile = Profile(skills=[], total_experience_years=None, domain_expertise=[])
    preference = Preference(min_salary=200_000, max_salary=300_000)
    job = _job(db_session, dedup_hash="hash4", salary_min=100_000, salary_max=150_000)
    db_session.flush()
    db_session.refresh(job)

    result = compute_match(profile, preference, job)

    assert result["components"]["salary_match"] == 0.0
