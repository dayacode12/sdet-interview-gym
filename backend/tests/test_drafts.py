"""Draft sync endpoints: cross-device work-in-progress storage."""
from __future__ import annotations


def test_draft_roundtrip(client):
    resp = client.put("/api/drafts/java:two-sum", json={"text": "class Main {}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["key"] == "java:two-sum"
    assert body["text"] == "class Main {}"
    assert body["updated_ms"] > 0

    listed = client.get("/api/drafts").json()["drafts"]
    assert any(d["key"] == "java:two-sum" and d["text"] == "class Main {}" for d in listed)


def test_draft_upsert_overwrites_without_duplicates(client):
    client.put("/api/drafts/sql:playground", json={"text": "SELECT 1"})
    client.put("/api/drafts/sql:playground", json={"text": "SELECT 2"})
    listed = client.get("/api/drafts").json()["drafts"]
    matches = [d for d in listed if d["key"] == "sql:playground"]
    assert len(matches) == 1
    assert matches[0]["text"] == "SELECT 2"


def test_draft_insert_race_recovers_as_update(client, monkeypatch):
    """Two tabs creating the same key at once: the loser must retry as an
    update, not return a 500."""
    from sqlalchemy.orm import Session

    from app.models import Draft

    assert client.put("/api/drafts/round1:race", json={"text": "first"}).status_code == 200

    real_get = Session.get
    lied = {"done": False}

    def racing_get(self, entity, ident, *args, **kwargs):
        # Pretend the row did not exist for the endpoint's first read, exactly
        # like the request that loses the insert race.
        if entity is Draft and not lied["done"]:
            lied["done"] = True
            return None
        return real_get(self, entity, ident, *args, **kwargs)

    monkeypatch.setattr(Session, "get", racing_get)
    resp = client.put("/api/drafts/round1:race", json={"text": "second"})
    assert resp.status_code == 200
    assert resp.json()["text"] == "second"

    listed = client.get("/api/drafts").json()["drafts"]
    matches = [d for d in listed if d["key"] == "round1:race"]
    assert len(matches) == 1
    assert matches[0]["text"] == "second"


def test_draft_delete_is_idempotent(client):
    client.put("/api/drafts/scenario:response", json={"text": "draft"})
    first = client.delete("/api/drafts/scenario:response")
    assert first.status_code == 200 and first.json()["deleted"] is True
    second = client.delete("/api/drafts/scenario:response")
    assert second.status_code == 200 and second.json()["deleted"] is False
    listed = client.get("/api/drafts").json()["drafts"]
    assert all(d["key"] != "scenario:response" for d in listed)


def test_draft_keys_can_contain_colons_and_slashes(client):
    key = "java:arrays/reverse-words"
    resp = client.put(f"/api/drafts/{key}", json={"text": "// program"})
    assert resp.status_code == 200
    assert resp.json()["key"] == key
