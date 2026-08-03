from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import Preference
from app.schemas.preferences import PreferenceOut, PreferenceUpdate

router = APIRouter(prefix="/preferences", tags=["preferences"])


def _get_or_create_preference(db: Session) -> Preference:
    preference = db.query(Preference).first()
    if not preference:
        preference = Preference()
        db.add(preference)
        db.commit()
        db.refresh(preference)
    return preference


@router.get("", response_model=PreferenceOut)
def get_preferences(db: Session = Depends(get_db)) -> Preference:
    return _get_or_create_preference(db)


@router.put("", response_model=PreferenceOut)
def update_preferences(payload: PreferenceUpdate, db: Session = Depends(get_db)) -> Preference:
    preference = _get_or_create_preference(db)
    for field, value in payload.model_dump().items():
        setattr(preference, field, value)
    db.commit()
    db.refresh(preference)
    return preference
