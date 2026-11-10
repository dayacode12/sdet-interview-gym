"""Roadmap, cheat sheet and dashboard summary endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.content import java_tricks
from app.content import roadmap as content

router = APIRouter(prefix="/api", tags=["roadmap"])


@router.get("/roadmap")
def get_roadmap():
    return {"roadmap": content.ROADMAP, "priority_questions": content.PRIORITY_QUESTIONS}


@router.get("/cheatsheet")
def get_cheatsheet():
    return {
        "sections": content.CHEAT_SHEET_SECTIONS,
        "http_status_codes": [
            {"code": code, "meaning": meaning} for code, meaning in content.HTTP_STATUS_CODES
        ],
        "java_tricks": java_tricks.JAVA_TRICKS,
    }


@router.get("/about")
def about():
    """Honesty page content: what this tool is and what it is not."""
    return {
        "candidate": settings.candidate_name,
        "disclaimer": (
            "All questions, scenarios and 'expected interview questions' in this gym are "
            "PREDICTIONS of likely interview topics based on the published role description and "
            "public interview-prep knowledge. They are not leaked or actual Charles Schwab "
            "interview questions."
        ),
        "scoring_note": (
            "Free-text scoring is rule-based and transparent (keyword coverage, structure "
            "signals) unless an LLM key is configured. It is a practice aid, not a human judge."
        ),
    }
