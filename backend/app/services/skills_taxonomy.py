"""Flat skills taxonomy shared by the ATS, matching, and gap engines.

Covers common terms across the professions named in the product spec
(software/data/AI/product/design/devops/cloud/sales/marketing/finance/
consulting/ops/cybersecurity) so keyword extraction isn't limited to
software engineering roles.
"""

import re

SKILLS_TAXONOMY: list[str] = [
    # Software engineering / general tech
    "python", "javascript", "typescript", "java", "c++", "c#", "golang", "rust", "ruby", "php",
    "react", "next.js", "vue", "angular", "node.js", "django", "flask", "fastapi", "spring boot",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "graphql", "rest api",
    "git", "ci/cd", "microservices", "system design", "unit testing", "agile", "scrum",
    # Data science / AI/ML
    "machine learning", "deep learning", "nlp", "computer vision", "pytorch", "tensorflow",
    "scikit-learn", "pandas", "numpy", "data analysis", "data visualization", "statistics",
    "sql analytics", "etl", "airflow", "spark", "hadoop", "llm", "generative ai", "mlops",
    # Cloud / DevOps
    "aws", "azure", "gcp", "kubernetes", "docker", "terraform", "ansible", "jenkins",
    "prometheus", "grafana", "linux", "networking", "load balancing", "site reliability",
    # Cybersecurity
    "penetration testing", "vulnerability assessment", "siem", "incident response",
    "threat intelligence", "network security", "cryptography", "iam", "compliance",
    "risk assessment", "soc", "malware analysis", "cissp", "ceh", "security operations",
    # Product / design
    "product management", "product strategy", "roadmapping", "user research", "figma",
    "wireframing", "prototyping", "ux design", "ui design", "usability testing", "a/b testing",
    # Sales / marketing / consulting / ops / finance
    "salesforce", "crm", "lead generation", "account management", "negotiation",
    "seo", "sem", "content marketing", "email marketing", "brand strategy", "market research",
    "financial modeling", "forecasting", "budgeting", "excel", "powerpoint", "stakeholder management",
    "project management", "process improvement", "supply chain", "operations management",
    "consulting", "client management", "strategic planning",
]

_NORMALIZED = {s.lower(): s for s in SKILLS_TAXONOMY}

# Word-boundary patterns so e.g. "java" doesn't match inside "javascript". \b is unreliable
# for skills containing non-word characters (c++, c#), so boundaries are defined explicitly
# against alphanumeric neighbors instead.
_PATTERNS = [
    (re.compile(r"(?<![a-z0-9])" + re.escape(key) + r"(?![a-z0-9])"), display)
    for key, display in _NORMALIZED.items()
]


def extract_skills_from_text(text: str) -> list[str]:
    """Case-insensitive, word-boundary-aware match of the taxonomy against free text."""
    if not text:
        return []
    lowered = text.lower()
    return [display for pattern, display in _PATTERNS if pattern.search(lowered)]
