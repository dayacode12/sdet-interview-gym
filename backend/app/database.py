"""Database engine and session management. SQLite by default, PostgreSQL via DATABASE_URL."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def _normalize_url(url: str) -> str:
    """Render and some hosts hand out postgres:// URLs; SQLAlchemy 2 wants postgresql://."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


_url = _normalize_url(settings.database_url)

connect_args = {"check_same_thread": False} if _url.startswith("sqlite") else {}

engine = create_engine(
    _url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
