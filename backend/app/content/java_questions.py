"""All Java questions combined, with lookup helpers."""
from __future__ import annotations

from app.content.java_core_a import JAVA_CORE_PART_A
from app.content.java_core_b import JAVA_CORE_PART_B
from app.content.java_automation import JAVA_AUTOMATION_QUESTIONS

JAVA_QUESTIONS = JAVA_CORE_PART_A + JAVA_CORE_PART_B + JAVA_AUTOMATION_QUESTIONS

# Solution code is hidden from the list endpoint; exposed only per-question on demand.
HIDDEN_FIELDS = {"solution", "explanation", "tests"}


def list_questions() -> list[dict]:
    """Question metadata without solutions/tests (client fetches details per question)."""
    out = []
    for q in JAVA_QUESTIONS:
        meta = {k: v for k, v in q.items() if k not in HIDDEN_FIELDS}
        meta["test_count"] = len(q.get("tests", []))
        out.append(meta)
    return out


def get_question(question_id: str) -> dict | None:
    for q in JAVA_QUESTIONS:
        if q["id"] == question_id:
            return q
    return None


def category_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for q in JAVA_QUESTIONS:
        counts[q["category"]] = counts.get(q["category"], 0) + 1
    return counts
