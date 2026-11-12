"""API endpoint smoke tests via TestClient (real Java execution, real SQL grading)."""
from __future__ import annotations

from app.config import JAVA_MODE


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["java_mode"] in {"docker", "local", "disabled"}
    # Tests run on a throwaway SQLite file; report the real backing store.
    assert body["database"]["dialect"] == "sqlite"
    assert body["database"]["reachable"] is True


def test_dashboard(client):
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert body["content"]["java_questions"] >= 30
    assert "PREDICTED" in body["honesty"]


def test_java_list_and_detail(client):
    listing = client.get("/api/java/questions").json()["questions"]
    assert len(listing) >= 30
    qid = listing[0]["id"]
    assert all("solution" not in q for q in listing)
    detail = client.get(f"/api/java/questions/{qid}")
    assert detail.status_code == 200
    assert "solution" not in detail.json()
    reveal = client.post(f"/api/java/questions/{qid}/reveal")
    assert reveal.status_code == 200
    assert reveal.json()["solution"]


def test_java_run_correct_solution(client):
    if JAVA_MODE == "disabled":
        resp = client.post("/api/java/run", json={"question_id": "java-reverse-string", "code": "x"})
        assert resp.json()["ok"] is False
        return
    listing = client.get("/api/java/questions").json()["questions"]
    runnable = [q for q in listing if q["type"] == "code" and q["test_count"] > 0]
    assert runnable, "There must be runnable Java questions"
    # Use the stored solution of the first runnable question — it must pass.
    qid = runnable[0]["id"]
    solution = client.post(f"/api/java/questions/{qid}/reveal").json()["solution"]
    resp = client.post("/api/java/run", json={"question_id": qid, "code": solution})
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] == JAVA_MODE
    assert body["ok"] is True, f"stored solution failed: {body}"
    assert body["passed"] == body["total"]


def test_java_run_broken_solution(client):
    resp = client.post("/api/java/run", json={"question_id": "nope", "code": "public class Main {}"})
    assert resp.status_code == 404
    listing = client.get("/api/java/questions").json()["questions"]
    runnable = next(q for q in listing if q["type"] == "code" and q["test_count"] > 0)
    resp = client.post(
        "/api/java/run",
        json={
            "question_id": runnable["id"],
            "code": "public class Main { public static void main(String[] a){ System.out.println(\"wrong\"); } }",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is False


def test_java_run_compile_error_is_honest(client):
    listing = client.get("/api/java/questions").json()["questions"]
    runnable = next(q for q in listing if q["type"] == "code" and q["test_count"] > 0)
    resp = client.post(
        "/api/java/run",
        json={"question_id": runnable["id"], "code": "public class Main { broken }"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is False
    assert body.get("compile_error") or body.get("error")


def test_sql_flow(client):
    listing = client.get("/api/sql/challenges").json()["challenges"]
    assert len(listing) >= 25
    cid = listing[0]["id"]
    detail = client.get(f"/api/sql/challenges/{cid}")
    assert detail.status_code == 200
    assert "expected_sql" not in detail.json()
    # Playground run
    run = client.post("/api/sql/run", json={"sql": "SELECT COUNT(*) AS n FROM USERS"})
    assert run.status_code == 200
    assert run.json()["row_count"] == 1
    # Blocked write
    blocked = client.post("/api/sql/run", json={"sql": "DELETE FROM USERS"})
    assert blocked.status_code == 400
    # Correct submission uses the reference query and must pass.
    reveal = client.post(f"/api/sql/challenges/{cid}/reveal").json()
    submit = client.post(f"/api/sql/challenges/{cid}/submit", json={"sql": reveal["expected_sql"]})
    assert submit.status_code == 200
    assert submit.json()["correct"] is True


def test_sql_submit_wrong_answer(client):
    listing = client.get("/api/sql/challenges").json()["challenges"]
    cid = listing[0]["id"]
    resp = client.post(
        f"/api/sql/challenges/{cid}/submit",
        json={"sql": "SELECT 'x' AS fake FROM USERS LIMIT 1"},
    )
    assert resp.status_code == 200
    assert resp.json()["correct"] is False


def test_scenario_flow(client):
    listing = client.get("/api/scenarios").json()["scenarios"]
    assert len(listing) >= 30
    sid = listing[0]["id"]
    detail = client.get(f"/api/scenarios/{sid}")
    assert detail.status_code == 200
    assert "strong_answer" not in detail.json()
    resp = client.post(
        f"/api/scenarios/{sid}/submit",
        json={"answer": "I would check the IGA dashboard and confirm the user is terminated."},
    )
    assert resp.status_code == 200
    body = resp.json()
    ev = body["evaluation"]
    assert ev["method"].startswith("rule-based")
    assert set(ev["scores"]) == {
        "technical_accuracy", "practical_implementation",
        "problem_solving", "communication", "security_awareness",
    }
    assert "strong_answer" in body


def test_mock_flow(client):
    plan = client.get("/api/mock/plan").json()
    assert plan["total_minutes"] == 60
    assert plan["total_questions"] >= 20
    research = client.get("/api/mock/research")
    assert research.status_code == 200
    research_body = research.json()
    assert research_body["sources"] and research_body["reported_themes"]
    assert len(research_body["process"]["rounds"]) >= 3
    questions = client.get("/api/mock/questions").json()["questions"]
    assert all("model_answer" not in q for q in questions)
    start = client.post("/api/mock/start", json={}).json()
    session_id = start["session_id"]
    qid = questions[0]["id"]
    answer = client.post(
        f"/api/mock/{session_id}/answer",
        json={"question_id": qid, "answer": "Two years of IAM automation.", "elapsed_seconds": 60},
    )
    assert answer.status_code == 200
    assert "model_answer" in answer.json()
    assert isinstance(answer.json()["delivery_note"], str) and answer.json()["delivery_note"]
    finish = client.post(f"/api/mock/{session_id}/finish")
    assert finish.status_code == 200
    body = finish.json()
    assert body["total_questions"] >= 20
    assert 0 <= body["total_score"] <= 100


def test_flashcards_flow(client):
    data = client.get("/api/flashcards").json()
    assert data["total"] == 100
    card_id = data["cards"][0]["id"]
    resp = client.post(f"/api/flashcards/{card_id}/review", json={"confidence": "good"})
    assert resp.status_code == 200
    assert resp.json()["known"] is True
    states = client.get("/api/flashcards/states").json()["states"]
    assert card_id in states
    bad = client.post(f"/api/flashcards/{card_id}/review", json={"confidence": "perfect"})
    assert bad.status_code == 422


def test_iam_flow(client):
    modules = client.get("/api/iam/modules").json()["modules"]
    assert len(modules) >= 5
    mid = modules[0]["id"]
    detail = client.get(f"/api/iam/modules/{mid}")
    assert detail.status_code == 200
    quiz = detail.json()["quiz"]
    assert all("correct_index" not in q for q in quiz)
    resp = client.post(f"/api/iam/modules/{mid}/quiz", json={"question_index": 0, "chosen_index": 0})
    assert resp.status_code == 200
    assert "correct_index" in resp.json()


def test_automation_and_resume(client):
    exercises = client.get("/api/automation/exercises").json()["exercises"]
    assert len(exercises) >= 12
    eid = exercises[0]["id"]
    detail = client.get(f"/api/automation/exercises/{eid}")
    assert "solution" not in detail.json()
    reveal = client.post(f"/api/automation/exercises/{eid}/reveal")
    assert reveal.json()["solution"]
    arch = client.get("/api/automation/architecture").json()["questions"]
    assert len(arch) >= 8
    resume = client.get("/api/resume/questions").json()["questions"]
    assert len(resume) >= 15
    rid = resume[0]["id"]
    rdetail = client.get(f"/api/resume/questions/{rid}")
    assert "star" in rdetail.json()


def test_roadmap_cheatsheet_settings_analytics(client):
    roadmap = client.get("/api/roadmap").json()
    assert len(roadmap["roadmap"]) == 3
    cheat = client.get("/api/cheatsheet").json()
    assert len(cheat["sections"]) >= 10
    tricks = cheat["java_tricks"]
    assert tricks["mnemonic"] == "R-D-F-D-S-P-W-S-R-M"
    assert len(tricks["programs"]) == 10
    java_ids = {q["id"] for q in client.get("/api/java/questions").json()["questions"]}
    for program in tricks["programs"]:
        assert program["practice_id"] in java_ids, program["name"]
    assert len(tricks["traps"]) >= 7
    assert len(tricks["flashcards"]) == 10
    assert len(tricks["complexity"]) == 10
    settings_resp = client.get("/api/settings")
    assert settings_resp.status_code == 200
    assert settings_resp.json()["java_mode"] in {"docker", "local", "disabled"}
    update = client.put(
        "/api/settings",
        json={"interview_datetime": "2026-11-20T10:00:00", "daily_goal_minutes": 240},
    )
    assert update.status_code == 200
    assert update.json()["interview_datetime"] == "2026-11-20T10:00:00"
    summary = client.get("/api/analytics/summary")
    assert summary.status_code == 200
    body = summary.json()
    assert body["java"]["total"] >= 30
    assert body["flashcards"]["total"] == 100
    activity = client.post("/api/analytics/activity", json={"topic": "Java Lab", "kind": "practice", "seconds": 300})
    assert activity.status_code == 200


def test_unknown_ids_return_404(client):
    assert client.get("/api/java/questions/nope").status_code == 404
    assert client.get("/api/sql/challenges/nope").status_code == 404
    assert client.get("/api/scenarios/nope").status_code == 404
    assert client.get("/api/iam/modules/nope").status_code == 404
    assert client.get("/api/resume/questions/nope").status_code == 404
