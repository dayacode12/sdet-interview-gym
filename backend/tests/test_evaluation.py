"""Rule-based evaluation: transparent rubric behaviour."""
from __future__ import annotations

from app.services.evaluation import (
    DIMENSIONS,
    RUBRIC_WEIGHTS,
    evaluate_answer,
)


def test_rubric_weights_match_spec():
    assert RUBRIC_WEIGHTS == {
        "technical_accuracy": 0.30,
        "practical_implementation": 0.25,
        "problem_solving": 0.20,
        "communication": 0.15,
        "security_awareness": 0.10,
    }
    assert abs(sum(RUBRIC_WEIGHTS.values()) - 1.0) < 1e-9


def test_empty_answer_scores_zero():
    result = evaluate_answer("")
    assert result["method"] == "rule-based"
    assert all(v <= 25.0 for v in result["scores"].values())
    assert result["overall"] <= 25.0


def test_strong_answer_scores_above_weak_answer():
    strong = (
        "First I validate the termination event in the HR source system, then confirm the IGA "
        "platform processed it and generated a deprovisioning task for every connected application. "
        "I verify provisioning logs per target, check the target application database directly with "
        "SQL to confirm the account is disabled and roles are revoked, then attempt a login to prove "
        "access is denied. I also test privileged accounts including the CyberArk vault entry, "
        "delayed HR events, partial failures on one of five apps, and retry behaviour. The audit log "
        "must record the whole chain for compliance evidence, because a terminated user with live "
        "access is a critical security risk and an audit finding."
    )
    weak = "I would check the dashboard and ask the developer."
    strong_result = evaluate_answer(strong, key_points=[
        "Validate the termination event in the HR source system first.",
        "Confirm the IGA platform received and processed the event.",
        "Verify a deprovisioning task was generated for EVERY connected application.",
        "Check provisioning logs per target: DISABLE/REVOKE operations and their status.",
        "Verify the target application's database: account disabled, roles removed.",
        "Attempt login with the terminated user's credentials — access must be denied.",
    ])
    weak_result = evaluate_answer(weak, key_points=[
        "Validate the termination event in the HR source system first.",
        "Confirm the IGA platform received and processed the event.",
        "Verify a deprovisioning task was generated for EVERY connected application.",
        "Check provisioning logs per target: DISABLE/REVOKE operations and their status.",
        "Verify the target application's database: account disabled, roles removed.",
        "Attempt login with the terminated user's credentials — access must be denied.",
    ])
    assert strong_result["overall"] > weak_result["overall"]
    assert strong_result["scores"]["technical_accuracy"] > 50
    assert strong_result["scores"]["security_awareness"] > 50


def test_feedback_is_explainable():
    result = evaluate_answer(
        "I would write a Selenium test that verifies the login fails.",
        keywords=["Selenium", "login", "verify"],
    )
    tech = result["feedback"]["technical_accuracy"]
    assert "matched" in tech and "missed" in tech and "note" in tech
    assert "Selenium" in tech["matched"]


def test_keyword_matching_punctuation_insensitive():
    result = evaluate_answer(
        "Access control, least privilege, and access review are key.",
        keywords=["access control", "least privilege", "access review"],
    )
    assert result["feedback"]["technical_accuracy"]["matched"] == [
        "access control", "least privilege", "access review"
    ]


def test_overall_is_weighted_combination():
    result = evaluate_answer("A reasonable answer with some detail about testing.")
    expected = round(sum(RUBRIC_WEIGHTS[d] * result["scores"][d] for d in DIMENSIONS), 1)
    assert result["overall"] == expected


def test_no_llm_key_means_rule_based():
    result = evaluate_answer("Some answer.", question="Why test termination workflows?")
    assert result["method"].startswith("rule-based")
