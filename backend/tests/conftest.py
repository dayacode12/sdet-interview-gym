"""Shared fixtures: isolated test DB + FastAPI TestClient."""
from __future__ import annotations

import os
import pathlib
import tempfile

# Must happen before any app import: point the app at a throwaway SQLite file.
_TMP = tempfile.mkdtemp(prefix="sdet-gym-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{pathlib.Path(_TMP) / 'test.db'.replace(chr(92), '/')}"
# Never touch an LLM during tests; keep rule-based scoring deterministic.
os.environ["LLM_API_KEY"] = ""
# Deterministic Java mode for the API tests (auto works too, but be explicit).
os.environ.setdefault("JAVA_EXECUTION_MODE", "auto")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
