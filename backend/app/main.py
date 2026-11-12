"""FastAPI application: SDET Interview Gym backend."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import JAVA_MODE, settings
from app.database import Base, engine
from app.routers import (
    analytics,
    automation,
    company,
    drafts,
    flashcards,
    iam,
    java,
    mindmap,
    mock,
    resume,
    roadmap,
    scenarios,
    settings as settings_router,
    sql,
)

CONTENT_INVENTORY = None  # computed at import below, from the real banks


def _compute_inventory() -> dict:
    """Live counts from the content banks — never hardcoded, always truthful."""
    from app.content import (
        automation_lab,
        flashcards,
        iam_modules,
        java_questions,
        mock_interview,
        resume_deep_dive,
        scenarios,
        sql_challenges,
    )

    return {
        "java_questions": len(java_questions.JAVA_QUESTIONS),
        "sql_challenges": len(sql_challenges.SQL_CHALLENGES),
        "scenarios": len(scenarios.SCENARIOS),
        "iam_modules": len(iam_modules.IAM_MODULES),
        "flashcards": len(flashcards.all_cards()),
        "resume_questions": len(resume_deep_dive.RESUME_QUESTIONS),
        "mock_sections": len(mock_interview.MOCK_SECTIONS),
        "automation_exercises": len(automation_lab.EXERCISES),
    }


CONTENT_INVENTORY = _compute_inventory()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (SQLite default). Seeding happens lazily via content modules.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Personal interview preparation platform for a Schwab-style SDET / Cyber Security QA "
        "interview. Java execution, SQL sandbox, scenario evaluation, mock interviews and "
        "progress analytics."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    java.router,
    sql.router,
    scenarios.router,
    mock.router,
    flashcards.router,
    iam.router,
    automation.router,
    resume.router,
    roadmap.router,
    analytics.router,
    company.router,
    mindmap.router,
    settings_router.router,
    drafts.router,
):
    app.include_router(router)


@app.get("/api/health")
def health():
    """Environment + which database is actually backing this instance.

    `database.dialect` answers "am I on Postgres or the ephemeral SQLite file?";
    host is included without credentials. A failed connection is reported
    honestly rather than pretending the app is healthy.
    """
    database = {"dialect": engine.dialect.name, "host": engine.url.host or "local-file"}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        database["reachable"] = True
    except Exception:
        database["reachable"] = False
    return {
        "status": "ok",
        "java_mode": JAVA_MODE,
        "llm_enabled": bool(settings.llm_api_key),
        "database": database,
    }


@app.get("/api/dashboard")
def dashboard():
    """Landing-page payload: environment + inventory + roadmap pointer."""
    return {
        "candidate_name": settings.candidate_name,
        "java_mode": JAVA_MODE,
        "content": CONTENT_INVENTORY,
        "tagline": (
            "Practice gym for the Charles Schwab Cyber Security QA SDET interview — "
            "Java coding, automation, API and SQL testing, IAM security scenarios, "
            "timed mock interviews and transparent scoring."
        ),
        "honesty": (
            "Every practice question here is a PREDICTED likely interview topic based on the "
            "public role description — not a leaked Schwab question bank. Java runs are real "
            "and never simulated; scoring is rule-based unless an LLM key is configured."
        ),
    }
