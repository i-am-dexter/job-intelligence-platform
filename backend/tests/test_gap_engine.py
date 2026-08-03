from app.db.models import Job, JobSkill, Profile
from app.services.gap_engine import analyze_gaps


def _job(db, dedup_hash="hash1"):
    job = Job(
        company_name="Acme",
        title="DevOps Engineer",
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
        dedup_hash=dedup_hash,
    )
    db.add(job)
    db.flush()
    return job


def test_matched_and_missing_skills(db_session):
    profile = Profile(skills=["aws", "docker"])
    job = _job(db_session)
    db_session.add(JobSkill(job_id=job.id, skill="aws", kind="required"))
    db_session.add(JobSkill(job_id=job.id, skill="kubernetes", kind="required"))
    db_session.add(JobSkill(job_id=job.id, skill="terraform", kind="preferred"))
    db_session.flush()
    db_session.refresh(job)

    result = analyze_gaps(profile, job)

    assert "aws" in result.matched_skills
    assert "kubernetes" in result.missing_skills
    assert "terraform" in result.missing_skills
    # only required-and-missing skills drive learning priorities
    assert "kubernetes" in result.learning_priorities
    assert "terraform" not in result.learning_priorities


def test_certification_recommendations_for_known_skill(db_session):
    profile = Profile(skills=[])
    job = _job(db_session, dedup_hash="hash2")
    db_session.add(JobSkill(job_id=job.id, skill="aws", kind="required"))
    db_session.flush()
    db_session.refresh(job)

    result = analyze_gaps(profile, job)

    assert any("AWS" in cert for cert in result.recommended_certifications)
