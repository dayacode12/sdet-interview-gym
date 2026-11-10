"""Field research behind the mock interview.

Sources are PUBLICLY REPORTED interview themes and Schwab's own published
careers guidance — collected from job portals (Glassdoor, AmbitionBox),
candidate reports (Reddit) and Schwab's careers site. They are NOT leaked
internal material, and none of it is claimed to be an official question bank.

Every claim below is attributed to the site it was reported on, and the mock
interview remains labelled as predicted questions informed by this research.
"""

SOURCES = [
    {
        "source": "Glassdoor — Charles Schwab QA SDET interview report (India)",
        "reports": (
            "First round was a Talent Acquisition connect. Second round was "
            "technical, conducted by EY, and tested knowledge on Java and "
            "automation concepts."
        ),
        "what_it_means": (
            "Expect a recruiter screen, then a Java-heavy technical round — "
            "possibly run by a partner firm. Java fundamentals and automation "
            "concepts carry real weight."
        ),
    },
    {
        "source": "Glassdoor — Charles Schwab Software QA Automation Engineer report",
        "reports": (
            "First three interviews were mostly talking with no whiteboard. The "
            "final interview was a whiteboard on how to test microservices, then "
            "a coding exercise."
        ),
        "what_it_means": (
            "The differentiator round tests SYSTEMS thinking: how you break a "
            "distributed system into testable services and contracts — not just "
            "test syntax. Practice explaining a microservices test strategy on "
            "a whiteboard: service boundaries, contract tests, integration seams, "
            "data consistency between services."
        ),
    },
    {
        "source": "AmbitionBox — Charles Schwab interview questions page",
        "reports": (
            "Reported questions: 'Why Charles Schwab? Why this role?', 'Core "
            "values of the company and how you align', resume screening on "
            "experience."
        ),
        "what_it_means": (
            "Prepare a genuine why-Schwab answer tied to their values, and know "
            "every line of your resume — the screening digs into it."
        ),
    },
    {
        "source": "Schwab's own careers site (schwabjobs.com)",
        "reports": (
            "Behavioral-based interviewing with a minimum of three interviewers "
            "(a Talent Advisor and two hiring managers). 'Past behavior often "
            "predicts future behavior' — stories must be specific, relevant and "
            "recent. Values: earning client trust ethically and proactively, "
            "client-centric innovation, empowering fellow Schwabbies, stewardship "
            "of the brand. Background check and drug screening before start."
        ),
        "what_it_means": (
            "Use STAR with RECENT stories. Frame answers around client trust and "
            "integrity — for a cyber security QA role, protecting client data IS "
            "the client-trust story."
        ),
    },
    {
        "source": "Reddit — associate software engineer final interview report",
        "reports": (
            "Deep-dive on resume projects, OOP/DSA questions, one LeetCode-style "
            "problem, and 'why did you choose your frameworks'."
        ),
        "what_it_means": (
            "Expect 'why' questions on every framework choice you made — Selenium "
            "vs Playwright, TestNG, REST Assured. Have reasons, trade-offs and "
            "measured outcomes ready."
        ),
    },
]

PROCESS_OVERVIEW = {
    "rounds": [
        {
            "round": 1,
            "name": "Talent Advisor (recruiter) screen",
            "detail": (
                "Background, why Schwab, why this role, logistics. AmbitionBox-"
                "reported questions live here. Keep it to a crisp 90-second story."
            ),
        },
        {
            "round": 2,
            "name": "Technical round — Java + automation",
            "detail": (
                "Java knowledge and automation concepts (one report was conducted "
                "by EY). OOP fundamentals, collections, coding exercises, waits, "
                "locators, API testing."
            ),
        },
        {
            "round": 3,
            "name": "Whiteboard — testing strategy + coding",
            "detail": (
                "Reported as 'how to test microservices' plus a coding exercise. "
                "Talk through service contracts, data flow, integration and "
                "failure modes before writing anything."
            ),
        },
        {
            "round": 4,
            "name": "Behavioral panel — STAR, values",
            "detail": (
                "Two hiring managers typical. Specific, relevant, recent stories: "
                "trust, integrity, proactivity, collaboration, learning quickly."
            ),
        },
    ],
    "note": (
        "Structure varies by role and team; these rounds are what candidates have "
        "publicly reported. Schwab's own guide says at least three people "
        "interview you. Verify your specific loop with your recruiter."
    ),
}

REPORTED_THEMES = [
    "Java fundamentals and OOP — reported in the technical round for QA SDET.",
    "Automation concepts: Selenium, waits, locators, framework design.",
    "'How would you test microservices' — the reported whiteboard differentiator.",
    "A live coding exercise (LeetCode-easy level reported by engineers).",
    "Resume deep-dive: every project and framework choice gets a 'why'.",
    "Why Schwab, why this role, values alignment.",
    "Behavioral STAR: trust, integrity, proactive service, collaboration.",
    "Questions for the interviewer — Schwab's Talent Advisors expect them.",
]

# Per-question delivery notes: what interviewers reportedly probe, mapped to
# the mock interview question ids. Grounded in the reported themes above.
DELIVERY_NOTES = {
    "mock-intro-1": (
        "This is round 1 territory (Talent Advisor screen). Reported Schwab "
        "screens cover background and motivation before deep technical probing — "
        "so keep this crisp and confident, and land one memorable number (33% "
        "regression reduction, 300+ cases). Do not recite your resume."
    ),
    "mock-intro-2": (
        "'Why Charles Schwab? Why this role?' is literally an AmbitionBox-reported "
        "question, and 'core values and how you align' is another. Anchor your "
        "answer in their published values: client trust through integrity and "
        "proactive service. For cyber security QA that is natural — access control "
        "defects break client trust in a financial institution."
    ),
    "mock-frame-1": (
        "Glassdoor reports a whiteboard round on testing MICROSERVICES — expect "
        "your architecture answer to be pushed toward service boundaries: how "
        "your framework tests services in isolation (contract/mocking) versus "
        "end-to-end flows. Name the layers, then volunteer where you would mock "
        "service dependencies and where you would not."
    ),
    "mock-frame-2": (
        "Reddit reports 'why did you choose your frameworks' as a real probe. Have "
        "the alternatives comparison ready (Playwright vs Cypress vs staying on "
        "Selenium) and the measurement method — reported interviews dig into "
        "whether your 33% claim survives scrutiny: same suite, same environment, "
        "multiple runs, median not best-case."
    ),
    "mock-frame-3": (
        "Schwab behavioral values include proactive service — frame flaky-test "
        "handling as protecting the team's signal, not firefighting. The "
        "classification habit (product/environment/automation) demonstrates "
        "the evidence-over-opinion mindset they screen for."
    ),
    "mock-code-1": (
        "The QA SDET technical round reportedly tested Java knowledge hard. "
        "Deliver the one-liner HashSet trick from muscle memory, then the "
        "complexity, then the IAM parallel (reconciliation duplicate detection) — "
        "the last part is what separates you from memorized answers."
    ),
    "mock-code-2": (
        "Classic Selenium probe in the reported technical round. The key phrase "
        "to land: condition-based waiting polls until true; sleep() is both "
        "slower AND less reliable. Then bridge to Playwright auto-waiting — "
        "interviewers reported asking why you migrated."
    ),
    "mock-code-3": (
        "API testing appears in both the technical round and the microservices "
        "whiteboard. After the syntax, volunteer the contract idea: schema "
        "validation is the contract test of an API — that sentence signals "
        "microservices fluency."
    ),
    "mock-code-4": (
        "This maps directly to the reported whiteboard theme: testing across "
        "service boundaries where the API sits in front of a database. Emphasize "
        "field-by-field comparison and bounded waits for eventual consistency — "
        "a distributed-systems word that lands well in that round."
    ),
    "mock-code-5": (
        "Pagination is the reported kind of API problem that hides "
        "microservices defects: page skipping, cursor semantics, 429s. The "
        "invariant framing (sum across pages equals total) is your whiteboard "
        "hook."
    ),
    "mock-sec-1": (
        "Core security-QA screening question. AmbitionBox-reported Schwab "
        "questions are motivation-based; the technical panel reportedly brings "
        "the domain depth — 401 vs 403 with the API-level enforcement point is "
        "the expected senior-quality signal."
    ),
    "mock-sec-2": (
        "This is your strongest story: you have run termination testing for a "
        "real IAM platform. Deliver the evidence chain (HR -> IGA -> target "
        "systems -> login attempt) with confidence — reported Schwab interviewers "
        "push from talking to whiteboard, so offer to draw the chain."
    ),
    "mock-sec-3": (
        "Reconciliation testing demonstrates exactly the microservices "
        "whiteboard skill reported on Glassdoor: cross-system data flow, "
        "failure modes, idempotency. Lead with counts, then record-level "
        "chasing, then the double-run idempotency test."
    ),
    "mock-sec-4": (
        "MFA/SSO questions test whether you think like an attacker. The "
        "bypass-via-direct-API-call point is the differentiator; the logout-"
        "propagation angle shows you know account-takeover vectors. Financial "
        "institutions feel both viscerally."
    ),
    "mock-sec-5": (
        "Honesty is the play here — Schwab's values explicitly include integrity, "
        "and their behavioral guide rewards candidates who admit limits and "
        "show transferable skill. Saying 'no hands-on DLP, here is how policy-"
        "engine testing transfers' reads as senior, not junior."
    ),
    "mock-sql-1": (
        "SQL is standard in the reported technical rounds. Deliver the query "
        "cleanly, then the security framing — every returned row is an access-"
        "control violation. That framing is why a cyber security QA team cares "
        "about your SQL."
    ),
    "mock-sql-2": (
        "GROUP BY + HAVING is the classic follow-up to the duplicate-array Java "
        "question — expect both in one technical round. The pivot to separation-"
        "of-duties (privilege accumulation) shows IAM domain depth."
    ),
    "mock-sql-3": (
        "Dashboard-vs-database disputes are exactly what they hired you for in "
        "your current role — this is a resume-deep-dive question in disguise. "
        "Reported rounds dig into real past work; give the real example and the "
        "three-way automated check you left behind."
    ),
    "mock-sql-4": (
        "Reported Schwab rounds move from talking to whiteboard exercises — "
        "troubleshooting scenarios test how you think. Talk through the pattern-"
        "first approach out loud; narrating your reasoning IS the assessment."
    ),
    "mock-beh-1": (
        "Schwab's behavioral guide: specific, relevant, recent — STAR with real "
        "names of artifacts (the SQL join, the login attempt). Their first "
        "published value is earning client trust ethically; a disagreement "
        "settled by evidence rather than volume is that value in practice."
    ),
    "mock-beh-2": (
        "Reported behavioral themes include managing competing priorities. "
        "Schwab values proactive communication — 'make the trade-off visible' is "
        "the phrase that separates engineered prioritisation from heroic "
        "absorption."
    ),
    "mock-beh-3": (
        "Schwab's Talent Advisors publish a suggested question list: day-to-day "
        "work, how performance is measured, learning and advancement, "
        "collaboration. Your four questions map onto it — asking about defect "
        "classes that reach production is the security-specific one that shows "
        "you already think in risk terms."
    ),
}


def get_research() -> dict:
    return {
        "sources": SOURCES,
        "process": PROCESS_OVERVIEW,
        "reported_themes": REPORTED_THEMES,
        "disclaimer": (
            "These themes were publicly reported by candidates on job portals "
            "and drawn from Schwab's own careers pages. They are not leaked or "
            "official interview material. The mock questions remain predictions "
            "informed by this research."
        ),
    }


def delivery_note_for(question_id: str) -> str | None:
    return DELIVERY_NOTES.get(question_id)
