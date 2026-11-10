"""Resume deep-dive: 15 questions built on the candidate's actual resume, with STAR scaffolds."""
from __future__ import annotations

RESUME_QUESTIONS = [
    {
        "id": "resume-300-tests",
        "title": "Walk me through your 300+ automated UI and API test cases",
        "category": "Automation portfolio",
        "needs_candidate_detail": True,
        "guidance": (
            "Structure: what the suites cover (login, JML flows, access requests, certifications, "
            "dashboards), the split between UI and API, where they run (CI schedule), and what they "
            "catch. Pick 2-3 representative tests and describe what they verify across layers. "
            "Be precise about what YOU built versus inherited."
        ),
        "star": {
            "situation": "Manual regression of IAM flows was slow and inconsistent across releases.",
            "task": "Build maintainable automation covering UI and API paths.",
            "action": "Design a layered framework (POM, service clients, utilities) and grow coverage suite by suite; 300+ cases across UI and API.",
            "result": "Repeatable nightly regression with evidence; defects caught before release. (Add your real numbers: execution time, defect escapes prevented.)",
        },
        "strong_answer": (
            "The suite is layered: API tests validate identity workflows — JML, access requests, "
            "provisioning, certifications — against REST endpoints and the database; UI tests cover "
            "the critical user paths like request submission, approval screens and dashboard "
            "reports. The split is deliberate: most assertions live in API tests because they are "
            "fast and stable, while UI tests focus on what only a browser can prove. Each test "
            "creates its own data and cleans up after itself, so the suite is order-independent "
            "and parallel-safe. In interviews I would quote the execution time, the pass rate "
            "and one concrete escape it caught."
        ),
        "followups": [
            "How did you decide UI vs API coverage for a workflow?",
            "What was your flakiness rate and how did you reduce it?",
            "Which test would you delete first, and why?",
        ],
    },
    {
        "id": "resume-playwright-migration",
        "title": "Tell me about the Selenium to Playwright migration",
        "category": "Framework evolution",
        "needs_candidate_detail": False,
        "guidance": (
            "Cover: the trigger (flakiness, execution time, maintenance), evaluation criteria, "
            "the migration approach (parallel run, page by page), locator strategy changes, wait "
            "strategy changes, and the measured outcome. The migration story is your strongest "
            "engineering-narrative asset — rehearse it until smooth."
        ),
        "star": {
            "situation": "Selenium suite had flaky waits and slow regression execution (~60 minutes).",
            "task": "Reduce execution time and flakiness without losing coverage.",
            "action": "Evaluated Playwright (auto-waiting, contexts, tracing); migrated page by page with parallel-run comparison; converted waits; kept POM structure.",
            "result": "~33% faster regression (about 60 -> 40 minutes) with improved stability and better failure diagnostics via traces.",
        },
        "strong_answer": (
            "The trigger was flakiness and a 60-minute regression run that blocked fast feedback. "
            "We evaluated Playwright on four criteria: wait handling (auto-waiting removes most "
            "race conditions), execution model (contexts give cheap parallelism), diagnostics "
            "(trace viewer shows DOM snapshots per step), and migration cost (POM structure "
            "transferred directly; locators moved to role-based). We migrated page by page with "
            "both suites running in parallel, comparing results before deleting the Selenium "
            "version — coverage never dropped. Regression went from roughly 60 to 40 minutes "
            "(about 33%), flakiness fell because explicit wait code disappeared, and CI failures "
            "became diagnosable from the trace alone. I can defend the measurement: same test set, "
            "same environment, repeated runs averaged before and after."
        ),
        "followups": [
            "Why not just fix the Selenium waits instead of migrating?",
            "What did auto-waiting actually replace in your code?",
            "How did you prove coverage did not drop during migration?",
        ],
    },
    {
        "id": "resume-33-percent",
        "title": "How exactly did you measure the 33% improvement?",
        "category": "Metrics",
        "needs_candidate_detail": False,
        "guidance": (
            "Numbers get challenged; have the measurement story ready. Method: same suite, same "
            "environment, same data, N runs averaged, wall-clock from pipeline logs, before and "
            "after. State the variance you observed."
        ),
        "star": {
            "situation": "Improvement claims need defensible evidence for stakeholders.",
            "task": "Quantify the migration outcome honestly.",
            "action": "Compared pipeline wall-clock times for identical suites and data across repeated runs before and after migration.",
            "result": "~60 to ~40 minutes median across runs; variance from environment load noted.",
        },
        "strong_answer": (
            "I measured from CI pipeline logs: the full regression job's wall-clock time, same "
            "test set, same environment, same seeded data, repeated across several nights — "
            "median around 60 minutes before, 40 after. I use median rather than a single run "
            "because environment noise creates outliers. I can also break the saving down: "
            "auto-waiting removed most sleep-and-retry time, and parallel contexts cut the UI "
            "segment specifically. If asked how I would prove it now, I would run the same "
            "measurement again and chart the distribution."
        ),
        "followups": [
            "What was the variance run to run?",
            "How much of the saving came from parallelism vs waiting?",
            "How would you present this to a sceptical engineering manager?",
        ],
    },
    {
        "id": "resume-framework-architecture",
        "title": "Explain your automation framework architecture",
        "category": "Framework",
        "needs_candidate_detail": True,
        "guidance": (
            "Draw it verbally layer by layer and name concrete classes/utilities you built. "
            "This is the most-asked architecture question in SDET interviews."
        ),
        "star": {
            "situation": "Multiple products and teams needed consistent automation with low duplication.",
            "task": "Design a layered, maintainable framework.",
            "action": "Layered design: test layer (TestNG/Cucumber), page objects + API clients, utilities (waits, assertions, data builders), config, execution (Maven, CI), reporting with evidence.",
            "result": "New flows automated quickly by juniors; failures diagnosable from artifacts.",
        },
        "strong_answer": (
            "Top-down: the test layer holds TestNG and Cucumber specs with no locators in them. "
            "Below it, page objects for UI and service clients for APIs — same shape, so a flow "
            "like 'submit access request' exists once and can be driven from UI or API tests. "
            "The utility layer has wait wrappers, assertion helpers with evidence capture, "
            "test-data builders and a config reader. Execution is Maven with parallel TestNG, "
            "wired into CI; reporting attaches screenshots, request/response logs and traces on "
            "failure. Data is per-test and self-cleaning, so parallel runs never interfere. "
            "The design principle throughout: a failure should be diagnosable from the report "
            "alone, without re-running anything."
        ),
        "followups": [
            "Where do your tests get credentials?",
            "How do you keep page objects from becoming god classes?",
            "How would this framework scale to 1,000 tests?",
        ],
    },
    {
        "id": "resume-saviynt-jml",
        "title": "Explain how you tested Saviynt JML workflows",
        "category": "IGA",
        "needs_candidate_detail": False,
        "guidance": (
            "Name the workflows (joiner creation, mover transfer, leaver termination), the "
            "integration points (HR feed, connectors), and the assertion depth (IGA state, "
            "provisioning logs, target DB, login attempt). The leaver story matters most."
        ),
        "star": {
            "situation": "JML defects create either blocked users or, worse, standing access for leavers.",
            "task": "Validate the full lifecycle through HR feed to target systems.",
            "action": "Automated joiner/mover/leaver flows with assertions at IGA, provisioning-log, target-database and login layers.",
            "result": "Lifecycle regressions caught pre-release; a deprovisioning gap found before it reached production.",
        },
        "strong_answer": (
            "Joiner: HR record feeds in, identity is correlated, birthright roles provision, and "
            "each target application account is created — I assert at the target database, not "
            "just the Saviynt UI. Mover: the critical assertion is that OLD department "
            "entitlements are revoked, because the mover gap — keeping both sets — is the classic "
            "defect. Leaver: termination event processed, deprovisioning task per application, "
            "role rows gone in the database, privileged vault entries removed, and an actual "
            "login attempt denied. Every step also validates audit logging, because for JML the "
            "audit trail is part of the requirement, not a nice-to-have."
        ),
        "followups": [
            "How did you simulate HR events in a test environment?",
            "What happened when a connector was down during termination?",
            "How did you keep test identities from polluting reporting?",
        ],
    },
    {
        "id": "resume-access-request-testing",
        "title": "How did you test access requests end-to-end?",
        "category": "IGA",
        "needs_candidate_detail": False,
        "guidance": (
            "Cover the state machine: submit -> route -> approve/reject -> provision -> verify. "
            "Include the negative paths (self-approval, rejection, tampering) and the SQL "
            "cross-checks."
        ),
        "star": {
            "situation": "Access grants must always trace to approvals.",
            "task": "Prove the request workflow grants only approved access.",
            "action": "Automated the full request lifecycle plus negative paths (self-approval, rejection, API tampering) with DB cross-checks.",
            "result": "Approval bypass and duplicate-request defects found before release.",
        },
        "strong_answer": (
            "I test it as a state machine. Positive path: request submitted routes to the right "
            "approver tier per policy, approval triggers provisioning, and the entitlement "
            "exists in the target application database — verified by SQL, not the UI alone. "
            "Negative paths get equal weight: rejection grants nothing, the requester cannot "
            "approve their own request through UI or API, calling the approve endpoint as the "
            "requester returns 403, and tampering with request IDs fails. I also verify "
            "duplicate submissions are idempotent, because request storms under slow feedback "
            "are real user behaviour, and duplicated grants are a security issue."
        ),
        "followups": [
            "How did you verify routing tiers (manager vs owner)?",
            "What happens on duplicate requests in your platform?",
            "How would you test emergency/exception approvals?",
        ],
    },
    {
        "id": "resume-certification-testing",
        "title": "How did you test access certifications?",
        "category": "IGA",
        "needs_candidate_detail": False,
        "guidance": (
            "Campaign lifecycle plus enforcement: population, reviewer assignment, decisions, "
            "downstream enforcement, statistics validation, overdue handling."
        ),
        "star": {
            "situation": "Campaign decisions that are not enforced downstream invalidate compliance.",
            "task": "Validate campaigns end-to-end including enforcement.",
            "action": "Automated campaign creation, decisions (approve/revoke/delegate/bulk), downstream revocation verification via SQL, and statistics-vs-dashboard checks.",
            "result": "Found a revoked-but-still-assigned gap and dashboard count mismatches before audits.",
        },
        "strong_answer": (
            "In three layers. Campaign mechanics: population rules include every in-scope user — I "
            "test that with SQL counts — reviewer assignment follows the manager hierarchy, and "
            "approve/revoke/delegate/bulk all work with audit entries. Enforcement: a REVOKE "
            "decision must remove the entitlement from the target application, which I verify "
            "with the join between certification decisions and current role assignments. "
            "Reporting: campaign statistics on the dashboard must equal the database query with "
            "the documented definitions. The defect class this catches — 'manager revoked it "
            "but the user still has it' — is exactly what an auditor would find."
        ),
        "followups": [
            "How did you handle delegated reviewers in tests?",
            "What auto-complete policy did overdue campaigns follow?",
            "How would you test a campaign for 50,000 users?",
        ],
    },
    {
        "id": "resume-ciam-reconciliation",
        "title": "Explain CIAM reconciliation testing",
        "category": "Integration",
        "needs_candidate_detail": True,
        "guidance": (
            "CIAM = customer identity: registrations, profile changes, deletions flowing between "
            "the customer-facing system and the IAM platform. Reconciliation = counts plus "
            "record-level comparison. Quantify with real volumes if possible."
        ),
        "star": {
            "situation": "Customer identity data must stay consistent between CIAM and the IAM platform.",
            "task": "Validate reconciliation accuracy and completeness.",
            "action": "Count-based plus record-level validation: source vs processed vs failed vs target; correlation rules; duplicate detection.",
            "result": "Detected missing-record and duplicate-identity defects before they hit customers.",
        },
        "strong_answer": (
            "Reconciliation testing is count math plus record-level chasing. Count math: source "
            "records, records read, processed, failed, and present in the target must reconcile — "
            "any gap is a defect with a name. Record level: when numbers disagree I chase the "
            "specific records through failure tables, correlation-rule rejects and pagination "
            "behaviour of the source API. For CIAM specifically I also watch customer-facing "
            "constraints: profile changes propagate, deletions actually remove downstream "
            "accounts, and re-registrations do not create duplicate customer identities. And "
            "idempotency: running reconciliation twice must change nothing."
        ),
        "followups": [
            "What volume did you reconcile nightly?",
            "What were the most common correlation failures?",
            "How did you test pagination edge cases?",
        ],
    },
    {
        "id": "resume-cyberark",
        "title": "Explain your CyberArk integration testing",
        "category": "PAM",
        "needs_candidate_detail": True,
        "guidance": (
            "Focus on integration points: privileged account provisioning to safes, role-to-safe "
            "mapping, rotation impact on dependent systems, and fail-closed behaviour. Be honest "
            "about depth — integration-level testing, not CyberArk administration."
        ),
        "star": {
            "situation": "Privileged credentials must be vaulted, rotated and audited.",
            "task": "Validate the IAM platform's integration with CyberArk.",
            "action": "Tested privileged account flows, safe mapping, rotation effects on dependent consumers, and approval requirements for privileged entitlements.",
            "result": "Verified vaulted credential flows and rotation impact without breaking dependent integrations.",
        },
        "strong_answer": (
            "My scope was the integration, not administering CyberArk. I tested privileged "
            "account flows: when the IAM platform grants a privileged entitlement, the account "
            "lands in the right safe with the right role mapping, and access to it requires the "
            "approval the policy demands. Rotation was the interesting part — when the vault "
            "rotates a credential, dependent integrations that consume it through the vault keep "
            "working, while anything caching the old credential fails, which is exactly the "
            "signal that it bypassed the vault. I also verified vault-unavailable behaviour "
            "matched the documented fail policy — for privileged access that means fail-closed. "
            "And every flow had audit assertions: who accessed what, when."
        ),
        "followups": [
            "What happens when a consumer caches a rotated credential?",
            "How would you test just-in-time elevation expiry?",
            "What does fail-closed mean for availability here?",
        ],
    },
    {
        "id": "resume-dashboard-sql",
        "title": "Explain dashboard validation through SQL",
        "category": "Data validation",
        "needs_candidate_detail": False,
        "guidance": (
            "The pattern: replicate the dashboard's documented query logic in SQL, compare "
            "numbers, file mismatches with precise filters. Name a real widget you validated."
        ),
        "star": {
            "situation": "IAM analytics dashboards drive governance decisions with unvalidated numbers.",
            "task": "Validate dashboard figures against the database.",
            "action": "Replicated widget query logic in SQL (counts by department, campaign stats, provisioning volumes) and compared against API/UI values.",
            "result": "Caught definition drift and stale-cache mismatches before stakeholders acted on wrong numbers.",
        },
        "strong_answer": (
            "The pattern is three-way validation. I take the widget's documented definition — "
            "the filters, the date window, what counts as 'active' — replicate it in SQL, and "
            "compare database vs API response vs rendered UI number. Mismatches split into "
            "definition drift (the dashboard counts delegated items as decided while the SQL "
            "does not), staleness (cached aggregates refreshing on a lag), or true calculation "
            "bugs. I file defects with the exact filter set and both timestamps so it is "
            "reproducible. This mattered because governance reviews acted on those numbers — "
            "wrong counts meant wrong decisions about who still had access."
        ),
        "followups": [
            "What mismatch did you find that surprised you?",
            "How did you automate the three-way check?",
            "What staleness SLA did you accept for cached widgets?",
        ],
    },
    {
        "id": "resume-complex-defect",
        "title": "Tell me about a complex defect you investigated",
        "category": "Debugging",
        "needs_candidate_detail": True,
        "guidance": (
            "Pick a cross-layer defect (UI vs API vs DB disagreement or an intermittent job "
            "failure). Structure: symptom, isolation steps layer by layer, root cause, fix, "
            "regression test, prevention. Have a second defect ready as backup."
        ),
        "star": {
            "situation": "Intermittent defect with contradictory evidence across layers.",
            "task": "Isolate the true root cause across UI, API, database and job logs.",
            "action": "Reproduced with controlled data; compared layer by layer; correlated timestamps across logs; narrowed to the failing hop.",
            "result": "Root cause identified and fixed; regression test added so the class of defect stays covered.",
        },
        "strong_answer": (
            "Best example: revoked entitlements still active for some users after a campaign. "
            "Symptom contradicted itself — the campaign UI said complete, the target app still "
            "showed access. I started with data: SQL joining certification decisions to current "
            "role assignments listed the affected users precisely. Then I pulled provisioning "
            "logs for those revoke operations: some showed FAILED with exhausted retries, some "
            "showed SUCCESS — the interesting split. The SUCCESS-but-still-assigned subset "
            "pointed at the target application ignoring the revoke for accounts it had "
            "re-correlated earlier. Root cause was a correlation mismatch on the target side; "
            "the fix was in reconciliation. My regression: the SQL join runs after every "
            "campaign in the suite — revoked means actually gone."
        ),
        "followups": [
            "How did you prove which component was at fault?",
            "What evidence convinced the dev team?",
            "How did you prevent the same class of defect elsewhere?",
        ],
    },
    {
        "id": "resume-mentoring",
        "title": "Tell me about mentoring junior automation engineers",
        "category": "Leadership",
        "needs_candidate_detail": True,
        "guidance": (
            "Give a concrete growth story: what the junior could not do, what you did, what "
            "changed. The JD asks for mentoring — this is a differentiator for a 2-year "
            "candidate, so make it specific and honest."
        ),
        "star": {
            "situation": "Junior engineers could write tests but not debug failures or design maintainable structure.",
            "task": "Grow them into independent contributors.",
            "action": "Paired on real defects (not toy tasks), reviewed PRs with reasoning, gave escalating ownership: fix one test, then own a module, then own the suite area.",
            "result": "Juniors took over module ownership and reviewed each other's work.",
        },
        "strong_answer": (
            "I mentored through debugging rather than lectures. When a junior's test failed, I "
            "did not fix it for them — we reproduced it together, looked at the trace and logs, "
            "and classified the failure: product, environment or automation. That single "
            "discipline changed how they wrote tests. Ownership escalated deliberately: first "
            "fixing flaky tests with me pairing, then owning a module's page objects, then "
            "owning a suite area including its CI health. Code review comments explained "
            "reasoning — why this locator, why this wait — so the standards survived without "
            "me. The JD's mentoring expectation is one I can speak to from actual experience, "
            "even at 2+ years."
        ),
        "followups": [
            "How did you handle a junior repeatedly writing flaky tests?",
            "How do you teach risk-based test selection?",
            "What did YOU learn from mentoring?",
        ],
    },
    {
        "id": "resume-testforge-ai",
        "title": "Explain your TestForge AI architecture",
        "category": "Personal project",
        "needs_candidate_detail": True,
        "guidance": (
            "Personal infrastructure project: describe the problem, components, tech choices and "
            "what works today. Scope honestly — say what is running versus planned."
        ),
        "star": {
            "situation": "Distributed automation execution needs infrastructure, not just scripts.",
            "task": "Build a platform to orchestrate test execution at scale as a personal project.",
            "action": "Designed distributed execution infrastructure with a control plane, worker nodes, containerised runners and result aggregation.",
            "result": "A working personal platform demonstrating infrastructure thinking beyond test scripting.",
        },
        "strong_answer": (
            "TestForge AI is my distributed automation infrastructure project: a control plane "
            "that queues test executions, worker nodes that run suites in containers, and "
            "aggregation of results with evidence into reports. The motivation was the gap I "
            "kept hitting at work: frameworks exist, but running them reliably at scale — "
            "isolated environments, parallel nodes, artefact collection — is its own "
            "engineering problem. It is a personal project, so I am precise about its state: "
            "the execution orchestration works; some advanced pieces remain roadmap. What it "
            "demonstrates is that I think about test infrastructure as a product, which is the "
            "same mindset a quality-engineering team at Schwab would need."
        ),
        "followups": [
            "What is containerised in TestForge and why?",
            "How do workers report results and artefacts?",
            "What would you build next and why?",
        ],
    },
    {
        "id": "resume-cicd",
        "title": "Explain your CI/CD automation experience",
        "category": "CI/CD",
        "needs_candidate_detail": False,
        "guidance": (
            "Name the pipeline tool (Azure DevOps, Jenkins), what runs at which stage, quality "
            "gates, environment promotion, and evidence handling. Docker usage counts too."
        ),
        "star": {
            "situation": "Regression needs to run reliably on schedule and on every change.",
            "task": "Wire suites into CI/CD with quality gates and evidence.",
            "action": "Pipeline stages: unit -> API -> UI smoke on commit, full regression nightly; containerised runners; reports and artefacts published per run.",
            "result": "Predictable feedback cadence; failures diagnosable from artefacts without environment access.",
        },
        "strong_answer": (
            "Suites run at three cadences. On commit: unit and API smoke for fast feedback. "
            "Nightly: the full regression including UI, against a refreshed environment. "
            "Pre-release: the full suite plus performance-sensitive checks as a quality gate. "
            "In Azure DevOps and Jenkins I have configured both the pipeline definitions and "
            "the environments — Docker for runners so the execution environment is identical "
            "everywhere. Failures publish screenshots, request/response logs and traces "
            "attached to the run, so nobody needs environment access to triage. That last part "
            "is the piece teams appreciate most: diagnosable failures turn a red pipeline into "
            "a signal instead of noise."
        ),
        "followups": [
            "How did you handle flaky tests inside the gate?",
            "How do secrets reach the pipeline?",
            "How did containerised runners change reliability?",
        ],
    },
    {
        "id": "resume-automate-or-not",
        "title": "How do you decide which tests to automate?",
        "category": "Test strategy",
        "needs_candidate_detail": False,
        "guidance": (
            "Risk x repeatability x stability. Include what you deliberately do NOT automate. "
            "This answer signals seniority more than any tool knowledge."
        ),
        "star": {
            "situation": "Limited automation time; infinite possible tests.",
            "task": "Choose automation targets that pay back their maintenance cost.",
            "action": "Prioritised by business risk, execution frequency and technical stability; kept exploratory and one-off checks manual; pushed assertions down to API where possible.",
            "result": "Suite grew in value per test instead of just in count.",
        },
        "strong_answer": (
            "Three filters: risk (what breaks the business or security posture), repeatability "
            "(how often the flow runs — regression value), and stability (does the underlying "
            "feature change faster than the test pays back). Security-relevant flows like JML "
            "and access approvals are at the top regardless of churn, because a defect there "
            "is an incident. I push assertions down the stack: if a check can be an API or SQL "
            "assertion, it should not be a UI test. And I am explicit about what I do NOT "
            "automate: pure visual judgement, one-off exploratory checks, and features about "
            "to be redesigned — automated tests for doomed UIs are pure maintenance debt."
        ),
        "followups": [
            "Give an example where you automated the wrong thing.",
            "How do you handle tests for rapidly changing features?",
            "How does security testing change that prioritisation?",
        ],
    },
]


def list_resume_questions() -> list[dict]:
    return [
        {
            "id": q["id"],
            "title": q["title"],
            "category": q["category"],
            "needs_candidate_detail": q["needs_candidate_detail"],
        }
        for q in RESUME_QUESTIONS
    ]


def get_resume_question(question_id: str) -> dict | None:
    for q in RESUME_QUESTIONS:
        if q["id"] == question_id:
            return q
    return None
