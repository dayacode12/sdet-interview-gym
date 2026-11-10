"""Mind map tree for the /mind-map page.

The tree is computed from the actual content banks at request time, so every
count is truthful. Each node may carry an href; the frontend deep-links into
the target page (with ?q= / ?cat= / ?tool= / ?topic= / ?module= params) so
clicking a node opens that exact topic.
"""
from __future__ import annotations

from collections import Counter, OrderedDict

from app.content import (
    automation_lab,
    company_profile,
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


def _n(
    node_id: str,
    label: str,
    *,
    count: int | None = None,
    unit: str | None = None,
    note: str | None = None,
    href: str | None = None,
    children: list[dict] | None = None,
) -> dict:
    node: dict = {"id": node_id, "label": label}
    if count is not None:
        node["count"] = count
    if unit:
        node["unit"] = unit
    if note:
        node["note"] = note
    if href:
        node["href"] = href
    if children:
        node["children"] = children
    return node


def _java_branch() -> dict:
    counts = java_questions.category_counts()
    children = [
        _n(
            f"java-cat-{i}",
            cat,
            count=n,
            unit="questions",
            href=f"/java-lab?cat={cat.replace(' ', '%20')}",
        )
        for i, (cat, n) in enumerate(counts.items())
    ]
    return _n(
        "java",
        "Java Coding",
        count=len(java_questions.JAVA_QUESTIONS),
        unit="questions",
        note="Runnable on a real JVM — stdin/stdout contract, hidden tests.",
        href="/java-lab",
        children=children,
    )


def _automation_branch() -> dict:
    by_tool = Counter(e["tool"] for e in automation_lab.EXERCISES)
    tool_children = [
        _n(
            f"auto-tool-{i}",
            tool,
            count=n,
            unit="exercises",
            href=f"/automation-lab?tool={tool.replace(' ', '%20')}",
        )
        for i, (tool, n) in enumerate(by_tool.items())
    ]
    rest_count = len([e for e in automation_lab.EXERCISES if e["tool"] == "REST Assured"])
    return _n(
        "automation",
        "Test Automation",
        count=len(automation_lab.EXERCISES),
        unit="exercises",
        note="Write your attempt, then compare with the model solution.",
        href="/automation-lab",
        children=[
            _n(
                "automation-exercises",
                "Automation Lab",
                count=len(automation_lab.EXERCISES),
                unit="exercises",
                href="/automation-lab",
                children=tool_children,
            ),
            _n(
                "automation-arch",
                "Framework architecture Q&A",
                count=len(automation_lab.FRAMEWORK_ARCHITECTURE_QA),
                unit="questions",
                href="/automation-lab",
            ),
            _n(
                "api-lab",
                "API Testing Lab (REST Assured)",
                count=rest_count,
                unit="exercises",
                note="Auth matrices, request chaining, schema validation, DB cross-checks.",
                href="/api-lab",
            ),
        ],
    )


def _iam_branch() -> dict:
    module_children = [
        _n(
            m["id"],
            m["title"].split(":", 1)[-1].strip(),
            count=m.get("concept_count") or len(m.get("concepts", [])),
            unit="concepts",
            href=f"/iam-lab?module={m['id']}",
        )
        for m in iam_modules.IAM_MODULES
    ]
    topic_counts = Counter(s["topic"] for s in scenarios.SCENARIOS)
    scenario_children = [
        _n(
            f"scenario-topic-{i}",
            topic,
            count=n,
            unit="scenarios",
            href=f"/scenarios?topic={topic.replace(' ', '%20')}",
        )
        for i, (topic, n) in enumerate(sorted(topic_counts.items(), key=lambda kv: -kv[1]))
    ]
    return _n(
        "security",
        "Cyber Security & IAM",
        count=len(iam_modules.IAM_MODULES),
        unit="modules",
        note="The domains this role tests hardest: IGA, PAM, protocols, DLP.",
        href="/iam-lab",
        children=[
            _n(
                "iam-lab",
                "IAM Lab",
                count=len(iam_modules.IAM_MODULES),
                unit="modules",
                href="/iam-lab",
                children=module_children,
            ),
            _n(
                "scenarios",
                "Scenario Simulator",
                count=len(scenarios.SCENARIOS),
                unit="scenarios",
                note="Enterprise security QA situations, rubric-scored.",
                href="/scenarios",
                children=scenario_children,
            ),
        ],
    )


def _sql_branch() -> dict:
    by_cat = OrderedDict()
    for c in sql_challenges.SQL_CHALLENGES:
        by_cat.setdefault(c["category"], []).append(c)
    children = [
        _n(
            f"sql-cat-{i}",
            cat,
            count=len(items),
            unit="challenges",
            href=f"/sql-playground?q={items[0]['id']}",
        )
        for i, (cat, items) in enumerate(sorted(by_cat.items(), key=lambda kv: -len(kv[1])))
    ]
    return _n(
        "sql",
        "Backend Validation",
        count=len(sql_challenges.SQL_CHALLENGES),
        unit="challenges",
        note="Real queries, graded against reference answers on a sandbox dataset.",
        href="/sql-playground",
        children=children,
    )


def _interview_branch() -> dict:
    section_children = []
    for s in mock_interview.MOCK_SECTIONS:
        q_count = sum(
            1 for q in mock_interview.all_questions() if q.get("section_id") == s["id"]
        )
        weight_pct = round(s.get("weight", 0) * 100)
        note = f"{weight_pct}% of the hour" if weight_pct else "warm-up"
        section_children.append(
            _n(
                f"mock-section-{s['id']}",
                s["title"],
                count=q_count,
                unit="questions",
                note=note,
                href="/mock-interview",
            )
        )
    research_count = len(interview_research.DELIVERY_NOTES)
    return _n(
        "interview",
        "Interview Simulation",
        count=mock_interview.total_questions(),
        unit="questions",
        note="Timed, rubric-scored mock rounds across six sections.",
        href="/mock-interview",
        children=[
            _n(
                "mock-interview",
                "Mock Interview",
                count=mock_interview.total_questions(),
                unit="questions",
                href="/mock-interview",
                children=section_children,
            ),
            _n(
                "research",
                "Interview Research",
                count=research_count,
                unit="delivery notes",
                note="Attributed themes from public candidate reports (Glassdoor, AmbitionBox…).",
                href="/mock-interview",
            ),
            _n(
                "resume",
                "Resume Deep Dive",
                count=len(resume_deep_dive.RESUME_QUESTIONS),
                unit="questions",
                href="/resume",
            ),
            _n(
                "company",
                "Company Brief — Charles Schwab",
                count=len(company_profile.COMPANY_PROFILE["interview_angles"]),
                unit="model answers",
                note="Mission, values, history, tech org, hiring process.",
                href="/company",
            ),
        ],
    )


def _revision_branch() -> dict:
    topic_counts = Counter(c["topic"] for c in flashcards.all_cards())
    fc_children = [
        _n(
            f"fc-topic-{i}",
            topic,
            count=n,
            unit="cards",
            href=f"/flashcards?topic={topic.replace(' ', '%20')}",
        )
        for i, (topic, n) in enumerate(sorted(topic_counts.items(), key=lambda kv: -kv[1]))
    ]
    return _n(
        "revision",
        "Revision & Tracking",
        count=len(flashcards.all_cards()),
        unit="flashcards",
        note="Last-mile revision the morning of the interview.",
        href="/flashcards",
        children=[
            _n(
                "flashcards",
                "Flashcards",
                count=len(flashcards.all_cards()),
                unit="cards",
                href="/flashcards",
                children=fc_children,
            ),
            _n(
                "cheatsheet",
                "Cheat Sheet",
                count=len(roadmap.CHEAT_SHEET_SECTIONS),
                unit="sections",
                note="Java tricks memory framework + all-topic quick reference.",
                href="/cheatsheet",
            ),
            _n(
                "roadmap",
                "Roadmap",
                count=len(roadmap.ROADMAP),
                unit="phases",
                href="/roadmap",
            ),
            _n("analytics", "Progress Analytics", href="/analytics"),
        ],
    )


def build_tree() -> dict:
    branches = [
        _java_branch(),
        _automation_branch(),
        _iam_branch(),
        _sql_branch(),
        _interview_branch(),
        _revision_branch(),
    ]
    return _n(
        "root",
        "SDET Interview Gym",
        note="Daya Sagar · Schwab Cyber Security QA prep — every node opens its topic.",
        children=branches,
    )


def walk(node: dict):
    """Yield every node in the tree (depth-first)."""
    yield node
    for child in node.get("children", []):
        yield from walk(child)
