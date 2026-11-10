"""Company knowledge endpoint: the Schwab brief for interview prep."""
from __future__ import annotations

from fastapi import APIRouter

from app.content import company_profile

router = APIRouter(prefix="/api/company", tags=["company"])


@router.get("")
def get_company_profile():
    return company_profile.COMPANY_PROFILE
