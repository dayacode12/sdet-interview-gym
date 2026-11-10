"""Mind map endpoint: the clickable tree of everything in the gym."""
from __future__ import annotations

from fastapi import APIRouter

from app.content import mind_map

router = APIRouter(prefix="/api/mindmap", tags=["mindmap"])


@router.get("")
def get_mind_map():
    return {"root": mind_map.build_tree()}
