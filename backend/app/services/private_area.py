"""Password gate for the private area (Admiral playbook + AI assistant).

The public site is a static build: anything it ships can be read by anyone.
So the password is checked here, on the server, and the protected endpoints
refuse to return content without a valid short-lived token. Nothing secret is
embedded in the published bundle.

Behaviour:
  * PRIVATE_AREA_PASSWORD unset  -> the gate is off (local development).
    This keeps `npm run dev` and the test suite frictionless.
  * PRIVATE_AREA_PASSWORD set    -> /api/admiral and /api/assistant/* require
    an `X-Gym-Access` token issued by POST /api/private/unlock.

The token is stateless: an expiry timestamp signed with a key derived from the
password itself. Rotating the password invalidates every outstanding token.
"""
from __future__ import annotations

import hashlib
import hmac
import time
from threading import Lock
from typing import Annotated

from fastapi import Header, HTTPException

from app.config import settings

TOKEN_TTL_SECONDS = 12 * 60 * 60

# Simple in-process throttle: the unlock endpoint is reachable from the open
# internet, so a password guess loop must not be free. Render runs one process
# per instance, which is enough for a personal site; a restart clears it.
_MAX_ATTEMPTS = 10
_ATTEMPT_WINDOW_SECONDS = 5 * 60
_attempts: dict[str, list[float]] = {}
_attempts_lock = Lock()


class PrivateAreaError(Exception):
    """Raised when the private area cannot be unlocked."""


def is_configured() -> bool:
    return bool(settings.private_area_password)


def _signing_key() -> bytes:
    return hashlib.sha256(
        f"sdet-gym-private-area|{settings.private_area_password}".encode("utf-8")
    ).digest()


def _sign(expires_at: int) -> str:
    return hmac.new(_signing_key(), str(expires_at).encode("ascii"), hashlib.sha256).hexdigest()


def issue_token(now: int | None = None) -> str:
    """Return a token valid for TOKEN_TTL_SECONDS."""
    expires_at = (now if now is not None else int(time.time())) + TOKEN_TTL_SECONDS
    return f"{expires_at}.{_sign(expires_at)}"


def verify_token(token: str, now: int | None = None) -> bool:
    """True when the token is well-formed, correctly signed and unexpired."""
    if not is_configured() or not token or len(token) > 96:
        return False
    try:
        raw_expiry, signature = token.split(".", 1)
        expires_at = int(raw_expiry)
    except (AttributeError, ValueError):
        return False
    if expires_at <= (now if now is not None else int(time.time())):
        return False
    return hmac.compare_digest(signature, _sign(expires_at))


def _client_key(client: str) -> str:
    return client or "unknown"


def _check_throttle(client: str, now: float) -> None:
    with _attempts_lock:
        history = [t for t in _attempts.get(client, []) if now - t < _ATTEMPT_WINDOW_SECONDS]
        if len(history) >= _MAX_ATTEMPTS:
            _attempts[client] = history
            raise PrivateAreaError(
                "Too many wrong attempts. Wait five minutes and try again."
            )
        _attempts[client] = history


def _record_failure(client: str, now: float) -> None:
    with _attempts_lock:
        history = [t for t in _attempts.get(client, []) if now - t < _ATTEMPT_WINDOW_SECONDS]
        history.append(now)
        _attempts[client] = history


def unlock(password: str, client: str = "local") -> str:
    """Check the password and return a token, or raise PrivateAreaError."""
    if not is_configured():
        raise PrivateAreaError(
            "The private area is not configured on this server. Set PRIVATE_AREA_PASSWORD."
        )
    now = time.time()
    _check_throttle(_client_key(client), now)
    if not password or not hmac.compare_digest(password, settings.private_area_password):
        _record_failure(_client_key(client), now)
        raise PrivateAreaError("That password is not right.")
    with _attempts_lock:
        _attempts.pop(_client_key(client), None)
    return issue_token()


def require_access(
    x_gym_access: Annotated[str | None, Header(alias="X-Gym-Access")] = None,
) -> None:
    """FastAPI dependency: 401s unless the request carries a valid token.

    No-op when PRIVATE_AREA_PASSWORD is unset, so local development and the
    test suite run without a login step.
    """
    if not is_configured():
        return
    if not verify_token(x_gym_access or ""):
        raise HTTPException(
            status_code=401,
            detail="This area is locked. Enter the access password to continue.",
            headers={"WWW-Authenticate": "Gym-Access"},
        )


def status(token: str | None) -> dict:
    return {
        "configured": is_configured(),
        "unlocked": (not is_configured()) or verify_token(token or ""),
        "token_ttl_seconds": TOKEN_TTL_SECONDS,
    }
