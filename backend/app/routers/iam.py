"""IAM learning module endpoints: study material + server-graded quizzes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.content import iam_modules as content
from app.database import get_db
from app.models import QuizAnswer
from app.schemas import QuizAnswerRequest

router = APIRouter(prefix="/api/iam", tags=["iam"])


@router.get("/modules")
def list_iam_modules():
    return {"modules": content.list_modules()}


@router.get("/modules/{module_id}")
def get_iam_module(module_id: str):
    m = content.get_module(module_id)
    if m is None:
        raise HTTPException(404, "Module not found.")
    # Quiz answers stay server-side: strip correct_index/explanation from the payload.
    module = dict(m)
    module["quiz"] = [
        {
            "index": i,
            "question": q["question"],
            "options": q["options"],
        }
        for i, q in enumerate(m["quiz"])
    ]
    return module


@router.post("/modules/{module_id}/quiz")
def answer_quiz(module_id: str, req: QuizAnswerRequest, db: Session = Depends(get_db)):
    m = content.get_module(module_id)
    if m is None:
        raise HTTPException(404, "Module not found.")
    if req.question_index >= len(m["quiz"]):
        raise HTTPException(404, "Quiz question not found.")
    q = m["quiz"][req.question_index]
    if req.chosen_index >= len(q["options"]):
        raise HTTPException(400, "Invalid choice index.")
    correct = req.chosen_index == q["correct_index"]
    db.add(
        QuizAnswer(
            module_id=module_id,
            question_id=f"{module_id}-quiz-{req.question_index}",
            chosen=str(req.chosen_index),
            correct=correct,
        )
    )
    db.commit()
    return {
        "correct": correct,
        "correct_index": q["correct_index"],
        "explanation": q["explanation"],
    }
