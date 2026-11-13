"""Round 1 playbook endpoint: the Schwab-specific first-round question bank."""
from __future__ import annotations

from fastapi import APIRouter

from app.content import round1

router = APIRouter(prefix="/api/round1", tags=["round1"])


@router.get("")
def get_round1_playbook():
    return round1.get_round1()
