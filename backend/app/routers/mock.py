"""Mock interview endpoints: plan, timed session, per-answer scoring, weighted finish."""
from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.content import interview_research, mock_interview as content
from app.database import get_db
from app.models import MockAnswer, MockSession
from app.schemas import MockAnswerRequest, MockStartRequest
from app.services import evaluation
from app.services.evaluation import DIMENSIONS, RUBRIC_WEIGHTS

router = APIRouter(prefix="/api/mock", tags=["mock"])


def _question(question_id: str) -> dict:
    for q in content.all_questions():
        if q["id"] == question_id:
            return q
    raise HTTPException(404, "Question not found.")


def _section(section_id: str) -> dict:
    for s in content.MOCK_SECTIONS:
        if s["id"] == section_id:
            return s
    raise HTTPException(404, "Section not found.")


@router.get("/plan")
def mock_plan():
    return {
        "sections": content.get_plan(),
        "total_minutes": sum(s["minutes"] for s in content.MOCK_SECTIONS),
        "total_questions": content.total_questions(),
        "rubric": RUBRIC_WEIGHTS,
        "rubric_note": (
            "Every answer is scored on five dimensions; the section weights below decide how "
            "much each section contributes to the final score. The introduction is a warm-up "
            "and is not scored."
        ),
    }


@router.get("/research")
def mock_research():
    """Publicly reported interview research backing the mock questions (attributed, honest)."""
    return interview_research.get_research()


@router.get("/questions")
def mock_questions():
    return {
        "questions": [
            {
                "id": q["id"],
                "section_id": q["section_id"],
                "prompt": q["prompt"],
                "guidance": q["guidance"],
            }
            for q in content.all_questions()
        ]
    }


@router.post("/start")
def start_mock(req: MockStartRequest, db: Session = Depends(get_db)):
    session = MockSession(label=req.label or "Schwab SDET Mock Interview")
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id, "started_at": session.started_at, "label": session.label}


@router.post("/{session_id}/answer")
def submit_mock_answer(
    session_id: int, req: MockAnswerRequest, db: Session = Depends(get_db)
):
    session = db.get(MockSession, session_id)
    if session is None:
        raise HTTPException(404, "Session not found.")
    q = _question(req.question_id)
    evaluation_result = evaluation.evaluate_answer(
        req.answer,
        question=q["prompt"],
        keywords=q.get("keywords"),
        reference_answer=q.get("model_answer", ""),
    )
    db.add(
        MockAnswer(
            session_id=session_id,
            question_id=req.question_id,
            section_id=q["section_id"],
            answer=req.answer,
            elapsed_seconds=req.elapsed_seconds,
            scores={"overall": evaluation_result["overall"], **evaluation_result["scores"]},
            feedback={
                "method": evaluation_result["method"],
                "dimensions": evaluation_result["feedback"],
            },
        )
    )
    db.commit()
    return {
        "evaluation": evaluation_result,
        "model_answer": q["model_answer"],
        "keywords": q.get("keywords", []),
        "delivery_note": interview_research.delivery_note_for(req.question_id),
    }


@router.post("/{session_id}/finish")
def finish_mock(session_id: int, db: Session = Depends(get_db)):
    session = db.get(MockSession, session_id)
    if session is None:
        raise HTTPException(404, "Session not found.")
    answers = (
        db.query(MockAnswer)
        .filter(MockAnswer.session_id == session_id)
        .order_by(MockAnswer.id)
        .all()
    )

    section_scores: dict[str, list[float]] = {}
    dimension_scores: dict[str, list[float]] = {d: [] for d in DIMENSIONS}
    question_scores = []
    for a in answers:
        overall = (a.scores or {}).get("overall", 0.0)
        section_scores.setdefault(a.section_id, []).append(overall)
        for d in DIMENSIONS:
            dimension_scores[d].append((a.scores or {}).get(d, 0.0))
        question_scores.append(
            {
                "question_id": a.question_id,
                "section_id": a.section_id,
                "overall": overall,
                "elapsed_seconds": a.elapsed_seconds,
            }
        )

    weighted_total = 0.0
    weight_used = 0.0
    section_breakdown = []
    for s in content.MOCK_SECTIONS:
        scores = section_scores.get(s["id"], [])
        avg = round(sum(scores) / len(scores), 1) if scores else None
        section_breakdown.append(
            {
                "section_id": s["id"],
                "title": s["title"],
                "minutes": s["minutes"],
                "weight": s["weight"],
                "answered": len(scores),
                "question_count": len(s["questions"]),
                "average_score": avg,
            }
        )
        if avg is not None and s["weight"] > 0:
            weighted_total += s["weight"] * avg
            weight_used += s["weight"]

    total = round(weighted_total, 1) if weight_used else 0.0
    dims = {
        d: round(sum(v) / len(v), 1) if v else 0.0 for d, v in dimension_scores.items()
    }

    session.finished_at = dt.datetime.now(dt.timezone.utc)
    session.total_score = total
    session.dimension_scores = dims
    session.question_scores = question_scores
    db.commit()

    weakest = min(DIMENSIONS, key=lambda d: dims[d]) if answers else None
    return {
        "session_id": session_id,
        "total_score": total,
        "dimension_scores": dims,
        "rubric": RUBRIC_WEIGHTS,
        "sections": section_breakdown,
        "answers": question_scores,
        "answered_questions": len(answers),
        "total_questions": content.total_questions(),
        "weakest_dimension": weakest,
        "advice": (
            f"Your weakest rubric dimension was '{weakest.replace('_', ' ')}'. "
            "Revisit the matching lab before your next mock."
            if weakest
            else "No answers were recorded in this session."
        ),
    }


@router.get("/sessions")
def list_mock_sessions(db: Session = Depends(get_db)):
    sessions = db.query(MockSession).order_by(MockSession.id.desc()).limit(20).all()
    return {
        "sessions": [
            {
                "id": s.id,
                "label": s.label,
                "started_at": s.started_at,
                "finished_at": s.finished_at,
                "total_score": s.total_score,
                "dimension_scores": s.dimension_scores,
            }
            for s in sessions
        ]
    }


@router.get("/{session_id}")
def get_mock_session(session_id: int, db: Session = Depends(get_db)):
    session = db.get(MockSession, session_id)
    if session is None:
        raise HTTPException(404, "Session not found.")
    answers = (
        db.query(MockAnswer)
        .filter(MockAnswer.session_id == session_id)
        .order_by(MockAnswer.id)
        .all()
    )
    return {
        "id": session.id,
        "label": session.label,
        "started_at": session.started_at,
        "finished_at": session.finished_at,
        "total_score": session.total_score,
        "dimension_scores": session.dimension_scores,
        "answers": [
            {
                "question_id": a.question_id,
                "section_id": a.section_id,
                "answer": a.answer,
                "elapsed_seconds": a.elapsed_seconds,
                "scores": a.scores,
                "feedback": a.feedback,
            }
            for a in answers
        ],
    }
