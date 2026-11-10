"""FastAPI application: SDET Interview Gym backend."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import JAVA_MODE, settings
from app.database import Base, engine
from app.routers import analytics, automation, flashcards, iam, java, mock, resume, roadmap, scenarios, settings as settings_router, sql

CONTENT_INVENTORY = {
    "java_questions": 33,
    "sql_challenges": 26,
    "scenarios": 30,
    "iam_modules": 5,
    "flashcards": 100,
    "resume_questions": 15,
    "mock_sections": 6,
    "automation_exercises": 12,
}


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
    settings_router.router,
):
    app.include_router(router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "java_mode": JAVA_MODE,
        "llm_enabled": bool(settings.llm_api_key),
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
