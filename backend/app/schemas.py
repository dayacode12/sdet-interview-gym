"""Pydantic request schemas. Responses are plain dicts built from content modules."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class JavaRunRequest(BaseModel):
    question_id: str
    code: str


class SqlRunRequest(BaseModel):
    sql: str


class SqlSubmitRequest(BaseModel):
    sql: str
    duration_seconds: int = 0


class ScenarioSubmitRequest(BaseModel):
    answer: str
    duration_seconds: int = 0


class MockStartRequest(BaseModel):
    label: str | None = None


class MockAnswerRequest(BaseModel):
    question_id: str
    answer: str
    elapsed_seconds: int = 0


class FlashcardReviewRequest(BaseModel):
    confidence: Literal["again", "hard", "good", "easy"]


class QuizAnswerRequest(BaseModel):
    question_index: int = Field(ge=0, le=49)
    chosen_index: int = Field(ge=0, le=9)


class ActivityRequest(BaseModel):
    topic: str = Field(max_length=64)
    kind: Literal["study", "practice", "mock", "review"] = "study"
    seconds: int = Field(default=0, ge=0, le=24 * 3600)


class SettingsUpdateRequest(BaseModel):
    interview_datetime: str | None = None  # ISO string, editable in the UI
    target_role: str | None = None
    daily_goal_minutes: int | None = Field(default=None, ge=15, le=720)
