"""Admiral IGA playbook endpoint: the current-role reference brief."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.content import admiral_iga
from app.services.private_area import require_access

# Gated: this is a live interview brief, so the public site must unlock first.
router = APIRouter(
    prefix="/api/admiral", tags=["admiral"], dependencies=[Depends(require_access)]
)


@router.get("")
def get_admiral_playbook():
    return admiral_iga.get_admiral()
