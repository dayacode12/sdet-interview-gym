"""SQL -> English translator: endpoint behavior + regression over every challenge."""
from __future__ import annotations

from app.content import sql_challenges


def test_explain_simple_select(client):
    resp = client.post(
        "/api/sql/explain",
        json={"sql": "SELECT username, status FROM USERS WHERE status = 'ACTIVE' ORDER BY username LIMIT 5"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["statement"] == "SELECT"
    assert "USERS" in body["tables"]
    labels = [c["label"] for c in body["clauses"]]
    assert "SELECT" in labels and "FROM" in labels and "WHERE" in labels
    assert "USERS" in body["summary"]
    assert "nothing is executed" in body["notes"][0]
    # Basics layer: beginner vocabulary grounded in this query's names.
    terms = {b["term"] for b in body["basics"]}
    assert "Table" in terms and "Column" in terms and "Field" in terms and "Row (record)" in terms
    table_basic = next(b for b in body["basics"] if b["term"] == "Table")
    assert "USERS" in table_basic["text"]
    row_basic = next(b for b in body["basics"] if b["term"] == "Row (record)")
    assert "at most 5" in row_basic["text"]


def test_explain_join_group_having(client):
    sql = (
        "SELECT u.username, COUNT(*) AS n FROM USERS u "
        "JOIN USER_ROLES ur ON u.user_id = ur.user_id "
        "GROUP BY u.username HAVING COUNT(*) > 1 ORDER BY n DESC"
    )
    resp = client.post("/api/sql/explain", json={"sql": sql})
    assert resp.status_code == 200
    labels = [c["label"] for c in resp.json()["clauses"]]
    assert any("JOIN" in label for label in labels)
    assert "GROUP BY" in labels
    assert "HAVING" in labels
    assert "the number of rows" in resp.json()["summary"]
    # Basics layer covers joins and aliases for this query.
    body = resp.json()
    terms = {b["term"] for b in body["basics"]}
    assert "Joined columns" in terms
    assert "Variable (alias)" in terms
    assert "Aggregate function" in terms
    joined = next(b for b in body["basics"] if b["term"] == "Joined columns")
    assert "u.user_id" in joined["text"] and "ur.user_id" in joined["text"]
    alias = next(b for b in body["basics"] if b["term"] == "Variable (alias)")
    assert "'u' is a nickname for the table USERS" in alias["text"]
    assert "'n' is the name given to the computed column COUNT(*)" in alias["text"]


def test_explain_union_and_cte(client):
    sql = (
        "WITH active AS (SELECT username FROM USERS WHERE status = 'ACTIVE') "
        "SELECT username FROM active UNION SELECT username FROM USERS WHERE status = 'LOCKED'"
    )
    resp = client.post("/api/sql/explain", json={"sql": sql})
    assert resp.status_code == 200
    labels = [c["label"] for c in resp.json()["clauses"]]
    assert "UNION" in labels
    assert "WITH" in labels


def test_explain_invalid_sql_rejected(client):
    resp = client.post("/api/sql/explain", json={"sql": "SELEC FRM USERS"})
    assert resp.status_code == 422
    assert "could not be parsed" in resp.json()["detail"]


def test_explain_non_select_rejected(client):
    resp = client.post("/api/sql/explain", json={"sql": "INSERT INTO USERS (username) VALUES ('x')"})
    assert resp.status_code == 422
    assert "Only SELECT" in resp.json()["detail"]


def test_explain_empty_rejected(client):
    resp = client.post("/api/sql/explain", json={"sql": "   "})
    assert resp.status_code == 422


def test_every_challenge_reference_answer_translates(client):
    """Regression: the reference answer of every SQL challenge must explain."""
    listing = sql_challenges.list_challenges()
    assert len(listing) >= 20
    for meta in listing:
        detail = sql_challenges.get_challenge(meta["id"])
        resp = client.post("/api/sql/explain", json={"sql": detail["expected_sql"]})
        assert resp.status_code == 200, f"{meta['id']}: {resp.text[:200]}"
        body = resp.json()
        assert body["summary"], f"{meta['id']} has an empty summary"
        assert body["clauses"], f"{meta['id']} has no clauses"
        assert body["tables"], f"{meta['id']} lists no tables"


def test_submit_includes_expected_english(client):
    listing = client.get("/api/sql/challenges").json()["challenges"]
    cid = listing[0]["id"]
    expected = sql_challenges.get_challenge(cid)["expected_sql"]
    resp = client.post(f"/api/sql/challenges/{cid}/submit", json={"sql": expected, "duration_seconds": 10})
    assert resp.status_code == 200
    body = resp.json()
    assert body["correct"] is True
    assert body["expected_english"]["summary"], "submit must include the reference query in English"
    assert body["expected_english"]["clauses"]


def test_reveal_includes_expected_english(client):
    listing = client.get("/api/sql/challenges").json()["challenges"]
    cid = listing[0]["id"]
    resp = client.post(f"/api/sql/challenges/{cid}/reveal")
    assert resp.status_code == 200
    body = resp.json()
    assert body["expected_english"]["summary"], "reveal must include the reference query in English"
