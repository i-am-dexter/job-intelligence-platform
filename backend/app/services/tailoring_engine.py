from app.db.models import Job, Profile
from app.schemas.analysis import TailoringResult
from app.services.gap_engine import analyze_gaps
from app.services.llm import complete_json, is_llm_configured

_SYSTEM_PROMPT = """You are a resume coach. Given a candidate profile and a target job, produce \
tailored resume content. Reply with ONLY a single JSON object matching exactly:
{
  "tailored_summary": string,
  "tailored_bullets": [string],
  "keyword_suggestions": [string],
  "project_recommendations": [string],
  "resume_improvements": [string]
}
Keep bullets achievement-oriented and truthful to the candidate's actual background — never invent \
experience they don't have. Do not fabricate metrics."""


def _template_fallback(profile: Profile, job: Job) -> TailoringResult:
    gaps = analyze_gaps(profile, job)
    role = job.title or "this role"
    top_skills = (profile.skills or [])[:5]

    summary = (
        f"{profile.name or 'Candidate'} is a professional with experience in "
        f"{', '.join(top_skills) or 'a range of relevant skills'}, well suited for the {role} position at {job.company_name}."
    )
    bullets = [f"Applied {skill} to deliver measurable outcomes in previous roles." for skill in top_skills[:3]]
    keyword_suggestions = gaps.missing_skills[:8]
    project_recommendations = gaps.recommended_projects
    resume_improvements = [
        "Add specific, quantified outcomes (%, $, time saved) to each bullet point.",
        f"Mirror the exact terminology from the {role} posting where it truthfully applies.",
    ]
    if gaps.missing_skills:
        resume_improvements.append(f"Address these missing keywords if applicable: {', '.join(gaps.missing_skills[:6])}")

    return TailoringResult(
        tailored_summary=summary,
        tailored_bullets=bullets,
        keyword_suggestions=keyword_suggestions,
        project_recommendations=project_recommendations,
        resume_improvements=resume_improvements,
    )


def generate_tailoring(profile: Profile, job: Job) -> TailoringResult:
    if not is_llm_configured():
        return _template_fallback(profile, job)

    profile_summary = {
        "name": profile.name,
        "skills": profile.skills,
        "technologies": profile.technologies,
        "experience": profile.experience,
        "projects": profile.projects,
        "total_experience_years": profile.total_experience_years,
    }
    job_summary = {
        "title": job.title,
        "company": job.company_name,
        "description": (job.description or "")[:4000],
        "requirements": (job.requirements or "")[:2000],
        "required_skills": [js.skill for js in job.skills if js.kind == "required"],
    }

    user_prompt = f"Candidate profile:\n{profile_summary}\n\nTarget job:\n{job_summary}"

    try:
        data = complete_json(system=_SYSTEM_PROMPT, user=user_prompt)
        return TailoringResult(**data)
    except Exception:
        return _template_fallback(profile, job)
