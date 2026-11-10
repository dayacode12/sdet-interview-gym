"""Mock interview: 60-minute simulated Schwab SDET interview with timed sections."""
from __future__ import annotations

MOCK_SECTIONS = [
    {
        "id": "intro",
        "title": "Introduction & Experience",
        "minutes": 5,
        "weight": 0.0,  # warm-up, unscored
        "questions": [
            {
                "id": "mock-intro-1",
                "prompt": "Tell me about yourself and your experience as an SDET.",
                "guidance": (
                    "90 seconds, structured: role, domain (IAM/IGA for insurance client), "
                    "stack (Java, Selenium/Playwright, TestNG, REST Assured, SQL), scale "
                    "(300+ cases, framework migration), and one sentence on why security "
                    "quality engineering. Do not recite your resume top to bottom."
                ),
                "model_answer": (
                    "I am an SDET with two-plus years at TCS, working for Admiral Group on "
                    "enterprise identity: Saviynt-based IAM with joiner-mover-leaver "
                    "workflows, access requests, certifications, provisioning and "
                    "reconciliation, plus CyberArk privileged access integrations. My "
                    "automation is Java-based — TestNG, Cucumber, REST Assured for APIs, "
                    "and I migrated our Selenium suite to Playwright, cutting regression "
                    "time by about a third. I validated dashboards and identity data "
                    "through SQL, mentored junior automation engineers, and I am drawn to "
                    "this role because security quality is exactly where my IAM testing "
                    "experience points: access control defects are incidents, not bugs."
                ),
                "keywords": ["SDET", "identity", "automation", "Selenium", "Playwright", "SQL", "mentoring"],
            },
            {
                "id": "mock-intro-2",
                "prompt": "Why are you interested in the Cyber Security QA team at Schwab?",
                "guidance": (
                    "Connect your actual IAM/IGA work to their security testing charter: "
                    "authentication, authorization, DLP. Be honest about years — position "
                    "depth and ownership instead."
                ),
                "model_answer": (
                    "My last two years have been security testing in practice, even though "
                    "my title said automation: I tested access control — who gets what "
                    "access, whether approvals are enforced, whether termination actually "
                    "revokes access. Those are exactly the questions a cybersecurity QA "
                    "team asks of every product it ships. I want to do that work where it "
                    "is the mission, with the scale Schwab operates at, and I am honest "
                    "that I am a two-year engineer: what I bring is depth in IAM testing, "
                    "framework ownership and the habit of validating claims with evidence."
                ),
                "keywords": ["access control", "security", "IAM", "honest", "depth"],
            },
        ],
    },
    {
        "id": "framework",
        "title": "Resume Deep Dive & Automation Framework",
        "minutes": 10,
        "weight": 0.2,
        "questions": [
            {
                "id": "mock-frame-1",
                "prompt": "Walk me through your automation framework architecture.",
                "guidance": "Layer by layer: tests, page/API objects, utilities, config, execution, reporting. Name concrete pieces you built.",
                "model_answer": (
                    "Test layer holds TestNG/Cucumber specs with zero locators. Below it, "
                    "page objects for UI and service clients for APIs — same operation "
                    "shape so flows are UI-or-API drivable. Utilities: wait wrappers, "
                    "assertion helpers that capture evidence on failure, test-data builders, "
                    "config reader. Execution: Maven, parallel TestNG, Azure DevOps/Jenkins; "
                    "Docker for consistent runners. Reporting attaches screenshots, "
                    "request/response logs and traces per failure. Tests are data-isolated "
                    "and self-cleaning for parallel safety. Design principle: a failure "
                    "must be diagnosable from the report alone."
                ),
                "keywords": ["Page Object", "TestNG", "layers", "parallel", "reporting", "evidence", "utilities", "config"],
            },
            {
                "id": "mock-frame-2",
                "prompt": "How did you migrate Selenium to Playwright and achieve roughly 33% faster execution?",
                "guidance": "Trigger, evaluation criteria, migration approach, what changed technically, measured outcome, coverage guarantee.",
                "model_answer": (
                    "Trigger: flaky explicit waits and a 60-minute regression blocking "
                    "feedback. We evaluated Playwright on wait handling, execution model, "
                    "diagnostics and migration cost. Migration was page-by-page with both "
                    "suites running in parallel and result comparison before removing "
                    "Selenium — coverage never dropped. Auto-waiting replaced most custom "
                    "wait code; browser contexts gave cheap parallelism; role-based "
                    "locators replaced fragile XPath. Measured from CI wall-clock over "
                    "repeated identical runs: median 60 to 40 minutes. Flakiness fell "
                    "because the race conditions the wait code was papering over "
                    "disappeared."
                ),
                "keywords": ["Playwright", "auto-waiting", "parallel", "contexts", "measurement", "coverage"],
            },
            {
                "id": "mock-frame-3",
                "prompt": "How do you handle flaky tests?",
                "guidance": "Classify first (product/environment/automation), then fix root cause; quarantine with owner and expiry; never retry-and-forget.",
                "model_answer": (
                    "First classify, because the three causes have three different owners. "
                    "Product: intermittent defect — file it, do not mask it. Environment: "
                    "flaky data or config — fix the environment or isolate data. "
                    "Automation: wait strategy or dependency between tests — fix the test. "
                    "True flakes get quarantined with an owner and expiry date so the "
                    "pipeline signal stays honest, and I track flake rate as a metric. "
                    "Retries are a last resort with reporting, because retry-and-forget "
                    "hides real defects. The Playwright migration reduced flakes at the "
                    "source by removing the race conditions."
                ),
                "keywords": ["classify", "product", "environment", "automation", "quarantine", "root cause", "retry"],
            },
        ],
    },
    {
        "id": "coding",
        "title": "Java, Selenium, Playwright & API Coding",
        "minutes": 15,
        "weight": 0.3,
        "questions": [
            {
                "id": "mock-code-1",
                "prompt": "Write Java code to find duplicate elements in an array.",
                "guidance": "HashSet, add() returns false on duplicate; LinkedHashSet to preserve order. O(n) time. Mention the reconciliation parallel.",
                "model_answer": (
                    "Set<Integer> seen = new HashSet<>(); Set<Integer> dupes = new "
                    "LinkedHashSet<>(); for (int x : nums) { if (!seen.add(x)) "
                    "dupes.add(x); } — add() returning false is the whole trick; "
                    "LinkedHashSet keeps first-seen order and prints each duplicate once. "
                    "O(n) time, O(n) space. This is also the reconciliation pattern: "
                    "detecting duplicate identity records from a nightly feed, which is "
                    "how I have used it in production automation."
                ),
                "keywords": ["HashSet", "LinkedHashSet", "add", "O(n)", "duplicate"],
            },
            {
                "id": "mock-code-2",
                "prompt": "Write an explicit wait in Selenium. Why not Thread.sleep()?",
                "guidance": "WebDriverWait + ExpectedConditions.elementToBeClickable; condition-based vs unconditional waiting.",
                "model_answer": (
                    "WebDriverWait wait = new WebDriverWait(driver, "
                    "Duration.ofSeconds(10)); "
                    "wait.until(ExpectedConditions.elementToBeClickable(By.id(\"login\"))).click(); "
                    "— the wait polls the condition and returns the instant it is true. "
                    "Thread.sleep(5000) always costs five seconds and still fails when the "
                    "app is slower, so it is both slower AND less reliable. In Playwright "
                    "this whole class of code disappears: actions auto-wait for visibility, "
                    "stability and enablement."
                ),
                "keywords": ["WebDriverWait", "ExpectedConditions", "Duration", "poll", "Thread.sleep", "auto-wait"],
            },
            {
                "id": "mock-code-3",
                "prompt": "Write a REST Assured test that validates user creation.",
                "guidance": "given/when/then, status code, body assertions; mention schema validation, auth header, response time, and DB verification as follow-ups.",
                "model_answer": (
                    "given().baseUri(url).contentType(ContentType.JSON).header(\"Authorization\", "
                    "\"Bearer \" + token).body(requestBody).when().post(\"/api/users\").then()"
                    ".statusCode(201).body(\"username\", equalTo(\"testuser\")).body(\"role\", "
                    "equalTo(\"EMPLOYEE\")); — plus matchesJsonSchemaInClasspath for the full "
                    "contract, .time(lessThan(2000L)) for latency, and — the part that "
                    "matters for IAM — a JDBC verification that the row exists with the "
                    "same values, because the API response and the database can disagree."
                ),
                "keywords": ["given", "when", "then", "statusCode", "equalTo", "Bearer", "schema", "database"],
            },
            {
                "id": "mock-code-4",
                "prompt": "How would you validate an API response against database records?",
                "guidance": "JDBC query, field-by-field comparison, timestamps/sync considerations, why API-vs-DB matters.",
                "model_answer": (
                    "Call the API, capture the response into a typed object, then query the "
                    "database via JDBC with the same filter the API used, and compare "
                    "field by field — not just counts. I account for sync lag: if the API "
                    "reads a replica or a cache, I retry briefly with a bounded wait "
                    "before declaring a mismatch. What this catches: the API returning "
                    "stale or transformed data, and the classic defect class where the UI "
                    "shows one role, the API another, and the database a third. That "
                    "three-way comparison is a standard pattern in my suite."
                ),
                "keywords": ["JDBC", "compare", "field", "sync", "replica", "cache", "retry"],
            },
            {
                "id": "mock-code-5",
                "prompt": "How do you test pagination on an API?",
                "guidance": "Page boundaries, paged sum equals total, cursor semantics, concurrent changes.",
                "model_answer": (
                    "I assert the invariant that catches most bugs: the sum of items "
                    "fetched across pages equals the reported total. Then boundaries: "
                    "page sizes at exact multiples (100, 200), partial pages (950 records), "
                    "and the empty-vs-end signalling — an invalid cursor must error "
                    "explicitly, not return an empty page that looks like the end. Then "
                    "dynamics: a record deleted mid-pagination, and rate limiting that "
                    "masquerades as empty pages. Consumers like reconciliation jobs "
                    "inherit these bugs silently, which is why I test the consumer's "
                    "import count too."
                ),
                "keywords": ["pagination", "cursor", "total", "boundary", "offset", "429"],
            },
        ],
    },
    {
        "id": "security",
        "title": "IAM, Cybersecurity & Scenario Testing",
        "minutes": 15,
        "weight": 0.3,
        "questions": [
            {
                "id": "mock-sec-1",
                "prompt": "Explain authentication vs authorization with examples.",
                "guidance": "Who you are vs what you may do; 401 vs 403; how you test each.",
                "model_answer": (
                    "Authentication proves identity — password, OTP, token validation. "
                    "Authorization decides permission — roles, entitlements, policy. The "
                    "HTTP encoding: 401 is missing or invalid credentials; 403 is valid "
                    "credentials lacking permission. I test them separately: invalid and "
                    "expired tokens must get 401; valid employee tokens on admin endpoints "
                    "must get 403; and I test authorization at the API layer directly, "
                    "because UI-level hiding is not enforcement."
                ),
                "keywords": ["authentication", "authorization", "401", "403", "token", "role", "API"],
            },
            {
                "id": "mock-sec-2",
                "prompt": "How would you test an employee termination workflow?",
                "guidance": "HR event -> IGA -> deprovisioning -> per-app validation -> login attempt. Include delayed event and partial failure cases.",
                "model_answer": (
                    "Walk the chain with evidence at each hop: the HR event exists and is "
                    "processed; the identity flips to terminated; a deprovisioning task "
                    "exists for EVERY target application; the logs show DISABLE/REVOKE "
                    "operations succeeded; the databases show accounts disabled and roles "
                    "removed — including privileged paths like CyberArk entries and API "
                    "keys; and an actual login attempt is denied. Then the failure "
                    "variants: delayed HR event, one application failing while others "
                    "succeed, retry behaviour, and duplicate execution not duplicating "
                    "accounts. I never certify termination from the IGA status field — "
                    "the target systems are the truth."
                ),
                "keywords": ["termination", "HR", "deprovision", "database", "login", "privileged", "retry", "target"],
            },
            {
                "id": "mock-sec-3",
                "prompt": "How would you test a scheduled reconciliation job that reports success but misses records?",
                "guidance": "Counts first (source/read/processed/failed/target), then record-level chasing: correlation, pagination, rate limits, idempotency.",
                "model_answer": (
                    "The scheduler's SUCCESS status is not business success — counts are. "
                    "Source records, records read, processed, failed, and present in the "
                    "target: 10,000 in, 9,500 landed means 500 records with names on them. "
                    "I chase them through the failure table (correlation rejects: null "
                    "emails, changed IDs), the API logs (pagination gaps, 429s), and "
                    "transformation errors. Then I test the failure modes deliberately: "
                    "page skipping, timeout mid-run with checkpoint resume, and running "
                    "the job twice — the second run must be a no-op, because "
                    "non-idempotent reconciliation creates duplicate identities."
                ),
                "keywords": ["counts", "reconciliation", "correlation", "pagination", "idempotent", "failure", "checkpoint"],
            },
            {
                "id": "mock-sec-4",
                "prompt": "How would you test MFA and SSO?",
                "guidance": "MFA: OTP lifecycle, lockout, bypass via direct API calls. SSO: SP/IdP flows, logout propagation, session termination.",
                "model_answer": (
                    "MFA: server-side sequence enforcement — calling the session API with "
                    "password-only state must fail; expired, replayed and wrong OTPs "
                    "rejected; lockout after N failures; recovery flows that re-verify "
                    "identity rather than bypass it. SSO: SP-initiated and IdP-initiated "
                    "logins, token validation, expiry, and logout as the headline test — "
                    "back-channel logout must kill every SP session, the browser back "
                    "button must not resurrect an authenticated page, and pre-logout "
                    "tokens must stop working. Incomplete logout is an account-takeover "
                    "vector, not a cosmetic bug."
                ),
                "keywords": ["MFA", "OTP", "lockout", "bypass", "SSO", "logout", "session", "token"],
            },
            {
                "id": "mock-sec-5",
                "prompt": "How would you test a DLP system?",
                "guidance": "Be honest about no hands-on DLP; show transferable policy-engine testing: policy as oracle, labelled corpus, channels, obfuscation, FP/FN rates, fail modes.",
                "model_answer": (
                    "Honestly: I have not implemented DLP, but it is a policy engine with "
                    "enforcement points, and that is the shape of testing I already do on "
                    "entitlement rules. The policy document is my oracle. I build a "
                    "labelled corpus — sensitive samples per classification plus benign "
                    "lookalikes — and drive it through every channel: email, upload, USB, "
                    "print. I probe obfuscation: renamed files, re-zipping, spaced digits, "
                    "format conversion, because content inspection must survive "
                    "transformation. I measure false positives and false negatives as "
                    "rates, not anecdotes. And I test engine-down behaviour against the "
                    "documented fail-open/fail-closed policy."
                ),
                "keywords": ["policy", "corpus", "channel", "obfuscation", "false positive", "false negative", "fail-open", "fail-closed"],
            },
        ],
    },
    {
        "id": "sql",
        "title": "SQL, Backend Validation & Troubleshooting",
        "minutes": 10,
        "weight": 0.15,
        "questions": [
            {
                "id": "mock-sql-1",
                "prompt": "Write a query to find inactive users who still have role assignments.",
                "guidance": "Three-table join, status filter; explain why the result is a security finding.",
                "model_answer": (
                    "SELECT u.username, r.role_name FROM users u JOIN user_roles ur ON "
                    "u.user_id = ur.user_id JOIN roles r ON ur.role_id = r.role_id WHERE "
                    "u.status <> 'ACTIVE'; — every row is a live access-control violation: "
                    "an inactive or terminated identity that can still act. This exact "
                    "query belongs in the automated termination regression, because it "
                    "is the database-level assertion that deprovisioning actually "
                    "happened."
                ),
                "keywords": ["JOIN", "status", "role", "WHERE", "security", "regression"],
            },
            {
                "id": "mock-sql-2",
                "prompt": "How would you find duplicate usernames and users with more than one role?",
                "guidance": "GROUP BY + HAVING for both; connect to reconciliation and privilege accumulation.",
                "model_answer": (
                    "Duplicates: SELECT username, COUNT(*) FROM users GROUP BY username "
                    "HAVING COUNT(*) > 1; — the reconciliation defect that creates "
                    "duplicate identities and double provisioning. Multiple roles: "
                    "SELECT u.username, COUNT(*) FROM users u JOIN user_roles ur ON "
                    "u.user_id = ur.user_id GROUP BY u.username HAVING COUNT(*) >= 2; — "
                    "and if I filter the roles to privileged levels first, that query "
                    "becomes a separation-of-duties check for privilege accumulation. "
                    "WHERE filters rows before grouping; HAVING filters the groups after."
                ),
                "keywords": ["GROUP BY", "HAVING", "COUNT", "duplicate", "privileged"],
            },
            {
                "id": "mock-sql-3",
                "prompt": "The dashboard count disagrees with your SQL. How do you investigate?",
                "guidance": "Definition-fair comparison first, then locate computation layer, staleness vs logic, three-way automated check.",
                "model_answer": (
                    "First make the comparison fair: same filters, same window, same "
                    "definitions — half of these are definition drift, like a dashboard "
                    "counting delegated decisions as completed while the raw query does "
                    "not. Then find where the number lives: live API, cached aggregate or "
                    "materialised table — that decides staleness versus logic bug. If the "
                    "gap survives beyond the documented refresh SLA, it is a defect with "
                    "a precise reproduction. And I leave behind the three-way automated "
                    "check — UI value, API value, SQL value — which is exactly the "
                    "dashboard validation I did against SQL in my current role."
                ),
                "keywords": ["filters", "definitions", "cache", "aggregate", "SLA", "three-way"],
            },
            {
                "id": "mock-sql-4",
                "prompt": "An intermittent automation failure appears every few nights. Walk me through your investigation.",
                "guidance": "Reproduce pattern, collect evidence on failure (logs, env), classify, isolate variables (data, timing, environment), fix root cause.",
                "model_answer": (
                    "I start with the pattern, not the code: which tests, which nights, "
                    "what else ran then — correlation with environment events (backups, "
                    "data refresh jobs, deployments) finds most of these. Evidence at "
                    "failure time is everything, so the framework captures screenshots, "
                    "DOM state, request/response logs and traces automatically. Then "
                    "isolate: same test on a freshly rebuilt environment with controlled "
                    "data; if it passes, the suspect is environment or timing; if it "
                    "fails, it is deterministic and I dig into the test's assumptions. "
                    "Classify honestly — product, environment or automation — because "
                    "the fix belongs to a different team in each case, and my job is to "
                    "hand them evidence, not guesses."
                ),
                "keywords": ["pattern", "evidence", "trace", "isolate", "environment", "classify", "root cause"],
            },
        ],
    },
    {
        "id": "behavioral",
        "title": "Leadership, Behavioral & Your Questions",
        "minutes": 5,
        "weight": 0.05,
        "questions": [
            {
                "id": "mock-beh-1",
                "prompt": "Tell me about a time you disagreed with a developer about a defect.",
                "guidance": "Evidence over opinion; reproduce at API/DB level; focus on user impact, not who is right.",
                "model_answer": (
                    "A developer marked a revoked-access defect as 'working as designed' "
                    "because the campaign UI showed the decision applied. I did not "
                    "argue from the UI — I produced evidence: the SQL join of revoked "
                    "decisions to current role assignments, plus the target application "
                    "still accepting the user's login. Data ended the discussion, and the "
                    "fix followed. My principle in disagreements is to move from opinions "
                    "to reproduction as fast as possible; the product's actual behaviour "
                    "is the referee."
                ),
                "keywords": ["evidence", "reproduce", "SQL", "respect", "impact"],
            },
            {
                "id": "mock-beh-2",
                "prompt": "How do you prioritise when everything is urgent?",
                "guidance": "Risk-based ordering: security > user impact > breadth; communicate early; make trade-offs visible.",
                "model_answer": (
                    "I order by risk and blast radius: security-relevant defects first — "
                    "access control failures are incidents, not bugs — then user-facing "
                    "breakage, then breadth of coverage. I make the trade-off visible "
                    "instead of silently absorbing it: here is what I will cover, here is "
                    "what slips, here is the exposure that leaves. Stakeholders can then "
                    "decide with information rather than being surprised later. And I "
                    "automate the repetitive parts of the urgent work so the next crunch "
                    "starts from a stronger baseline."
                ),
                "keywords": ["risk", "prioritise", "security", "communicate", "trade-off", "automate"],
            },
            {
                "id": "mock-beh-3",
                "prompt": "What questions do you have for us?",
                "guidance": "Ask about the security QA charter, what defects reach production today, automation maturity, and what success looks like in 6 months.",
                "model_answer": (
                    "What does the security QA charter own today — authentication and "
                    "authorization testing, DLP, or both? What defect classes currently "
                    "reach production and which one hurts most? How mature is the "
                    "automation estate for security flows versus manual review? And what "
                    "would make the team say, six months from now, that this hire "
                    "clearly worked? Those answers tell me where to create value first."
                ),
                "keywords": ["charter", "defects", "automation", "success"],
            },
        ],
    },
]


def get_plan() -> list[dict]:
    """Interview plan with cumulative time budget."""
    out = []
    elapsed = 0
    for section in MOCK_SECTIONS:
        out.append(
            {
                "id": section["id"],
                "title": section["title"],
                "minutes": section["minutes"],
                "weight": section["weight"],
                "start_minute": elapsed,
                "question_count": len(section["questions"]),
            }
        )
        elapsed += section["minutes"]
    return out


def all_questions() -> list[dict]:
    rows = []
    for section in MOCK_SECTIONS:
        for q in section["questions"]:
            rows.append(
                {
                    "id": q["id"],
                    "section_id": section["id"],
                    "prompt": q["prompt"],
                    "guidance": q["guidance"],
                    "model_answer": q["model_answer"],
                    "keywords": q["keywords"],
                }
            )
    return rows


def total_questions() -> int:
    return sum(len(s["questions"]) for s in MOCK_SECTIONS)
