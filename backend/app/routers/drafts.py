"""Editor draft endpoints: work-in-progress code and answers that follow the
user across browsers and devices. The client mirrors each draft to
localStorage (instant, offline) and syncs it here so opening the gym anywhere
shows the same programs."""
from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Draft
from app.schemas import DraftPutRequest

router = APIRouter(prefix="/api/drafts", tags=["drafts"])


def _as_ms(value: dt.datetime) -> int:
    """Epoch ms for the client's newer-wins merge. SQLite returns naive UTC
    datetimes; Postgres aware ones — both must compare identically."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt.timezone.utc)
    return int(value.timestamp() * 1000)


@router.get("")
def list_drafts(db: Session = Depends(get_db)):
    rows = db.query(Draft).order_by(Draft.updated_at.desc()).all()
    return {
        "drafts": [
            {"key": r.key, "text": r.text, "updated_ms": _as_ms(r.updated_at)} for r in rows
        ]
    }


@router.put("/{key:path}")
def put_draft(key: str, req: DraftPutRequest, db: Session = Depends(get_db)):
    # Two tabs (or a debounced push racing a focus sync) can create the same
    # key at once: both see "no row", both INSERT, one loses the unique
    # constraint. Retry as an update instead of returning a 500 the client
    # cannot retry on its own.
    for attempt in range(3):
        row = db.get(Draft, key)
        if row is None:
            row = Draft(key=key, text=req.text)
            db.add(row)
        else:
            row.text = req.text
            row.updated_at = dt.datetime.now(dt.timezone.utc)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            if attempt == 2:
                raise HTTPException(
                    status_code=409, detail="draft is being written concurrently; retry"
                )
            continue
        db.refresh(row)
        return {"key": row.key, "text": row.text, "updated_ms": _as_ms(row.updated_at)}
    raise HTTPException(status_code=409, detail="draft is being written concurrently; retry")


@router.delete("/{key:path}")
def delete_draft(key: str, db: Session = Depends(get_db)):
    """Idempotent delete — the client discards drafts fire-and-forget."""
    row = db.get(Draft, key)
    if row is not None:
        db.delete(row)
        db.commit()
    return {"deleted": row is not None, "key": key}
