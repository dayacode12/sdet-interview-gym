"""SQLAlchemy models for user progress persistence."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Setting(Base):
    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[dict | str | None] = mapped_column(JSON, nullable=True)


class Attempt(Base):
    """One attempt at a Java coding question or SQL challenge."""

    __tablename__ = "attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_type: Mapped[str] = mapped_column(String(16))  # 'java' | 'sql'
    question_id: Mapped[str] = mapped_column(String(96))
    status: Mapped[str] = mapped_column(String(16))  # pass | fail | revealed
    score: Mapped[float] = mapped_column(Float, default=0.0)  # 0..100
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ScenarioSubmission(Base):
    __tablename__ = "scenario_submissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String(96))
    answer: Mapped[str] = mapped_column(Text)
    scores: Mapped[dict] = mapped_column(JSON, default=dict)
    feedback: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MockSession(Base):
    __tablename__ = "mock_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(128), default="Schwab SDET Mock Interview")
    started_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    dimension_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    question_scores: Mapped[list] = mapped_column(JSON, default=list)


class MockAnswer(Base):
    __tablename__ = "mock_answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer)
    question_id: Mapped[str] = mapped_column(String(96))
    section_id: Mapped[str] = mapped_column(String(64))
    answer: Mapped[str] = mapped_column(Text)
    elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    scores: Mapped[dict] = mapped_column(JSON, default=dict)
    feedback: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FlashcardState(Base):
    __tablename__ = "flashcard_states"
    card_id: Mapped[str] = mapped_column(String(96), primary_key=True)
    confidence: Mapped[str] = mapped_column(String(16), default="again")  # again|hard|good|easy
    known: Mapped[bool] = mapped_column(Boolean, default=False)
    reviews: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class QuizAnswer(Base):
    """IAM module quiz + automation self-check answers."""

    __tablename__ = "quiz_answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[str] = mapped_column(String(96))
    question_id: Mapped[str] = mapped_column(String(96))
    chosen: Mapped[str] = mapped_column(String(16))
    correct: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ActivityEvent(Base):
    """Time-on-topic tracking for analytics."""

    __tablename__ = "activity_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic: Mapped[str] = mapped_column(String(64))
    kind: Mapped[str] = mapped_column(String(32))  # study | practice | mock | review
    seconds: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Draft(Base):
    """Work-in-progress editor content, keyed by the frontend's storage key.

    The client mirrors every draft to localStorage (instant, offline) and to
    this table (follows the user across browsers and devices). On Render's
    free tier the SQLite file is ephemeral; setting DATABASE_URL to a real
    PostgreSQL makes drafts durable.
    """

    __tablename__ = "drafts"
    key: Mapped[str] = mapped_column(String(160), primary_key=True)
    text: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
