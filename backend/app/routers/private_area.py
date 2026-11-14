"""Unlock endpoint for the private area.

The public static site asks for a password here; the server decides whether
that password is right and hands back a short-lived token. Nothing about the
password or the gated content is shipped to the browser.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app.services import private_area

router = APIRouter(prefix="/api/private", tags=["private"])


class UnlockRequest(BaseModel):
    password: str = Field(min_length=1, max_length=200)


def _client(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/status")
def private_status(
    x_gym_access: Annotated[str | None, Header(alias="X-Gym-Access")] = None,
):
    """Whether the gate is configured and whether this caller already holds it."""
    return private_area.status(x_gym_access)


@router.post("/unlock")
def unlock(req: UnlockRequest, request: Request):
    try:
        token = private_area.unlock(req.password, client=_client(request))
    except private_area.PrivateAreaError as exc:
        message = str(exc)
        if not private_area.is_configured():
            raise HTTPException(status_code=503, detail=message) from exc
        status_code = 429 if "Too many" in message else 401
        raise HTTPException(status_code=status_code, detail=message) from exc
    return {"token": token, "expires_in": private_area.TOKEN_TTL_SECONDS}
