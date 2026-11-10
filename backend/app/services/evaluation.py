"""Answer evaluation: transparent rule-based rubric, optional LLM assist.

Rubric (from the interview prep spec):
  technical accuracy      30%
  practical implementation 25%
  problem solving          20%
  communication            15%
  security awareness       10%

The rule-based evaluator never pretends to understand language. It scores on
explicit, explainable signals — reference concept coverage, testing vocabulary,
structured-breakdown vocabulary, answer structure and security vocabulary — and
returns exactly which terms were matched or missed so the UI can show WHY a
score was given. When an LLM key is configured, the LLM grades against the same
rubric; on any error we fall back to the rule-based path and say so.
"""
from __future__ import annotations

import json
import re

import httpx

from app.config import settings

RUBRIC_WEIGHTS = {
    "technical_accuracy": 0.30,
    "practical_implementation": 0.25,
    "problem_solving": 0.20,
    "communication": 0.15,
    "security_awareness": 0.10,
}

DIMENSIONS = list(RUBRIC_WEIGHTS.keys())

# --- Vocabulary pools. These are honest heuristics, not hidden magic. ---

PRACTICAL_TERMS = [
    "test", "verify", "validate", "assert", "check", "execute", "run",
    "automate", "selenium", "playwright", "api", "database", "sql", "query",
    "endpoint", "request", "response", "reproduce", "log", "trace",
    "regression", "negative", "boundary", "positive", "mock", "stub",
    "pipeline", "jenkins", "ci", "framework", "report", "screenshot",
    "evidence", "retry", "cleanup", "test case", "test data", "locator",
    "wait", "flaky", "coverage", "script",
]

PROBLEM_SOLVING_TERMS = [
    "root cause", "why", "because", "first", "then", "next", "finally",
    "prioritize", "priority", "impact", "scope", "isolate", "reproduce",
    "debug", "investigate", "hypothesis", "analyze", "compare", "difference",
    "approach", "plan", "step", "sequence", "order", "break down", "narrow",
    "eliminate", "cause", "fix", "resolve", "mitigate", "risk", "if",
    "scenario", "edge case", "alternative", "trade off", "trial and error",
]

SECURITY_TERMS = [
    "security", "audit", "compliance", "privilege", "least privilege",
    "breach", "threat", "vulnerability", "attack", "unauthorized",
    "access control", "encryption", "pii", "sensitive", "confidential",
    "incident", "governance", "policy", "segregation", "sod", "insider",
    "exploit", "vault", "mfa", "authentication", "authorization", "revoke",
    "deprovision", "malicious", "regulation", "sox", "gdpr", "risk",
    "certification", "entitlement", "provisioning",
]

_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "you",
    "your", "they", "their", "have", "has", "had", "not", "but", "can",
    "will", "would", "should", "could", "into", "than", "then", "them",
    "there", "these", "those", "what", "when", "where", "which", "while",
    "about", "also", "each", "other", "some", "such", "only", "over",
    "must", "may", "might", "shall", "does", "done", "how", "why", "who",
    "its", "it's", "per", "via", "any", "all", "one", "two", "use", "used",
    "using", "see", "seen", "like", "get", "got", "let", "make", "made",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]+", " ", (text or "").lower())).strip()


def _word_count(text: str) -> int:
    return len((text or "").split())


def _unique_ratio(text: str) -> float:
    words = [w for w in _normalize(text).split() if w]
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def _matched_terms(normalized: str, terms: list[str]) -> list[str]:
    return [t for t in terms if t in normalized]


def _coverage_score(normalized: str, pool: list[str], target: int) -> tuple[float, list[str]]:
    """Score = matched/target, capped at 100. Returns (score, matched)."""
    matched = _matched_terms(normalized, pool)
    denom = max(1, min(target, len(pool)))
    score = round(min(100.0, 100.0 * len(matched) / denom), 1)
    return score, matched


def _key_point_coverage(normalized: str, key_points: list[str]) -> tuple[float, list[str], list[str]]:
    """A key point counts as covered when >= 40% of its significant words appear."""
    covered: list[str] = []
    missed: list[str] = []
    answer_tokens = set(normalized.split())
    for point in key_points:
        tokens = {
            w for w in _normalize(point).split()
            if len(w) > 3 and w not in _STOPWORDS
        }
        if not tokens:
            continue
        overlap = len(tokens & answer_tokens) / len(tokens)
        (covered if overlap >= 0.4 else missed).append(point)
    total = len(covered) + len(missed)
    score = round(100.0 * len(covered) / total, 1) if total else 50.0
    return score, covered, missed


def _communication_score(text: str) -> tuple[float, str]:
    """Length band + structure signals + lexical variety. Fully explainable."""
    words = _word_count(text)
    notes: list[str] = []
    if words == 0:
        return 0.0, "The answer is empty."
    if words < 25:
        score = 20.0
        notes.append(f"Very short ({words} words) — too thin to communicate an approach.")
    elif words < 60:
        score = 55.0
        notes.append(f"Short ({words} words) — interviewers expect roughly 150-300 words for scenario answers.")
    elif words <= 450:
        score = 80.0
        notes.append(f"Good length ({words} words).")
    else:
        score = 65.0
        notes.append(f"Long ({words} words) — risk of rambling; tighten to the strongest points.")
    structure = 0
    if re.search(r"^\s*\d+[.)]", text, re.MULTILINE):
        structure += 8
        notes.append("Uses numbered steps.")
    if re.search(r"^\s*[-*•]\s", text, re.MULTILINE):
        structure += 6
        notes.append("Uses bullet points.")
    if text.count("\n\n") >= 1 or len(re.findall(r"[.!?] +[A-Z]", text)) >= 2:
        structure += 4
        notes.append("Broken into sentences/paragraphs.")
    variety = _unique_ratio(text)
    if variety < 0.35:
        notes.append(f"Low word variety ({variety:.0%} unique) — repetition hurts clarity.")
    else:
        structure += min(4, int((variety - 0.35) * 20))
    score = min(100.0, score + structure)
    return round(score, 1), " ".join(notes)


def _rule_based(
    answer: str,
    keywords: list[str] | None,
    key_points: list[str] | None,
) -> dict:
    normalized = _normalize(answer)
    words = _word_count(answer)
    feedback: dict[str, dict] = {}
    scores: dict[str, float] = {}

    # Technical accuracy: reference concept coverage.
    if keywords:
        matched_kw = [k for k in keywords if _normalize(k) in normalized or _normalize(k).replace(" ", "") in normalized.replace(" ", "")]
        target = max(1, min(len(keywords), 8))
        tech = round(min(100.0, 100.0 * len(matched_kw) / target), 1)
        scores["technical_accuracy"] = tech
        feedback["technical_accuracy"] = {
            "matched": matched_kw,
            "missed": [k for k in keywords if k not in matched_kw],
            "note": f"Mentioned {len(matched_kw)} of {len(keywords)} reference concepts.",
        }
    elif key_points:
        tech, covered, missed = _key_point_coverage(normalized, key_points)
        scores["technical_accuracy"] = tech
        feedback["technical_accuracy"] = {
            "matched": covered,
            "missed": missed,
            "note": f"Addressed {len(covered)} of {len(covered) + len(missed)} key points.",
        }
    else:
        scores["technical_accuracy"] = 40.0
        feedback["technical_accuracy"] = {
            "matched": [],
            "missed": [],
            "note": "No reference checklist for this question; scored on structure only.",
        }

    # Practical implementation, problem solving, security awareness: vocabulary coverage.
    practical, p_matched = _coverage_score(normalized, PRACTICAL_TERMS, 6)
    scores["practical_implementation"] = practical
    feedback["practical_implementation"] = {
        "matched": p_matched,
        "note": "Grounded in concrete testing actions (tools, artefacts, checks).",
    }
    solving, s_matched = _coverage_score(normalized, PROBLEM_SOLVING_TERMS, 5)
    scores["problem_solving"] = solving
    feedback["problem_solving"] = {
        "matched": s_matched,
        "note": "Shows a structured breakdown (sequencing, causes, priorities, alternatives).",
    }
    security, sec_matched = _coverage_score(normalized, SECURITY_TERMS, 4)
    scores["security_awareness"] = security
    feedback["security_awareness"] = {
        "matched": sec_matched,
        "note": "Connects the answer to security impact and controls.",
    }

    comm, comm_note = _communication_score(answer)
    scores["communication"] = comm
    feedback["communication"] = {"matched": [], "note": comm_note}

    # A near-empty answer cannot demonstrate anything, whatever it contains.
    if words < 10:
        for dim in scores:
            scores[dim] = min(scores[dim], 25.0)

    overall = round(sum(RUBRIC_WEIGHTS[d] * scores[d] for d in DIMENSIONS), 1)
    return {"method": "rule-based", "scores": scores, "overall": overall, "feedback": feedback}


# ---------------------------- optional LLM path ----------------------------

_LLM_SYSTEM_PROMPT = (
    "You are an interview evaluator for a senior SDET / cybersecurity QA role. "
    "Grade the candidate's answer strictly against this rubric, each dimension 0-100:\n"
    "technical_accuracy (30%): correctness and depth of the technical content.\n"
    "practical_implementation (25%): concrete, executable test design (tools, data, checks).\n"
    "problem_solving (20%): structured approach, causes, priorities, trade-offs.\n"
    "communication (15%): clarity, structure, appropriate length.\n"
    "security_awareness (10%): connects the work to security impact and controls.\n"
    "Respond with STRICT JSON only: "
    '{"technical_accuracy": <int>, "practical_implementation": <int>, '
    '"problem_solving": <int>, "communication": <int>, "security_awareness": <int>, '
    '"feedback": {"technical_accuracy": "<one sentence>", "practical_implementation": "<one sentence>", '
    '"problem_solving": "<one sentence>", "communication": "<one sentence>", '
    '"security_awareness": "<one sentence>"}}'
)


def _llm_available() -> bool:
    return bool(settings.llm_api_key)


def _evaluate_with_llm(answer: str, reference: str, question: str) -> dict | None:
    payload = {
        "model": settings.llm_model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": _LLM_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"QUESTION:\n{question}\n\nREFERENCE ANSWER (model answer):\n{reference}\n\n"
                    f"CANDIDATE ANSWER:\n{answer}"
                ),
            },
        ],
    }
    try:
        resp = httpx.post(
            f"{settings.llm_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            json=payload,
            timeout=45,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        # Strip markdown code fences if present.
        content = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE).strip()
        parsed = json.loads(content)
        scores = {}
        for dim in DIMENSIONS:
            val = parsed.get(dim)
            if not isinstance(val, (int, float)) or not 0 <= val <= 100:
                return None
            scores[dim] = round(float(val), 1)
        fb = parsed.get("feedback") or {}
        feedback = {
            d: {"matched": [], "missed": [], "note": str(fb.get(d, ""))[:400]} for d in DIMENSIONS
        }
        overall = round(sum(RUBRIC_WEIGHTS[d] * scores[d] for d in DIMENSIONS), 1)
        return {"method": "llm", "scores": scores, "overall": overall, "feedback": feedback}
    except Exception:
        return None


def evaluate_answer(
    answer: str,
    *,
    question: str = "",
    keywords: list[str] | None = None,
    key_points: list[str] | None = None,
    reference_answer: str = "",
) -> dict:
    """Evaluate a free-text answer against the rubric.

    Prefers LLM grading when configured; otherwise transparent rule-based.
    Never fabricates: the rule-based path reports exactly what it measured.
    """
    answer = (answer or "").strip()
    if not answer:
        result = _rule_based("", keywords, key_points)
        result["feedback"]["communication"]["note"] = "No answer submitted."
        return result
    if _llm_available() and question:
        llm = _evaluate_with_llm(answer, reference_answer or "No reference answer provided.", question)
        if llm is not None:
            return llm
        result = _rule_based(answer, keywords, key_points)
        result["method"] = "rule-based (LLM unavailable, fell back)"
        return result
    return _rule_based(answer, keywords, key_points)


def llm_status() -> dict:
    return {
        "llm_enabled": _llm_available(),
        "llm_model": settings.llm_model if _llm_available() else None,
        "note": (
            "LLM evaluation enabled — answers are graded by the configured model against the rubric."
            if _llm_available()
            else "No LLM key configured — scoring uses the transparent rule-based rubric (keyword and structure signals)."
        ),
    }
