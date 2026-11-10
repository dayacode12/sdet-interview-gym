"""Java coding lab endpoints: list, detail, reveal, run."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services import java_executor
from app.config import JAVA_MODE
from app.content import java_questions
from app.database import get_db
from app.models import Attempt
from app.schemas import JavaRunRequest

router = APIRouter(prefix="/api/java", tags=["java"])

_SOLUTION_FIELDS = {"solution", "explanation", "followups"}


@router.get("/meta")
def java_meta():
    return {
        "java_mode": JAVA_MODE,
        "mode_label": {
            "docker": "Docker sandbox (isolated container, no network)",
            "local": "Local JVM subprocess (isolated temp directory)",
            "disabled": "Execution disabled — study mode only",
        }[JAVA_MODE],
        "total_questions": len(java_questions.JAVA_QUESTIONS),
        "runnable": sum(1 for q in java_questions.JAVA_QUESTIONS if q.get("tests")),
        "categories": java_questions.category_counts(),
    }


@router.get("/questions")
def list_java_questions():
    return {"questions": java_questions.list_questions()}


@router.get("/questions/{question_id}")
def get_java_question(question_id: str):
    q = java_questions.get_question(question_id)
    if q is None:
        raise HTTPException(404, "Question not found.")
    detail = {k: v for k, v in q.items() if k not in _SOLUTION_FIELDS}
    return detail


@router.post("/questions/{question_id}/reveal")
def reveal_java_solution(question_id: str, db: Session = Depends(get_db)):
    q = java_questions.get_question(question_id)
    if q is None:
        raise HTTPException(404, "Question not found.")
    db.add(
        Attempt(
            question_type="java",
            question_id=question_id,
            status="revealed",
            score=0.0,
        )
    )
    db.commit()
    return {
        "solution": q["solution"],
        "explanation": q["explanation"],
        "followups": q["followups"],
    }


@router.post("/run")
def run_java(req: JavaRunRequest, db: Session = Depends(get_db)):
    q = java_questions.get_question(req.question_id)
    if q is None:
        raise HTTPException(404, "Question not found.")
    tests = q.get("tests") or []
    if not tests:
        return {
            "ok": False,
            "mode": JAVA_MODE,
            "error": (
                "This is a design/code-review question — there is nothing to execute. "
                "Compare your code with the model solution instead."
            ),
        }
    result = java_executor.run_tests(req.code, tests)
    if result.total > 0:
        db.add(
            Attempt(
                question_type="java",
                question_id=req.question_id,
                status="pass" if result.ok else "fail",
                score=round(100.0 * result.passed / result.total, 1),
            )
        )
        db.commit()
    return result.to_dict()
