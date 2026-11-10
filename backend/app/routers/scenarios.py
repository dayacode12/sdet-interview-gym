"""Scenario simulator endpoints: list, attempt, submit for evaluation, reveal."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.content import scenarios as content
from app.database import get_db
from app.models import ScenarioSubmission
from app.schemas import ScenarioSubmitRequest
from app.services import evaluation

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

# Material hidden until the candidate answers (or asks to reveal).
_HIDDEN = {"key_points", "test_cases", "api_checks", "db_checks", "job_checks",
           "security_consideration", "root_cause_paths", "strong_answer", "followups"}


@router.get("")
def list_scenarios(topic: str | None = None, severity: str | None = None):
    items = content.list_scenarios()
    if topic:
        items = [s for s in items if topic.lower() in s["topic"].lower()]
    if severity:
        items = [s for s in items if s["severity"].lower() == severity.lower()]
    topics = sorted({s["topic"] for s in content.list_scenarios()})
    severities = sorted({s["severity"] for s in content.list_scenarios()})
    return {"scenarios": items, "topics": topics, "severities": severities}


@router.get("/{scenario_id}")
def get_scenario(scenario_id: str):
    s = content.get_scenario(scenario_id)
    if s is None:
        raise HTTPException(404, "Scenario not found.")
    return {k: v for k, v in s.items() if k not in _HIDDEN}


@router.post("/{scenario_id}/submit")
def submit_scenario(scenario_id: str, req: ScenarioSubmitRequest, db: Session = Depends(get_db)):
    s = content.get_scenario(scenario_id)
    if s is None:
        raise HTTPException(404, "Scenario not found.")
    evaluation_result = evaluation.evaluate_answer(
        req.answer,
        question=s["interviewer_question"],
        key_points=s["key_points"],
        reference_answer=s["strong_answer"],
    )
    db.add(
        ScenarioSubmission(
            scenario_id=scenario_id,
            answer=req.answer,
            scores={
                "overall": evaluation_result["overall"],
                **evaluation_result["scores"],
            },
            feedback={
                "method": evaluation_result["method"],
                "dimensions": evaluation_result["feedback"],
            },
        )
    )
    db.commit()
    return {
        "evaluation": evaluation_result,
        "key_points": s["key_points"],
        "strong_answer": s["strong_answer"],
        "test_cases": s["test_cases"],
        "api_checks": s["api_checks"],
        "db_checks": s["db_checks"],
        "job_checks": s["job_checks"],
        "security_consideration": s["security_consideration"],
        "root_cause_paths": s["root_cause_paths"],
        "followups": s["followups"],
    }


@router.post("/{scenario_id}/reveal")
def reveal_scenario(scenario_id: str, db: Session = Depends(get_db)):
    s = content.get_scenario(scenario_id)
    if s is None:
        raise HTTPException(404, "Scenario not found.")
    db.add(
        ScenarioSubmission(
            scenario_id=scenario_id,
            answer="",
            scores={"revealed": True},
            feedback={"method": "revealed"},
        )
    )
    db.commit()
    return {k: v for k, v in s.items() if k in _HIDDEN}
