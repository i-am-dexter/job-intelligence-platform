from sqlalchemy.orm import Session

from app.db.models import SystemLog


def log_event(db: Session, category: str, message: str, context: dict | None = None) -> None:
    db.add(SystemLog(category=category, message=message, context=context))
    db.commit()
