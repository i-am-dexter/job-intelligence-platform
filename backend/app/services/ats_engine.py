from app.db.models import Job, Profile
from app.schemas.analysis import ATSResult
from app.services.skills_taxonomy import extract_skills_from_text


def analyze_ats(profile: Profile, job: Job) -> ATSResult:
    jd_text = f"{job.title} {job.description or ''} {job.requirements or ''}"

    required_keywords = {js.skill.lower() for js in job.skills if js.kind == "required"}
    preferred_keywords = {js.skill.lower() for js in job.skills if js.kind == "preferred"}
    if not required_keywords and not preferred_keywords:
        # Job wasn't pre-tagged with skills; fall back to extracting from raw text.
        required_keywords = {s.lower() for s in extract_skills_from_text(jd_text)}

    all_keywords = required_keywords | preferred_keywords
    profile_keywords = {s.lower() for s in (profile.skills or []) + (profile.technologies or [])}

    matched = sorted(all_keywords & profile_keywords)
    missing = sorted(all_keywords - profile_keywords)

    coverage = round(100 * len(matched) / len(all_keywords), 1) if all_keywords else 100.0

    missing_required = sorted(required_keywords - profile_keywords)
    recommendations = []
    if missing_required:
        recommendations.append(
            f"Add these required keywords to your resume if you have the experience: {', '.join(missing_required[:8])}"
        )
    if coverage < 50:
        recommendations.append("Your resume covers less than half of this job's keywords — consider tailoring it before applying.")
    if not recommendations:
        recommendations.append("Strong keyword coverage for this role.")

    return ATSResult(
        ats_score=coverage,
        keyword_coverage=coverage,
        matched_keywords=matched,
        missing_keywords=missing,
        recommendations=recommendations,
    )
