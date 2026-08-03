from app.db.models import Company, Job, Preference
from app.services.ranking import compute_final_score


def test_remote_bonus_applied_for_remote_job(db_session):
    job = Job(
        company_name="Acme",
        title="Engineer",
        description="",
        requirements="",
        location=None,
        country=None,
        remote=True,
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
    db_session.add(job)
    db_session.flush()

    result = compute_final_score(match_score=50.0, preference=None, job=job)

    assert result["remote_bonus"] > 0
    assert result["final_score"] == 50.0 + result["salary_score"] + result["company_score"] + result["remote_bonus"] + result["preference_bonus"]


def test_higher_salary_increases_salary_score(db_session):
    low = Job(
        company_name="Acme", title="Engineer", description="", requirements="",
        location=None, country=None, remote=False, salary_min=None, salary_max=80_000,
        currency=None, employment_type=None, experience_required=None,
        source="greenhouse", url="https://example.com/1", posted_date=None, dedup_hash="hash-low",
    )
    high = Job(
        company_name="Acme", title="Engineer", description="", requirements="",
        location=None, country=None, remote=False, salary_min=None, salary_max=250_000,
        currency=None, employment_type=None, experience_required=None,
        source="greenhouse", url="https://example.com/2", posted_date=None, dedup_hash="hash-high",
    )
    db_session.add_all([low, high])
    db_session.flush()

    low_score = compute_final_score(50.0, None, low)["salary_score"]
    high_score = compute_final_score(50.0, None, high)["salary_score"]

    assert high_score > low_score


def test_company_reputation_increases_company_score(db_session):
    company = Company(name="GoodCo", company_rating=9, tech_reputation=8, engineering_reputation=9)
    db_session.add(company)
    db_session.flush()

    job = Job(
        company_id=company.id, company_name="GoodCo", title="Engineer", description="", requirements="",
        location=None, country=None, remote=False, salary_min=None, salary_max=None,
        currency=None, employment_type=None, experience_required=None,
        source="greenhouse", url="https://example.com/3", posted_date=None, dedup_hash="hash-co",
    )
    db_session.add(job)
    db_session.flush()
    db_session.refresh(job)

    result = compute_final_score(50.0, None, job)

    assert result["company_score"] > 0
