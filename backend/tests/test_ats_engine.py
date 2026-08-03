from app.db.models import Job, JobSkill, Profile
from app.services.ats_engine import analyze_ats


def _job_with_skills(db, required=None, preferred=None):
    job = Job(
        company_name="Acme",
        title="Backend Engineer",
        description="",
        requirements="",
        location=None,
        country=None,
        remote=False,
        salary_min=None,
        salary_max=None,
        currency=None,
        employment_type=None,
        experience_required=None,
        source="greenhouse",
        url="https://example.com/job",
        posted_date=None,
        dedup_hash="hash1",
    )
    db.add(job)
    db.flush()
    for skill in required or []:
        db.add(JobSkill(job_id=job.id, skill=skill, kind="required"))
    for skill in preferred or []:
        db.add(JobSkill(job_id=job.id, skill=skill, kind="preferred"))
    db.flush()
    db.refresh(job)
    return job


def test_full_keyword_coverage(db_session):
    profile = Profile(skills=["python", "sql"], technologies=[])
    job = _job_with_skills(db_session, required=["python", "sql"])

    result = analyze_ats(profile, job)

    assert result.ats_score == 100.0
    assert result.missing_keywords == []
    assert set(result.matched_keywords) == {"python", "sql"}


def test_missing_required_keywords_flagged(db_session):
    profile = Profile(skills=["python"], technologies=[])
    job = _job_with_skills(db_session, required=["python", "kubernetes"], preferred=["aws"])

    result = analyze_ats(profile, job)

    assert result.ats_score < 100
    assert "kubernetes" in result.missing_keywords
    assert any("kubernetes" in rec for rec in result.recommendations)


def test_no_tagged_skills_falls_back_to_text_extraction(db_session):
    profile = Profile(skills=["python"], technologies=[])
    job = Job(
        company_name="Acme",
        title="Backend Engineer",
        description="We need someone skilled in Python and Docker.",
        requirements="Docker required.",
        location=None,
        country=None,
        remote=False,
        salary_min=None,
        salary_max=None,
        currency=None,
        employment_type=None,
        experience_required=None,
        source="greenhouse",
        url="https://example.com/job",
        posted_date=None,
        dedup_hash="hash2",
    )
    db_session.add(job)
    db_session.flush()

    result = analyze_ats(profile, job)

    assert "docker" in result.missing_keywords
    assert "python" in result.matched_keywords
