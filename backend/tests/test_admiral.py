"""Admiral IGA playbook: content integrity and internal-evidence discipline."""
from __future__ import annotations

import re

TICKET_RE = re.compile(r"^IAMPAM-\d{3,5}$")


def test_admiral_payload_shape(client):
    resp = client.get("/api/admiral")
    assert resp.status_code == 200
    body = resp.json()

    assert body["title"] == "Admiral IGA Playbook"
    assert body["question_count"] == len(body["questions"])
    assert body["question_count"] >= 15
    assert body["role"]["company"] == "Admiral Group"
    assert "Identity Governance" in body["role"]["title"]
    assert len(body["ciam_stages"]) == 6
    assert len(body["domains"]) >= 6
    assert len(body["lifecycle"]["stages"]) == 4
    assert body["schwab_map"]


def test_admiral_questions_are_complete_and_unique(client):
    body = client.get("/api/admiral").json()
    source_ids = {s["id"] for s in body["sources"]}
    ids = []
    for q in body["questions"]:
        ids.append(q["id"])
        assert q["prompt"].strip()
        assert q["why"].strip()
        assert q["answer"].strip()
        assert len(q["key_points"]) >= 3, q["id"]
        assert q["follow_ups"]
        assert q["evidence"] in {"internal", "jira"}, q["id"]
        assert q["source_ids"], q["id"]
        assert set(q["source_ids"]) <= source_ids, (q["id"], set(q["source_ids"]) - source_ids)
    assert len(ids) == len(set(ids)), "question ids must be unique"


def test_admiral_tickets_are_internal_jira_keys(client):
    body = client.get("/api/admiral").json()
    keys = set()
    for stage in body["ciam_stages"]:
        keys.add(stage["ticket"])
    for domain in body["domains"]:
        for ticket in domain["tickets"]:
            keys.add(ticket["key"])
            assert TICKET_RE.match(ticket["key"]), ticket["key"]
            assert ticket["url"].endswith(f"/browse/{ticket['key']}")
    for stage in body["ciam_stages"]:
        assert TICKET_RE.match(stage["ticket"]), stage["ticket"]
    assert len(keys) >= 20


def test_admiral_sources_are_only_the_provided_brief_and_internal_jira(client):
    """No public Admiral source exists for this material, and no vendor or web
    source was researched for it. The ledger must say exactly that."""
    body = client.get("/api/admiral").json()
    by_id = {s["id"]: s for s in body["sources"]}

    assert set(by_id) == {"role-brief", "jira-board"}
    assert by_id["role-brief"]["type"] == "internal"
    assert by_id["role-brief"]["url"] == ""
    assert by_id["jira-board"]["type"] == "jira"
    assert "SSO" in by_id["jira-board"]["publisher"]

    for source in body["sources"]:
        assert source["type"] in {"internal", "jira"}
        assert source["type"] != "official"

    # The disclaimer has to carry the honesty claim, not just the page copy.
    assert "No Admiral source was queried" in body["disclaimer"]


def test_admiral_answers_do_not_invent_metrics(client):
    """The brief has projects and ticket keys but no measured numbers. Any
    percentage, multiplier or user volume would be fabricated."""
    body = client.get("/api/admiral").json()
    text = " ".join(q["answer"] for q in body["questions"])
    text += " " + " ".join(d["script"] for d in body["domains"])
    text += " " + " ".join(s["detail"] for s in body["ciam_stages"])

    assert "%" not in text
    assert not re.search(r"\b\d+(?:\.\d+)?\s?(?:percent|x faster)\b", text, re.I)
    # Ticket keys are allowed; bare large user/record counts are not.
    assert not re.search(r"\b\d{1,3}(?:,\d{3})+\s+(?:users|records|accounts)\b", text, re.I)


def test_admiral_lifecycle_and_sprint_match_the_brief(client):
    body = client.get("/api/admiral").json()
    stage_tickets = [s["ticket"] for s in body["lifecycle"]["stages"]]
    assert stage_tickets == [
        "IAMPAM-8340",
        "IAMPAM-8194",
        "IAMPAM-8195",
        "IAMPAM-8341",
    ]

    sprint = {item["key"]: item for item in body["sprint"]["items"]}
    assert sprint["IAMPAM-9031"]["status"] == "In Test"
    assert sprint["IAMPAM-8983"]["status"] == "Ready and Refined"
    assert "Q4-NOV-1-2026" == body["sprint"]["name"]
