"""Automation lab endpoints: Selenium/Playwright/REST Assured exercises + architecture Q&A."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.content import automation_lab as content
from app.database import get_db
from app.models import ActivityEvent
from app.schemas import ActivityRequest

router = APIRouter(prefix="/api/automation", tags=["automation"])

_SOLUTION_FIELDS = {"solution", "explanation", "followups"}


@router.get("/exercises")
def list_automation_exercises():
    return {"exercises": content.list_exercises()}


@router.get("/exercises/{exercise_id}")
def get_automation_exercise(exercise_id: str):
    e = content.get_exercise(exercise_id)
    if e is None:
        raise HTTPException(404, "Exercise not found.")
    return {k: v for k, v in e.items() if k not in _SOLUTION_FIELDS}


@router.post("/exercises/{exercise_id}/reveal")
def reveal_automation_exercise(exercise_id: str, db=Depends(get_db)):
    e = content.get_exercise(exercise_id)
    if e is None:
        raise HTTPException(404, "Exercise not found.")
    return {
        "solution": e.get("solution"),
        "explanation": e.get("explanation"),
        "followups": e.get("followups", []),
    }


@router.get("/architecture")
def framework_architecture():
    return {"questions": content.list_architecture_qa()}


@router.post("/activity")
def record_activity(req: ActivityRequest, db=Depends(get_db)):
    db.add(ActivityEvent(topic=req.topic, kind=req.kind, seconds=req.seconds))
    db.commit()
    return {"recorded": True}
