from app.db.models import Job, Profile
from app.schemas.analysis import GapResult

# Lightweight skill -> (certifications, project ideas) mapping for common skills across
# professions. Not exhaustive; used to seed concrete, actionable suggestions.
SKILL_RECOMMENDATIONS: dict[str, dict[str, list[str]]] = {
    "aws": {"certifications": ["AWS Certified Solutions Architect – Associate"], "projects": ["Deploy a containerized app on AWS ECS/EKS"]},
    "azure": {"certifications": ["Microsoft Certified: Azure Fundamentals"], "projects": ["Build a CI/CD pipeline on Azure DevOps"]},
    "gcp": {"certifications": ["Google Cloud Professional Cloud Architect"], "projects": ["Deploy a serverless app on Cloud Run"]},
    "kubernetes": {"certifications": ["Certified Kubernetes Administrator (CKA)"], "projects": ["Deploy a multi-service app on a self-managed k8s cluster"]},
    "machine learning": {"certifications": ["DeepLearning.AI Machine Learning Specialization"], "projects": ["Build and deploy an end-to-end ML model"]},
    "penetration testing": {"certifications": ["Offensive Security Certified Professional (OSCP)"], "projects": ["Complete a set of HackTheBox/TryHackMe boxes and document write-ups"]},
    "cissp": {"certifications": ["CISSP"], "projects": []},
    "product management": {"certifications": ["Pragmatic Institute Product Management Certification"], "projects": ["Write a full PRD and go-to-market plan for a sample product"]},
    "financial modeling": {"certifications": ["CFA Level I"], "projects": ["Build a 3-statement financial model for a public company"]},
    "salesforce": {"certifications": ["Salesforce Certified Administrator"], "projects": []},
    "seo": {"certifications": ["Google Analytics / SEO certifications"], "projects": ["Run and document an SEO audit + improvement plan for a site"]},
}


def analyze_gaps(profile: Profile, job: Job) -> GapResult:
    profile_skills = {s.lower(): s for s in (profile.skills or [])}
    required = {js.skill.lower(): js.skill for js in job.skills if js.kind == "required"}
    preferred = {js.skill.lower(): js.skill for js in job.skills if js.kind == "preferred"}
    job_skills = {**preferred, **required}

    matched = [display for key, display in job_skills.items() if key in profile_skills]
    missing = [display for key, display in job_skills.items() if key not in profile_skills]

    # Suggested skills: adjacent taxonomy skills mentioned in the JD but not required/preferred
    # and not already on the profile — kept simple by reusing the missing list minus required.
    missing_required = [display for key, display in required.items() if key not in profile_skills]
    suggested = [s for s in missing if s not in missing_required]

    learning_priorities = missing_required[:5]

    certifications: list[str] = []
    projects: list[str] = []
    for skill in missing_required:
        rec = SKILL_RECOMMENDATIONS.get(skill.lower())
        if rec:
            certifications.extend(rec["certifications"])
            projects.extend(rec["projects"])

    return GapResult(
        matched_skills=matched,
        missing_skills=missing,
        suggested_skills=suggested,
        learning_priorities=learning_priorities,
        recommended_certifications=sorted(set(certifications)),
        recommended_projects=sorted(set(projects)),
    )
