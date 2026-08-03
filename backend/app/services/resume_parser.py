import re
from pathlib import Path

import pdfplumber
from docx import Document

from app.services.llm import complete_json, is_llm_configured
from app.services.skills_taxonomy import extract_skills_from_text

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/[^\s,;)]+", re.IGNORECASE)
PORTFOLIO_RE = re.compile(
    r"(https?://)?(www\.)?(?!linkedin\.com)[a-zA-Z0-9-]+\.(dev|io|me|com|xyz|tech)(/[^\s,;)]*)?",
    re.IGNORECASE,
)


def extract_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return _extract_pdf_text(file_path)
    if ext == ".docx":
        return _extract_docx_text(file_path)
    raise ValueError(f"Unsupported resume format: {ext}")


def _extract_pdf_text(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _extract_docx_text(file_path: str) -> str:
    document = Document(file_path)
    return "\n".join(p.text for p in document.paragraphs)


def _rule_based_extract(text: str) -> dict:
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    linkedin_match = LINKEDIN_RE.search(text)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = lines[0] if lines and len(lines[0]) < 80 else None

    skills = extract_skills_from_text(text)

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "portfolio": None,
        "experience": [],
        "education": [],
        "skills": skills,
        "certifications": [],
        "projects": [],
        "technologies": skills,
        "domain_expertise": [],
        "preferred_roles": [],
        "preferred_locations": [],
        "total_experience_years": None,
    }


_EXTRACTION_SYSTEM_PROMPT = """You extract structured profile data from resume text for a job \
intelligence platform that supports any profession (software, data/AI, product, design, \
devops/cloud, cybersecurity, sales, marketing, finance, consulting, operations, etc).

Reply with ONLY a single JSON object, no prose, matching exactly this shape:
{
  "name": string|null, "email": string|null, "phone": string|null,
  "linkedin": string|null, "portfolio": string|null,
  "experience": [{"title": string, "company": string, "start": string|null, "end": string|null, "summary": string}],
  "education": [{"degree": string, "institution": string, "year": string|null}],
  "skills": [string], "certifications": [string],
  "projects": [{"name": string, "description": string}],
  "technologies": [string], "domain_expertise": [string],
  "preferred_roles": [string], "preferred_locations": [string],
  "total_experience_years": number|null
}"""


def parse_resume_to_profile(text: str) -> dict:
    """Best-effort structured extraction: LLM-assisted when configured, rule-based fallback."""
    fallback = _rule_based_extract(text)

    if not is_llm_configured():
        return fallback

    try:
        extracted = complete_json(system=_EXTRACTION_SYSTEM_PROMPT, user=text[:15000])
    except Exception:
        return fallback

    merged = {**fallback, **{k: v for k, v in extracted.items() if v not in (None, [], "")}}
    if not merged.get("skills"):
        merged["skills"] = fallback["skills"]
    return merged
