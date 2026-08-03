from app.db.models import Job, Preference


def _salary_score(job: Job) -> float:
    if job.salary_max:
        # Normalize against a $300k ceiling so the bonus stays within a sane range.
        return round(min(job.salary_max, 300_000) / 3000, 1)
    return 0.0


def _company_score(job: Job) -> float:
    if not job.company:
        return 0.0
    ratings = [
        r
        for r in [job.company.company_rating, job.company.tech_reputation, job.company.engineering_reputation]
        if r is not None
    ]
    return round(sum(ratings) / len(ratings) * 2, 1) if ratings else 0.0  # ratings assumed 0-10 -> up to 20 bonus


def _remote_bonus(preference: Preference | None, job: Job) -> float:
    if job.remote and (preference is None or preference.remote_only):
        return 10.0
    if job.remote:
        return 5.0
    return 0.0


def _preference_bonus(preference: Preference | None, job: Job) -> float:
    if preference is None:
        return 0.0
    bonus = 0.0
    if preference.preferred_titles and any(t.lower() in job.title.lower() for t in preference.preferred_titles):
        bonus += 5.0
    if preference.industries and job.company and job.company.industry:
        if job.company.industry.lower() in [i.lower() for i in preference.industries]:
            bonus += 5.0
    return bonus


def compute_final_score(match_score: float, preference: Preference | None, job: Job) -> dict:
    salary_score = _salary_score(job)
    company_score = _company_score(job)
    remote_bonus = _remote_bonus(preference, job)
    preference_bonus = _preference_bonus(preference, job)

    final_score = match_score + salary_score + company_score + remote_bonus + preference_bonus

    return {
        "salary_score": salary_score,
        "company_score": company_score,
        "remote_bonus": remote_bonus,
        "preference_bonus": preference_bonus,
        "final_score": round(final_score, 1),
    }
