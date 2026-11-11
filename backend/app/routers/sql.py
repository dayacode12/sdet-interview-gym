"""SQL playground + challenge endpoints. The sandbox is read-only and isolated."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.content import sql_challenges
from app.database import get_db
from app.models import Attempt
from app.schemas import SqlRunRequest, SqlSubmitRequest
from app.services import sql_explain, sql_runner

router = APIRouter(prefix="/api/sql", tags=["sql"])

_HIDDEN = {"expected_sql", "explanation", "followups"}


def _english(sql: str) -> dict | None:
    """Best-effort English translation for a reference query. Never raises —
    a translation failure must not break submitting or revealing."""
    try:
        return sql_explain.explain(sql)
    except Exception:  # noqa: BLE001 - defensive by design
        return None


def _grade_rows(user_rows: list, expected_rows: list) -> bool:
    """Order-insensitive multiset comparison — ORDER BY is never the point."""
    if len(user_rows) != len(expected_rows):
        return False
    if not expected_rows:
        return len(user_rows) == 0

    def key(rows):
        return sorted(repr(r) for r in rows)

    return key(user_rows) == key(expected_rows)


@router.get("/challenges")
def list_sql_challenges():
    return {"challenges": sql_challenges.list_challenges()}


@router.get("/schema")
def sql_schema():
    """Table shapes so the UI can render the data dictionary (no credentials)."""
    from app.content.sql_data import TABLE_COLUMNS

    return {"tables": TABLE_COLUMNS}


@router.get("/challenges/{challenge_id}")
def get_sql_challenge(challenge_id: str):
    c = sql_challenges.get_challenge(challenge_id)
    if c is None:
        raise HTTPException(404, "Challenge not found.")
    return {k: v for k, v in c.items() if k not in _HIDDEN}


@router.post("/run")
def run_sql(req: SqlRunRequest):
    try:
        return sql_runner.run_query(req.sql)
    except sql_runner.SqlExecutionError as exc:
        raise HTTPException(400, str(exc))


@router.post("/explain")
def explain_sql(req: SqlRunRequest):
    """Translate a query into plain English. Parsing only — nothing is executed."""
    try:
        return sql_explain.explain(req.sql)
    except sql_explain.SqlExplainError as exc:
        raise HTTPException(422, str(exc))


@router.post("/challenges/{challenge_id}/submit")
def submit_sql(challenge_id: str, req: SqlSubmitRequest, db: Session = Depends(get_db)):
    c = sql_challenges.get_challenge(challenge_id)
    if c is None:
        raise HTTPException(404, "Challenge not found.")
    try:
        result = sql_runner.run_query(req.sql)
    except sql_runner.SqlExecutionError as exc:
        db.add(
            Attempt(
                question_type="sql",
                question_id=challenge_id,
                status="fail",
                score=0.0,
                duration_seconds=req.duration_seconds,
            )
        )
        db.commit()
        raise HTTPException(400, str(exc))

    expected_rows = sql_runner.run_expected(c["expected_sql"])
    correct = _grade_rows(result["rows"], expected_rows)
    db.add(
        Attempt(
            question_type="sql",
            question_id=challenge_id,
            status="pass" if correct else "fail",
            score=100.0 if correct else 0.0,
            duration_seconds=req.duration_seconds,
        )
    )
    db.commit()
    return {
        "correct": correct,
        "your_rows": result["rows"],
        "expected_rows": expected_rows,
        "row_order_ignored": True,
        "expected_sql": c["expected_sql"],
        "expected_english": _english(c["expected_sql"]),
        "explanation": c["explanation"],
        "security_note": c["security_note"],
        "followups": c["followups"],
    }


@router.post("/challenges/{challenge_id}/reveal")
def reveal_sql(challenge_id: str, db: Session = Depends(get_db)):
    c = sql_challenges.get_challenge(challenge_id)
    if c is None:
        raise HTTPException(404, "Challenge not found.")
    db.add(
        Attempt(question_type="sql", question_id=challenge_id, status="revealed", score=0.0)
    )
    db.commit()
    return {
        "expected_sql": c["expected_sql"],
        "expected_english": _english(c["expected_sql"]),
        "expected_rows": sql_runner.run_expected(c["expected_sql"]),
        "explanation": c["explanation"],
        "security_note": c["security_note"],
        "followups": c["followups"],
    }
