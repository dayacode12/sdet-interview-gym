"""In-app interview assistant endpoint (grounded in repo content)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.services import assistant
from app.services.private_area import require_access
from app.config import settings

# Gated: every assistant route spends Groq quota and answers from private
# playbook content, so it sits behind the same password as the Admiral page.
router = APIRouter(
    prefix="/api/assistant", tags=["assistant"], dependencies=[Depends(require_access)]
)

_ALLOWED_AUDIO_PREFIXES = ("audio/", "video/webm")


class HistoryTurn(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    # Generous cap: the UI replays prior answers, and answers are often longer
    # than 1500 characters. The service trims each turn again before prompting.
    content: str = Field(min_length=1, max_length=8000)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    page: str | None = Field(default=None, max_length=120)
    history: list[HistoryTurn] = Field(default_factory=list, max_length=8)


@router.get("/status")
def assistant_status():
    """Whether the assistant is configured, and how big the corpus is."""
    return assistant.status()


@router.post("/ask")
def ask_assistant(req: AskRequest):
    """Answer a question using only the repo's own content."""
    try:
        return assistant.ask(
            req.question,
            page=req.page,
            history=[turn.model_dump() for turn in req.history],
        )
    except assistant.AssistantUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Turn a short dictation clip into text (Groq Whisper, server-side).

    The browser's Web Speech API is unreliable on Chromium forks and behind
    VPNs, so the mic records a clip and posts it here instead.
    """
    content_type = (file.content_type or "").lower()
    if not content_type.startswith(_ALLOWED_AUDIO_PREFIXES):
        raise HTTPException(
            status_code=415,
            detail="Unsupported audio format. Send an audio/webm, audio/mp4 or audio/ogg clip.",
        )
    audio = await file.read(assistant.MAX_AUDIO_BYTES + 1)
    if len(audio) > assistant.MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=413,
            detail="The audio clip is too large (max 10 MB). Keep it under 90 seconds.",
        )
    try:
        text = assistant.transcribe(
            audio,
            filename=file.filename or "dictation.webm",
            content_type=content_type,
        )
    except assistant.AssistantUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except assistant.AssistantError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"text": text, "model": settings.groq_whisper_model}
