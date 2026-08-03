import hashlib


def compute_dedup_hash(company: str, title: str, location: str | None) -> str:
    key = f"{(company or '').strip().lower()}|{(title or '').strip().lower()}|{(location or '').strip().lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()
