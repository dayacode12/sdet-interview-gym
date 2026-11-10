"""Flashcard endpoints with simple spaced-repetition-ish state."""
from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.content import flashcards as content
from app.database import get_db
from app.models import FlashcardState
from app.schemas import FlashcardReviewRequest

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


@router.get("")
def list_flashcards(topic: str | None = None):
    cards = content.all_cards()
    if topic:
        cards = [c for c in cards if c["topic"].lower() == topic.lower()]
    return {"cards": cards, "topics": content.topics(), "total": len(content.all_cards())}


@router.get("/states")
def flashcard_states(db: Session = Depends(get_db)):
    states = db.query(FlashcardState).all()
    return {
        "states": {
            s.card_id: {
                "confidence": s.confidence,
                "known": s.known,
                "reviews": s.reviews,
                "updated_at": s.updated_at,
            }
            for s in states
        }
    }


@router.post("/{card_id}/review")
def review_flashcard(card_id: str, req: FlashcardReviewRequest, db: Session = Depends(get_db)):
    card = next((c for c in content.all_cards() if c["id"] == card_id), None)
    if card is None:
        raise HTTPException(404, "Card not found.")
    state = db.get(FlashcardState, card_id)
    if state is None:
        state = FlashcardState(card_id=card_id)
        db.add(state)
    state.confidence = req.confidence
    state.known = req.confidence in {"good", "easy"}
    state.reviews = (state.reviews or 0) + 1
    state.updated_at = dt.datetime.now(dt.timezone.utc)
    db.commit()
    return {"card_id": card_id, "confidence": state.confidence, "known": state.known, "reviews": state.reviews}


@router.post("/reset")
def reset_flashcards(db: Session = Depends(get_db)):
    deleted = db.query(FlashcardState).delete()
    db.commit()
    return {"reset": True, "deleted": deleted}
