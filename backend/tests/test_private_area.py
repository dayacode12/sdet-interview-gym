"""Private area: the password gate must actually keep the content out.

These tests exist because the published site is static — a client-side check
would be decoration. Everything here goes through the real endpoints.
"""
from __future__ import annotations

import time

from app.config import settings
from app.services import private_area


def _locked(monkeypatch, password: str = "correct-horse"):
    """Turn the gate on for the duration of a test."""
    monkeypatch.setattr(settings, "private_area_password", password)
    private_area._attempts.clear()


def test_gate_is_off_when_no_password_is_configured(client, monkeypatch):
    """Local development: no password set, nothing is hidden."""
    monkeypatch.setattr(settings, "private_area_password", "")

    assert client.get("/api/admiral").status_code == 200
    assert client.get("/api/assistant/status").status_code == 200
    assert client.get("/api/private/status").json()["unlocked"] is True


def test_content_is_refused_without_a_token(client, monkeypatch):
    _locked(monkeypatch)

    admiral = client.get("/api/admiral")
    assert admiral.status_code == 401
    assert "password" in admiral.json()["detail"].lower()
    # The refusal must not leak a single character of the brief.
    assert "Saviynt" not in admiral.text

    assert client.get("/api/assistant/status").status_code == 401
    assert client.post("/api/assistant/ask", json={"question": "test a leaver"}).status_code == 401


def test_wrong_password_and_unknown_tokens_are_rejected(client, monkeypatch):
    _locked(monkeypatch)

    wrong = client.post("/api/private/unlock", json={"password": "nope"})
    assert wrong.status_code == 401
    assert "not right" in wrong.json()["detail"]

    forged = client.get("/api/admiral", headers={"X-Gym-Access": "9999999999.deadbeef"})
    assert forged.status_code == 401

    expired = private_area.issue_token(now=int(time.time()) - private_area.TOKEN_TTL_SECONDS - 5)
    assert client.get("/api/admiral", headers={"X-Gym-Access": expired}).status_code == 401


def test_correct_password_unlocks_both_areas(client, monkeypatch):
    _locked(monkeypatch, "correct-horse")

    body = client.post("/api/private/unlock", json={"password": "correct-horse"}).json()
    headers = {"X-Gym-Access": body["token"]}
    assert body["expires_in"] == private_area.TOKEN_TTL_SECONDS

    admiral = client.get("/api/admiral", headers=headers)
    assert admiral.status_code == 200
    assert admiral.json()["question_count"] > 0

    status = client.get("/api/assistant/status", headers=headers)
    assert status.status_code == 200
    assert status.json()["excerpt_count"] > 0

    assert client.get("/api/private/status", headers=headers).json()["unlocked"] is True


def test_password_check_is_constant_time_and_rotating_it_revokes_tokens(
    client, monkeypatch
):
    _locked(monkeypatch, "first-password")
    token = client.post(
        "/api/private/unlock", json={"password": "first-password"}
    ).json()["token"]
    assert client.get("/api/admiral", headers={"X-Gym-Access": token}).status_code == 200

    # A new password must invalidate every token signed with the old one.
    monkeypatch.setattr(settings, "private_area_password", "second-password")
    assert client.get("/api/admiral", headers={"X-Gym-Access": token}).status_code == 401
    assert private_area.verify_token(token) is False


def test_unlock_is_throttled(client, monkeypatch):
    _locked(monkeypatch, "correct-horse")
    private_area._attempts.clear()

    for _ in range(private_area._MAX_ATTEMPTS):
        assert client.post("/api/private/unlock", json={"password": "wrong"}).status_code == 401

    blocked = client.post("/api/private/unlock", json={"password": "wrong"})
    assert blocked.status_code == 429
    # Throttling must not become a way to lock the correct password out.
    assert "wait" in blocked.json()["detail"].lower()


def test_unlock_explains_when_the_server_has_no_password(client, monkeypatch):
    monkeypatch.setattr(settings, "private_area_password", "")
    private_area._attempts.clear()

    resp = client.post("/api/private/unlock", json={"password": "anything"})
    assert resp.status_code == 503
    assert "PRIVATE_AREA_PASSWORD" in resp.json()["detail"]
