from app.db.models import Job, Preference, Profile
from app.services.ats_engine import analyze_ats

# Weights sum to 100 so match_score lands in [0, 100].
WEIGHTS = {
    "skill_match": 30,
    "experience_match": 15,
    "preference_match": 15,
    "domain_match": 10,
    "location_match": 15,
    "salary_match": 10,
    "ats_match": 5,
}


def _skill_match(profile: Profile, job: Job) -> float:
    profile_skills = {s.lower() for s in (profile.skills or [])}
    job_skills = {js.skill.lower() for js in job.skills}
    if not job_skills:
        return 50.0  # no extracted skills to compare against; neutral score
    overlap = profile_skills & job_skills
    return round(100 * len(overlap) / len(job_skills), 1)


def _experience_match(profile: Profile, job: Job) -> float:
    if not job.experience_required or profile.total_experience_years is None:
        return 50.0
    required = _extract_years(job.experience_required)
    if required is None:
        return 50.0
    years = profile.total_experience_years
    if years >= required:
        return 100.0
    if required == 0:
        return 100.0
    return round(max(0.0, 100 * years / required), 1)


def _extract_years(text: str) -> float | None:
    import re

    match = re.search(r"(\d+)", text)
    return float(match.group(1)) if match else None


def _preference_match(preference: Preference | None, job: Job) -> float:
    if preference is None:
        return 50.0
    score = 0.0
    checks = 0

    if preference.preferred_titles:
        checks += 1
        if any(t.lower() in job.title.lower() for t in preference.preferred_titles):
            score += 1

    if preference.employment_type:
        checks += 1
        if job.employment_type and job.employment_type.lower() in [
            e.lower() for e in preference.employment_type
        ]:
            score += 1

    if preference.industries:
        checks += 1
        if job.company and job.company.industry and job.company.industry.lower() in [
            i.lower() for i in preference.industries
        ]:
            score += 1

    if checks == 0:
        return 50.0
    return round(100 * score / checks, 1)


def _domain_match(profile: Profile, job: Job) -> float:
    domains = {d.lower() for d in (profile.domain_expertise or [])}
    if not domains:
        return 50.0
    haystack = f"{job.title} {job.description or ''}".lower()
    return 100.0 if any(d in haystack for d in domains) else 30.0


def _location_match(preference: Preference | None, job: Job) -> float:
    if preference is None:
        return 50.0

    if job.remote:
        return 100.0 if preference.remote_only or preference.hybrid_ok or preference.onsite_ok else 50.0

    if preference.remote_only:
        return 0.0

    if preference.preferred_locations and job.location:
        if any(loc.lower() in job.location.lower() for loc in preference.preferred_locations):
            return 100.0
        return 30.0

    if preference.countries and job.country:
        if job.country.lower() in [c.lower() for c in preference.countries]:
            return 100.0
        return 30.0

    return 50.0


def _salary_match(preference: Preference | None, job: Job) -> float:
    if preference is None or (preference.min_salary is None and preference.max_salary is None):
        return 50.0
    if job.salary_min is None and job.salary_max is None:
        return 50.0

    job_min = job.salary_min or job.salary_max
    job_max = job.salary_max or job.salary_min
    pref_min = preference.min_salary or 0
    pref_max = preference.max_salary or float("inf")

    if job_max < pref_min or job_min > pref_max:
        return 0.0
    return 100.0


def compute_match(profile: Profile, preference: Preference | None, job: Job) -> dict:
    ats = analyze_ats(profile, job)

    components = {
        "skill_match": _skill_match(profile, job),
        "experience_match": _experience_match(profile, job),
        "preference_match": _preference_match(preference, job),
        "domain_match": _domain_match(profile, job),
        "location_match": _location_match(preference, job),
        "salary_match": _salary_match(preference, job),
        "ats_match": ats.ats_score,
    }

    match_score = sum(components[key] * (WEIGHTS[key] / 100) for key in WEIGHTS)

    return {"match_score": round(match_score, 1), "components": components}
