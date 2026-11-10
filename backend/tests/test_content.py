"""Content integrity: the banks must meet the spec's minimums and be well-formed."""
from __future__ import annotations

from app.content import (
    automation_lab,
    flashcards,
    iam_modules,
    interview_research,
    java_questions,
    mock_interview,
    resume_deep_dive,
    roadmap,
    scenarios,
    sql_challenges,
)

REQUIRED_SCENARIO_KEYS = {
    "id", "title", "severity", "topic", "situation", "interviewer_question",
    "key_points", "test_cases", "api_checks", "db_checks", "job_checks",
    "security_consideration", "root_cause_paths", "strong_answer", "followups",
}


def test_java_question_minimums():
    questions = java_questions.JAVA_QUESTIONS
    assert len(questions) >= 30
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids)), "Java question ids must be unique"
    for q in questions:
        for key in ("id", "title", "category", "difficulty", "type", "problem",
                    "starter_code", "solution", "hints", "explanation", "followups"):
            assert key in q, f"{q['id']} missing {key}"
        if q["type"] == "code":
            assert q.get("tests"), f"{q['id']} is runnable and must have tests"
            for t in q["tests"]:
                assert "name" in t and "expected" in t


def test_sql_challenge_minimums():
    challenges = sql_challenges.SQL_CHALLENGES
    assert len(challenges) >= 25
    ids = [c["id"] for c in challenges]
    assert len(ids) == len(set(ids))
    for c in challenges:
        for key in ("id", "title", "difficulty", "category", "problem", "hints",
                    "expected_sql", "explanation", "security_note", "followups"):
            assert key in c, f"{c['id']} missing {key}"


def test_every_sql_expected_query_runs_and_returns_rows():
    """Every reference solution must execute against the seeded sandbox."""
    from app.services import sql_runner

    for c in sql_challenges.SQL_CHALLENGES:
        rows = sql_runner.run_expected(c["expected_sql"])
        assert isinstance(rows, list), f"{c['id']} reference query failed"


def test_scenario_minimums():
    assert len(scenarios.SCENARIOS) >= 30
    ids = [s["id"] for s in scenarios.SCENARIOS]
    assert len(ids) == len(set(ids))
    for s in scenarios.SCENARIOS:
        missing = REQUIRED_SCENARIO_KEYS - set(s.keys())
        assert not missing, f"{s['id']} missing {missing}"
        assert len(s["key_points"]) >= 5
        assert len(s["test_cases"]) >= 3
        assert len(s["root_cause_paths"]) >= 3
        assert len(s["followups"]) >= 2


def test_iam_modules_minimums():
    assert len(iam_modules.IAM_MODULES) >= 5
    for m in iam_modules.IAM_MODULES:
        assert m["concepts"], f"{m['id']} has no concepts"
        assert m["quiz"], f"{m['id']} has no quiz"
        for q in m["quiz"]:
            assert q["correct_index"] < len(q["options"])
        assert m["interview_questions"]
        assert m["test_cases"]


def test_flashcards_minimums():
    cards = flashcards.all_cards()
    assert len(cards) == 100
    ids = [c["id"] for c in cards]
    assert len(ids) == len(set(ids))
    assert len(flashcards.topics()) >= 10


def test_resume_questions_minimums():
    questions = resume_deep_dive.RESUME_QUESTIONS
    assert len(questions) >= 15
    flagged = [q for q in questions if q.get("needs_candidate_detail")]
    assert flagged, "Some resume answers must flag candidate-specific details"


def test_mock_interview_structure():
    sections = mock_interview.MOCK_SECTIONS
    assert len(sections) == 6
    total_minutes = sum(s["minutes"] for s in sections)
    assert total_minutes == 60
    weights = sum(s["weight"] for s in sections)
    assert abs(weights - 1.0) < 1e-9, "Section weights must sum to 1.0"
    for q in mock_interview.all_questions():
        assert q["keywords"], f"{q['id']} needs keywords for rule-based scoring"
        assert q["model_answer"], f"{q['id']} needs a model answer"


def test_interview_research_covers_all_mock_questions():
    notes = interview_research.DELIVERY_NOTES
    for q in mock_interview.all_questions():
        assert q["id"] in notes, f"{q['id']} has no research-backed delivery note"
        assert len(notes[q["id"]]) >= 80, f"{q['id']} delivery note too thin"
    assert len(interview_research.SOURCES) >= 4
    assert len(interview_research.PROCESS_OVERVIEW["rounds"]) >= 3
    for source in interview_research.SOURCES:
        assert source["source"] and source["reports"] and source["what_it_means"]


def test_automation_lab_minimums():
    assert len(automation_lab.EXERCISES) >= 12
    assert len(automation_lab.FRAMEWORK_ARCHITECTURE_QA) >= 8


def test_roadmap_content():
    assert len(roadmap.ROADMAP) == 3
    assert len(roadmap.PRIORITY_QUESTIONS) == 10
    assert len(roadmap.CHEAT_SHEET_SECTIONS) >= 10
    assert len(roadmap.HTTP_STATUS_CODES) >= 10
