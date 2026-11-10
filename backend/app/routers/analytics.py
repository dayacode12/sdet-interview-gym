"""Progress analytics: honest aggregation of everything recorded so far."""
from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.content import (
    flashcards as flashcards_content,
    iam_modules as iam_content,
    java_questions,
    sql_challenges,
)
from app.database import get_db
from app.models import (
    ActivityEvent,
    Attempt,
    FlashcardState,
    MockSession,
    QuizAnswer,
    ScenarioSubmission,
)
from app.schemas import ActivityRequest

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.post("/activity")
def record_activity(req: ActivityRequest, db: Session = Depends(get_db)):
    db.add(ActivityEvent(topic=req.topic, kind=req.kind, seconds=req.seconds))
    db.commit()
    return {"recorded": True}


def _question_stats(db: Session, question_type: str) -> dict:
    attempts = db.query(Attempt).filter(Attempt.question_type == question_type).all()
    by_question: dict[str, dict] = defaultdict(lambda: {"pass": 0, "fail": 0, "revealed": 0, "best": 0.0})
    for a in attempts:
        entry = by_question[a.question_id]
        entry[a.status] = entry.get(a.status, 0) + 1
        entry["best"] = max(entry["best"], a.score or 0.0)
    return by_question


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    java_attempts = db.query(Attempt).filter(Attempt.question_type == "java").all()
    sql_attempts = db.query(Attempt).filter(Attempt.question_type == "sql").all()

    java_by_q = _question_stats(db, "java")
    sql_by_q = _question_stats(db, "sql")

    def domain_stats(by_q, all_ids):
        attempted = {qid for qid, v in by_q.items() if (v["pass"] + v["fail"]) > 0}
        passed = {qid for qid, v in by_q.items() if v["pass"] > 0}
        revealed = {qid for qid, v in by_q.items() if v["revealed"] > 0}
        return {
            "total": len(all_ids),
            "attempted": len(attempted),
            "passed": len(passed & attempted),
            "revealed": len(revealed),
            "unseen": len([i for i in all_ids if i not in by_q]),
            "completion_pct": round(100.0 * (len(passed) + len(revealed)) / len(all_ids), 1) if all_ids else 0.0,
        }

    java_stats = domain_stats(java_by_q, [q["id"] for q in java_questions.list_questions()])
    sql_stats = domain_stats(sql_by_q, [c["id"] for c in sql_challenges.list_challenges()])

    # Weak Java categories: pass rate per category among attempted.
    category_perf = defaultdict(lambda: {"attempts": 0, "passes": 0})
    id_to_category = {q["id"]: q["category"] for q in java_questions.list_questions()}
    for a in java_attempts:
        if a.status in {"pass", "fail"}:
            cat = id_to_category.get(a.question_id, "unknown")
            category_perf[cat]["attempts"] += 1
            if a.status == "pass":
                category_perf[cat]["passes"] += 1
    weak_categories = [
        {
            "category": cat,
            "pass_rate": round(100.0 * v["passes"] / v["attempts"], 1),
            "attempts": v["attempts"],
        }
        for cat, v in category_perf.items()
    ]
    weak_categories.sort(key=lambda x: x["pass_rate"])

    # Scenarios.
    scenario_rows = db.query(ScenarioSubmission).all()
    scored = [r for r in scenario_rows if isinstance(r.scores, dict) and "overall" in (r.scores or {})]
    scenario_stats = {
        "total": 30,
        "attempted": len({r.scenario_id for r in scenario_rows}),
        "submissions": len(scored),
        "revealed": sum(1 for r in scenario_rows if (r.scores or {}).get("revealed")),
        "average_score": round(sum(r.scores["overall"] for r in scored) / len(scored), 1) if scored else None,
    }

    # Mock interviews.
    mock_sessions = db.query(MockSession).order_by(MockSession.id.desc()).limit(20).all()
    finished = [s for s in mock_sessions if s.finished_at is not None and s.total_score]
    mock_stats = {
        "sessions": len(mock_sessions),
        "finished": len(finished),
        "last_score": finished[0].total_score if finished else None,
        "best_score": round(max(s.total_score for s in finished), 1) if finished else None,
        "dimension_averages": _dimension_averages(finished),
    }

    # Flashcards.
    states = db.query(FlashcardState).all()
    flashcard_stats = {
        "total": len(flashcards_content.all_cards()),
        "reviewed": len(states),
        "known": sum(1 for s in states if s.known),
        "needs_revision": sum(1 for s in states if not s.known),
    }

    # Quiz accuracy per IAM module.
    quiz_rows = db.query(QuizAnswer).all()
    quiz_by_module = defaultdict(lambda: {"correct": 0, "total": 0})
    for r in quiz_rows:
        quiz_by_module[r.module_id]["total"] += 1
        quiz_by_module[r.module_id]["correct"] += int(r.correct)
    quiz_stats = {
        module_id: {
            "module": next((m["title"] for m in iam_content.list_modules() if m["id"] == module_id), module_id),
            "accuracy": round(100.0 * v["correct"] / v["total"], 1),
            "answered": v["total"],
        }
        for module_id, v in quiz_by_module.items()
    }

    # Time on topic.
    events = db.query(ActivityEvent).order_by(ActivityEvent.id.desc()).limit(500).all()
    by_topic = defaultdict(int)
    by_kind = defaultdict(int)
    for e in events:
        by_topic[e.topic] += e.seconds or 0
        by_kind[e.kind] += e.seconds or 0

    recent_attempts = [
        {
            "question_type": a.question_type,
            "question_id": a.question_id,
            "status": a.status,
            "score": a.score,
            "created_at": a.created_at,
        }
        for a in (java_attempts + sql_attempts)[-25:]
    ]

    return {
        "java": java_stats,
        "sql": sql_stats,
        "scenarios": scenario_stats,
        "mock": mock_stats,
        "flashcards": flashcard_stats,
        "quizzes": quiz_stats,
        "weak_java_categories": weak_categories[:5],
        "recent_attempts": recent_attempts,
        "time_by_topic": dict(sorted(by_topic.items(), key=lambda kv: -kv[1])[:10]),
        "time_by_kind": dict(by_kind),
    }


def _dimension_averages(finished_sessions: list) -> dict | None:
    totals: dict[str, list] = defaultdict(list)
    for s in finished_sessions:
        for dim, val in (s.dimension_scores or {}).items():
            totals[dim].append(val)
    if not totals:
        return None
    return {d: round(sum(v) / len(v), 1) for d, v in totals.items()}
