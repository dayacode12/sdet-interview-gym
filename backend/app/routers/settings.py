"""User settings: interview countdown and study preferences."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import JAVA_MODE, settings
from app.database import get_db
from app.models import Setting
from app.schemas import SettingsUpdateRequest
from app.services import evaluation

router = APIRouter(prefix="/api/settings", tags=["settings"])

DEFAULTS = {
    "interview_datetime": "",
    "target_role": "SDET — Cyber Security QA, Charles Schwab",
    "daily_goal_minutes": 240,
}


def _get(db: Session, key: str, default):
    row = db.get(Setting, key)
    if row is None:
        return default
    value = row.value
    if isinstance(value, dict):
        return value.get("value", default)
    return value if value is not None else default


@router.get("")
def get_settings(db: Session = Depends(get_db)):
    return {
        "candidate_name": settings.candidate_name,
        "interview_datetime": _get(db, "interview_datetime", DEFAULTS["interview_datetime"]),
        "target_role": _get(db, "target_role", DEFAULTS["target_role"]),
        "daily_goal_minutes": _get(db, "daily_goal_minutes", DEFAULTS["daily_goal_minutes"]),
        "java_mode": JAVA_MODE,
        "llm": evaluation.llm_status(),
    }


@router.put("")
def update_settings(req: SettingsUpdateRequest, db: Session = Depends(get_db)):
    updates = {
        "interview_datetime": req.interview_datetime,
        "target_role": req.target_role,
        "daily_goal_minutes": req.daily_goal_minutes,
    }
    for key, value in updates.items():
        if value is None:
            continue
        row = db.get(Setting, key)
        if row is None:
            row = Setting(key=key, value={"value": value})
            db.add(row)
        else:
            row.value = {"value": value}
    db.commit()
    return get_settings(db)
