"""Resume deep-dive endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.content import resume_deep_dive as content

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.get("/questions")
def list_resume_questions():
    return {"questions": content.list_resume_questions()}


@router.get("/questions/{question_id}")
def get_resume_question(question_id: str):
    q = content.get_resume_question(question_id)
    if q is None:
        raise HTTPException(404, "Question not found.")
    return q
