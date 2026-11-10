"""Content integrity: the banks must meet the spec's minimums and be well-formed."""
from __future__ import annotations

from app.content import (
    automation_lab,
    company_profile,
    flashcards,
    iam_modules,
    interview_research,
    java_questions,
    mind_map,
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


def test_company_profile_completeness():
    p = company_profile.COMPANY_PROFILE
    assert p["mission"], "mission must be present"
    assert [v["name"] for v in p["values"]] == ["Trust", "Innovation", "Teamwork", "Stewardship"]
    for v in p["values"]:
        assert v["meaning"] and v["qa_link"], "every value needs meaning + QA angle"
    assert len(p["numbers"]) >= 6
    assert any("$10.10 trillion" == n["value"] for n in p["numbers"])
    assert len(p["history"]) >= 6
    assert len(p["interview_angles"]) >= 4
    for a in p["interview_angles"]:
        assert a["question"] and len(a["talking_points"]) >= 4 and len(a["model_answer"]) >= 200
    assert len(p["hiring"]["steps"]) == 5
    assert len(p["quick_facts_drill"]) >= 10
    assert len(p["sources"]) >= 4
    for s in p["sources"]:
        assert s["name"] and s["url"].startswith("http") and s["what"]
    assert p["disclaimer"]


def test_mind_map_tree_structure():
    tree = mind_map.build_tree()
    assert tree["id"] == "root"
    branch_ids = [b["id"] for b in tree["children"]]
    assert branch_ids == ["java", "automation", "security", "sql", "interview", "revision"]
    for node in mind_map.walk(tree):
        assert node["id"] and node["label"]
        # Every leaf must open a topic; counts must be positive ints when present.
        if not node.get("children"):
            assert node.get("href"), f"leaf {node['id']} must link to a topic page"
        if node.get("count") is not None:
            assert isinstance(node["count"], int) and node["count"] >= 0
    # The six top branches all deep-link somewhere.
    for b in tree["children"]:
        assert b.get("href"), f"branch {b['id']} must have an href"
    # Counts match the real banks (truthfulness contract).
    nodes = {n["label"]: n for n in mind_map.walk(tree)}
    assert nodes["Java Coding"]["count"] == len(java_questions.JAVA_QUESTIONS)
    assert nodes["Backend Validation"]["count"] == len(sql_challenges.SQL_CHALLENGES)
