"""Admiral Group IGA SDET reference brief and interview playbook.

Evidence discipline:
  * "internal" = your own account of your current role: teams, stages, tools,
    responsibilities. It is true because you did the work, but it is not a
    public source anyone can check.
  * "jira"     = an IAMPAM ticket on Admiral's Jira. The ticket is real work
    history, but the URL requires Admiral SSO. Never present it as public.

Everything below comes from the role brief you pasted. No Admiral source was
queried or researched, and this app never fetches an Admiral URL. The brief
contains projects and ticket keys but no measured numbers, so nothing here
invents a percentage, a volume or a time saving. Where a number would help,
the answer says what you would measure rather than guessing it.
"""

from __future__ import annotations

ACCESSED = "2026-11-13"

JIRA_BOARD = (
    "https://admiralgroup.atlassian.net/jira/software/c/projects/IAMPAM/"
    "boards/2874?assignee=712020%3A4a3d941a-d097-4b54-8a48-b9c7c0125648"
)
JIRA_BROWSE = "https://admiralgroup.atlassian.net/browse/"


def _ticket(key: str, title: str, note: str) -> dict:
    return {
        "key": key,
        "title": title,
        "note": note,
        "url": f"{JIRA_BROWSE}{key}",
    }


SOURCES = [
    {
        "id": "role-brief",
        "name": "Your Admiral IGA SDET role brief",
        "publisher": "You / Daya Sagar (internal)",
        "type": "internal",
        "url": "",
        "supports": (
            "The team, the CIAM stages, the JML and certification scope, the "
            "four-stage QA lifecycle, the sprint and the colleagues named on "
            "this page. First-hand account, used exactly as provided."
        ),
        "accessed": ACCESSED,
    },
    {
        "id": "jira-board",
        "name": "IAMPAM sprint board and ticket history",
        "publisher": "Admiral Group Jira (internal, SSO required)",
        "type": "jira",
        "url": JIRA_BOARD,
        "supports": (
            "The ticket keys cited throughout: CIAM stages 1A-1E and 2, ARS "
            "forms, JML, certification regression, ServiceNow delegation, "
            "release hygiene and the race-condition defect. Internal evidence, "
            "not a public source. These links are never fetched by this app."
        ),
        "accessed": ACCESSED,
    },
]


ROLE = {
    "title": "SDET / QA Engineer — Identity Governance & Administration (IGA)",
    "company": "Admiral Group",
    "function": "Identity & Access Management (IAM)",
    "summary": (
        "Quality engineering for security-critical identity lifecycles, access "
        "governance and platform integrations. The work sits between Saviynt "
        "IGA, Transmit Security CIAM, Microsoft Entra ID / Active Directory and "
        "the applications that consume them, with ServiceNow in the approval "
        "path and Zephyr Scale / Jira holding the evidence."
    ),
    "focus": [
        "Customer Identity & Access Management (CIAM) reconciliation and correlation",
        "Joiner, mover and leaver lifecycle testing across multi-tier environments",
        "Access certification campaigns, escalation analytics and regression buckets",
        "Enterprise integrations: ServiceNow delegation, Workiva, AEP, Anaplan, CyberArk",
        "Automation framework development, release hygiene and defect investigation",
    ],
    "stack": [
        "Saviynt",
        "Transmit Security (CIAM)",
        "Microsoft Entra ID / Active Directory",
        "ServiceNow",
        "Zephyr Scale",
        "Jira",
        "Node.js",
        "REST APIs",
        "SQL",
        "Git",
    ],
    "environments": ["Development", "Pre-Production", "Production"],
    "sprint": "Q4-NOV-1-2026",
}

TEAM = {
    "engineers": ["Rishabh Gupta", "Saikath Bose", "Tejo Vempaty"],
    "test_engineers": ["Shilpi Gupta"],
    "leadership": ["Michael Baker", "Adrian Crowther"],
    "note": (
        "Name people accurately and only for the work they actually did with "
        "you. In an interview, 'I worked alongside' is safer and more credible "
        "than claiming to have led people you did not manage."
    ),
}

SPRINT = {
    "name": "Q4-NOV-1-2026",
    "items": [
        {
            "key": "IAMPAM-9031",
            "status": "In Test",
            "title": "Test — apply email template to disconnected certification escalation analytics",
            "detail": (
                "Validating that escalation analytics trigger the designated email "
                "template for disconnected certifications, including trigger "
                "criteria, recipient set and content accuracy during an escalation run."
            ),
            "url": f"{JIRA_BROWSE}IAMPAM-9031",
        },
        {
            "key": "IAMPAM-8983",
            "status": "Ready and Refined",
            "title": "TEST — ServiceNow delegation functionality",
            "detail": (
                "Preparing execution for delegated authority and approval routing in "
                "ServiceNow: who may act for whom, what the delegate can approve, "
                "and whether the audit trail names the delegate rather than the owner."
            ),
            "url": f"{JIRA_BROWSE}IAMPAM-8983",
        },
    ],
}

CIAM_STAGES = [
    {
        "id": "stage-1a",
        "label": "Stage 1A",
        "title": "Entra group reconciliation and correlation",
        "ticket": "IAMPAM-8347",
        "environment": "CIAM Development",
        "detail": (
            "Reconcile and correlate Microsoft Entra (Azure AD) groups into the CIAM "
            "development environment. Groups are the join key, so a missed group "
            "becomes a missed population of users in every downstream stage."
        ),
        "what_i_test": [
            "Source group count vs groups read, correlated, unmatched and failed.",
            "Group-to-identity correlation on the agreed unique attribute, including duplicates.",
            "Nested group and empty group behaviour, not just the flat happy path.",
            "Re-running the job changes nothing (idempotency) and leaves no duplicate links.",
        ],
        "risk": (
            "If correlation is wrong here, every later stage reports the wrong "
            "population as complete — reconciliation looks green while users are missing."
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "stage-1b",
        "label": "Stage 1B",
        "title": "Application accounts and roles via REST API",
        "ticket": "IAMPAM-8348",
        "environment": "CIAM Development",
        "detail": (
            "Validate the application accounts and assigned roles fetched and "
            "synchronised through the REST API integration."
        ),
        "what_i_test": [
            "Account count and role count reconcile between API source and Saviynt.",
            "Field mapping: account identifier, role name, status and ownership.",
            "Pagination, rate limiting and partial-failure responses from the API.",
            "A role removed at source is removed downstream — not just absent from the page.",
        ],
        "risk": (
            "A role that survives removal is standing access. This is the defect class "
            "an access review exists to catch, so it is the assertion that matters most."
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "stage-1c",
        "label": "Stage 1C",
        "title": "Pre-Production reconciliation",
        "ticket": "IAMPAM-8349",
        "environment": "Pre-Production",
        "detail": (
            "Repeat the reconciliation and correlation in Pre-Production, where the "
            "data shape and connector behaviour differ from Development."
        ),
        "what_i_test": [
            "The same count math as Dev, executed against Pre-Prod data.",
            "Configuration drift between environments: endpoints, credentials, schedules.",
            "Records that reconcile in Dev but fail in Pre-Prod — the interesting delta.",
        ],
        "risk": (
            "A defect that only appears in Pre-Prod is the one most likely to reach "
            "Production, because it survives the environment change."
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "stage-1d",
        "label": "Stage 1E",
        "title": "Production reconciliation",
        "ticket": "IAMPAM-8350",
        "environment": "Production",
        "detail": (
            "Verify the reconciliation and correlation behaviour in Production with "
            "production-shaped data, read-only where the control requires it."
        ),
        "what_i_test": [
            "Production counts against the expected population before sign-off.",
            "Failure records and rejects are visible and explainable, not silently dropped.",
            "No test identity, test group or probe account leaks into production reporting.",
        ],
        "risk": (
            "Production is where a reconciliation gap becomes a real user with real "
            "access. Evidence has to be clean enough to hand to an auditor."
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "stage-2",
        "label": "Stage 2",
        "title": "Deprovisioning and termination",
        "ticket": "IAMPAM-8351",
        "environment": "Dev, test and Production CIAM",
        "detail": (
            "Verify termination for users holding active accounts across the "
            "Development, test and Production CIAM environments."
        ),
        "what_i_test": [
            "Every active account for the leaver is disabled, in every environment.",
            "Sessions and tokens are invalidated, not just the account row.",
            "Re-running termination is safe and does not resurrect or duplicate access.",
            "A real login attempt fails at the API, and the audit trail shows why.",
        ],
        "risk": (
            "One surviving environment is a live account for a person who has left. "
            "This is the highest-severity defect in the JML surface."
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "stage-5a",
        "label": "Stage 5A",
        "title": "Access Request System forms",
        "ticket": "IAMPAM-8352",
        "environment": "Mosaic CIAM Development",
        "detail": (
            "Test the self-service and automated request workflows in the Mosaic CIAM "
            "Development ARS forms, including the approval path each request takes."
        ),
        "what_i_test": [
            "Form validation: required fields, invalid combinations, duplicate submissions.",
            "Routing to the correct approver tier, including custom end-user approval roles.",
            "Approve, reject, delegate and expire paths, each with an audit entry.",
            "The grant exists in the target only after approval — verified by API or SQL.",
        ],
        "risk": (
            "A request form that grants before approval, or to the wrong tier, is an "
            "approval bypass with a friendly user interface."
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
]


DOMAINS = [
    {
        "id": "ciam",
        "title": "CIAM reconciliation and correlation",
        "icon": "network",
        "summary": (
            "The multi-stage Transmit Security CIAM integration into Saviynt, tested "
            "from Entra groups through application roles to Production sign-off."
        ),
        "tickets": [
            _ticket("IAMPAM-8347", "Stage 1A — Entra group reconciliation (CIAM Dev)",
                    "Group population and correlation in Development."),
            _ticket("IAMPAM-8348", "Stage 1B — accounts and roles via REST API",
                    "Application accounts and assigned roles fetched through the API."),
            _ticket("IAMPAM-8349", "Stage 1C — Pre-Production reconciliation",
                    "The same reconciliation against Pre-Prod data and connectors."),
            _ticket("IAMPAM-8350", "Stage 1E — Production reconciliation",
                    "Production counts, rejects and sign-off evidence."),
        ],
        "what_i_test": [
            "Count math: source, read, processed, failed and target records reconcile.",
            "Record-level correlation: unmatched and duplicate identities have named reasons.",
            "Role removal propagates; role addition does not duplicate.",
            "Idempotency: a second run produces the same state.",
        ],
        "risk": (
            "Reconciliation is the control that proves the IGA platform sees the real "
            "population. A silent gap invalidates every certification built on top of it."
        ),
        "approach": (
            "Start with counts, then chase the exact records behind any gap through the "
            "failure table, the correlation rejects and the API pagination behaviour. "
            "Assert at the data layer, not the console."
        ),
        "script": (
            "\"The CIAM work was phased, and I tested each phase as its own gate. Stage 1A "
            "was Entra groups into the Dev tenant — population and correlation. Stage 1B "
            "was accounts and assigned roles coming through the REST API. Stage 1C repeated "
            "that in Pre-Prod, and Stage 1E in Production. My assertion was never 'the job "
            "ran'. It was: source count equals target count, every unmatched record has a "
            "reason, and a role removed at source is actually gone downstream. Then I ran "
            "it twice to prove the second run changed nothing.\""
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "jml",
        "title": "Joiner, mover and leaver lifecycle",
        "icon": "users",
        "summary": (
            "Onboarding, external joiner processing, termination and the manual-action "
            "dashboards that catch what automation leaves behind."
        ),
        "tickets": [
            _ticket("IAMPAM-7937", "External account joiner processing",
                    "Onboarding path for external identities."),
            _ticket("IAMPAM-8351", "Stage 2 — termination across CIAM environments",
                    "Deprovisioning where a user holds accounts in Dev, test and Prod."),
            _ticket("IAMPAM-8152", "Manual Actions Leavers Dashboard",
                    "The manual queue for leavers that need a human action."),
            _ticket("IAMPAM-8146", "Post-recertification removals on manual action dashboards",
                    "Removals that follow a certification decision."),
            _ticket("IAMPAM-7758", "Leaver ownership transfer and manager notification",
                    "What happens to owned objects and who is told."),
            _ticket("IAMPAM-7477", "Out-of-band access revocations",
                    "Manual revocations outside the normal connector path."),
            _ticket("IAMPAM-7771", "Automated user-group handling for leavers",
                    "Group membership cleanup in the leaver flow."),
            _ticket("IAMPAM-7652", "Automated leaver group handling",
                    "The automation behind the group cleanup."),
            _ticket("IAMPAM-7847", "Auto-provision users and Anaplan licences",
                    "Provisioning into Anaplan through Saviynt."),
            _ticket("IAMPAM-7495", "Anaplan platform explorer licence provisioning",
                    "Licence assignment as part of the joiner path."),
            _ticket("IAMPAM-7516", "Email notification error handling",
                    "Failure behaviour when a notification cannot be sent."),
            _ticket("IAMPAM-7311", "New joiner email updates",
                    "Content and recipient correctness for the joiner notification."),
            _ticket("IAMPAM-8700", "Non-EUI secondary email notifications",
                    "Users outside the EUI path still get the right message."),
            _ticket("IAMPAM-8517", "External supplier logic enhancements",
                    "Supplier-specific lifecycle rules."),
            _ticket("IAMPAM-7429", "Custom end-user approval role",
                    "ROLE_CUSTOM_END_USER and the approval routing it enables."),
        ],
        "what_i_test": [
            "Joiner: identity correlated, birthright roles provisioned, target account exists.",
            "Mover: the new access is added and the old access is gone — test the removal.",
            "Leaver: accounts disabled, sessions revoked, groups cleaned, owned objects transferred.",
            "Manual dashboards: the queue is complete, actionable and shows the right owner.",
            "Every step leaves an audit entry that names the actor and the reason.",
        ],
        "risk": (
            "Mover is where privilege creep lives, and leaver is where standing access "
            "becomes an incident. Both fail quietly unless the removal is asserted."
        ),
        "approach": (
            "Test the evidence chain: HR/source event → IGA state → connector task → "
            "target account → live login attempt → audit row. A green task is not proof."
        ),
        "script": (
            "\"The leaver path is the one I test hardest, because a failure there is a live "
            "account for someone who has left. In the CIAM termination work, a user could "
            "hold active accounts in Development, test and Production at the same time, so "
            "the test asserts every one of them is disabled — not just the environment I "
            "happened to open. I also check that sessions are invalidated and that a login "
            "attempt fails at the API. On the joiner side, external accounts and the "
            "non-EUI email path were the edge cases, because the standard notification "
            "assumptions did not hold for them.\""
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "certifications",
        "title": "Access certifications and governance",
        "icon": "shield",
        "summary": (
            "Campaign execution, escalation analytics, email templates and the SQLMD1 "
            "regression bucket that proves a certification release did not break."
        ),
        "tickets": [
            _ticket("IAMPAM-8455", "SQLMD1 certification regression bucket",
                    "The dedicated regression set for access certification campaigns."),
            _ticket("IAMPAM-9031", "Disconnected certification escalation analytics email template",
                    "In Test: trigger criteria, recipients and content."),
            _ticket("IAMPAM-7494", "Saviynt Neo UI certification campaigns",
                    "Campaign behaviour after the UI modernisation."),
            _ticket("IAMPAM-8194", "Test script design and case authoring",
                    "Zephyr Scale cases traced to the Jira story."),
            _ticket("IAMPAM-8195", "Manual and automated execution",
                    "Running the cycle and recording evidence."),
            _ticket("IAMPAM-8609", "Execution evidence for the release",
                    "The cycle results handed to the release."),
        ],
        "what_i_test": [
            "Campaign population matches the in-scope query — counts first, then identities.",
            "Reviewer assignment follows the hierarchy, including delegated reviewers.",
            "Decisions: certify, revoke, delegate and bulk, each with an audit entry.",
            "Escalation analytics trigger the right email template, to the right people, once.",
            "A revoke decision actually removes the entitlement downstream.",
        ],
        "risk": (
            "A campaign that closes without enforcing its revokes is compliance theatre. "
            "The auditor finds it later, with your name on the evidence."
        ),
        "approach": (
            "Run the bucket, then reconcile decisions to current entitlements with SQL. "
            "Separate 'campaign completed' from 'access removed' — they are different claims."
        ),
        "script": (
            "\"Certification work splits into two questions: did the campaign run, and did "
            "the decisions change anything? I run the SQLMD1 regression bucket for the "
            "campaign surface, then use SQL to join decisions to current entitlements. A "
            "revoke that leaves the role assigned is a finding, even if the campaign shows "
            "complete. The escalation work was the same discipline applied to email: does "
            "the analytics trigger fire, does it pick the disconnected certifications, and "
            "does the template reach the right recipient with the right content.\""
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "servicenow",
        "title": "ServiceNow delegation and approvals",
        "icon": "workflow",
        "summary": (
            "Delegated authority and approval chains where the person who approves is "
            "not the person who owns the request."
        ),
        "tickets": [
            _ticket("IAMPAM-8983", "ServiceNow delegation functionality",
                    "Ready and Refined: delegated authority and approval routing."),
            _ticket("IAMPAM-7769", "Delegation approval-chain cases",
                    "The Zephyr cases covering the approval path."),
        ],
        "what_i_test": [
            "A delegate can act only within the scope and dates granted.",
            "The approval records both the delegate and the original approver.",
            "Revoking delegation removes the ability immediately, including in-flight items.",
            "Self-delegation, circular delegation and expired delegation are rejected.",
        ],
        "risk": (
            "Delegation that is too broad is an approval bypass. Delegation with a weak "
            "audit trail is an unattributable decision."
        ),
        "approach": (
            "Model it as a permission matrix: delegator × delegate × scope × time. Test the "
            "allowed cell, then the four neighbouring denials."
        ),
        "script": (
            "\"Delegation is an authorization feature wearing a workflow costume. So I test "
            "it as a permission matrix — who can act for whom, on what, until when. The "
            "positive case is easy. The value is in the denials: the delegate acting outside "
            "the scope, after the end date, on their own request, or after the delegation is "
            "revoked. And I check the audit entry names the delegate, because otherwise the "
            "decision is unattributable.\""
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "automation",
        "title": "Automation framework and release hygiene",
        "icon": "code",
        "summary": (
            "Static-user harnesses for CIAM, regression stability across DEV and PRE-PROD, "
            "credential handling and branch discipline at release cut-off."
        ),
        "tickets": [
            _ticket("IAMPAM-8692", "Static user test harness — CIAM Development",
                    "Deterministic test identities for the Dev platform."),
            _ticket("IAMPAM-8693", "Static user harness extension",
                    "Additional coverage on the same harness."),
            _ticket("IAMPAM-8694", "Static user harness completion",
                    "The harness used by the CIAM automation suite."),
            _ticket("IAMPAM-8753", "Regression failures in DEV and PRE-PROD",
                    "Diagnosing and fixing suite failures across environments."),
            _ticket("IAMPAM-7674", "Credentials vault storage and TLS validation",
                    "Removing embedded credentials and enforcing certificate checks."),
            _ticket("IAMPAM-8612", "IGA_RELEASE_2026 branch preparation and merge",
                    "Release branch hygiene for the major cut-off."),
            _ticket("IAMPAM-6924", "PRE-PROD automation branch into MASTER",
                    "The merge path that keeps release automation current."),
        ],
        "what_i_test": [
            "The harness creates its own identities and leaves no residue for the next run.",
            "A failure is classified as product, environment or automation before it is filed.",
            "No credential is embedded in code; TLS validation is on, not bypassed.",
            "The release branch contains the same reviewed automation as the tested branch.",
        ],
        "risk": (
            "A suite that passes because it silently skipped, or stores a password in a "
            "properties file, is worse than no suite — it creates false confidence."
        ),
        "approach": (
            "Treat flakiness as a defect with a cause. Reproduce in the failing environment, "
            "compare the environment delta, then fix the harness or file the product bug."
        ),
        "script": (
            "\"The static-user harness exists because CIAM test data was not deterministic. "
            "If each run creates a known identity, a failure means the product changed, not "
            "that the data drifted. When the suite failed in DEV but passed in PRE-PROD, I "
            "treated the environment delta as the suspect first — endpoint, credential, "
            "schedule — and only filed a product defect once the harness was eliminated. The "
            "other piece I care about is credentials: they belong in the vault, and TLS "
            "validation stays on. A green suite that trusts every certificate is not a "
            "security test.\""
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "onboarding",
        "title": "Application onboarding",
        "icon": "plug",
        "summary": (
            "Connected applications where identity lifecycle, API synchronisation and role "
            "assignment have to work in the platform's own model."
        ),
        "tickets": [
            _ticket("IAMPAM-7664", "Workiva identity lifecycle",
                    "Onboarding and lifecycle behaviour for Workiva."),
            _ticket("IAMPAM-8288", "Workiva API synchronisation and roles",
                    "Account and role sync through the integration."),
            _ticket("IAMPAM-7505", "Adobe Experience Platform user management API",
                    "AEP/CXP user lifecycle through the API."),
            _ticket("IAMPAM-7355", "Anaplan onboarding",
                    "Anaplan identity and licence provisioning."),
        ],
        "what_i_test": [
            "Create, update and disable map to the application's real model, not just ours.",
            "Role or licence assignment uses the correct identifier and is idempotent.",
            "The API's error responses are surfaced, not swallowed as success.",
            "A removal at source reaches the application on the next sync.",
        ],
        "risk": (
            "Every application has its own idea of a role. A mapping that looks right in "
            "Saviynt can grant the wrong thing in the target."
        ),
        "approach": (
            "Read the vendor's user-management model first, then assert in the target "
            "application — API response and data, not the provisioning log alone."
        ),
        "script": (
            "\"Onboarding a new application is mostly translation. Workiva, AEP and Anaplan "
            "each model users and roles differently, so the test has to assert in the "
            "target's language. I check create, update and disable, then the removal path, "
            "because a role that is added and never removed is the defect that survives. I "
            "also force the API error path: if the target rejects the call, the sync must "
            "report a failure, not a cheerful success.\""
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "defects",
        "title": "Defect investigation",
        "icon": "bug",
        "summary": (
            "Complex identity edge cases, including concurrency between attribute updates "
            "and absence records."
        ),
        "tickets": [
            _ticket("IAMPAM-7109", "Race condition: attribute updates and absence records",
                    "Concurrent writes produce an inconsistent identity state."),
            _ticket("IAMPAM-8341", "Defect management and test closure",
                    "The closure standard: root cause, evidence, regression."),
            _ticket("IAMPAM-8340", "Test data and environment preparation",
                    "The setup that makes a concurrency defect reproducible."),
        ],
        "what_i_test": [
            "Reproduce deterministically: same inputs, same ordering, same timing window.",
            "Compare the two writes and the final state; identify which one lost.",
            "Prove the fix with the race still in the test, not by removing the trigger.",
        ],
        "risk": (
            "A concurrency bug that is 'fixed' by retrying hides a data-integrity problem "
            "that will reappear under real load."
        ),
        "approach": (
            "Timeline first: order the events with timestamps from both systems, then "
            "narrow to the hop where the last write wins."
        ),
        "script": (
            "\"The race condition was between an attribute update and an absence record. "
            "Depending on which write landed last, the identity ended up in a state that was "
            "individually valid but jointly wrong. I reproduced it by controlling the order "
            "rather than hoping for it, then built a timeline from both systems' timestamps "
            "to show which write was lost. The regression test keeps both writes in the same "
            "window, so a retry-based fix would not pass it.\""
        ),
        "source_ids": ["role-brief", "jira-board"],
    },
]


LIFECYCLE = {
    "title": "The four-stage stage-gate you actually run",
    "note": (
        "This is the operating procedure from the role brief. In an interview, naming the "
        "stages and the artefact each one produces sounds far more senior than listing tools."
    ),
    "stages": [
        {
            "id": "prepare",
            "label": "1. Test data and environment preparation",
            "ticket": "IAMPAM-8340",
            "what": (
                "Agree the environment, build deterministic identities, and prove the "
                "connector and schedule are healthy before testing the feature."
            ),
            "artefact": "Data set, environment checklist, known-good baseline.",
            "question": "Can I reproduce this run tomorrow, on a clean environment?",
            "source_ids": ["role-brief", "jira-board"],
        },
        {
            "id": "design",
            "label": "2. Test script design and case authoring",
            "ticket": "IAMPAM-8194",
            "what": (
                "Turn the Jira story and acceptance criteria into Zephyr Scale cases with "
                "explicit expected results, including negative and authorization paths."
            ),
            "artefact": "Zephyr cases traced to the Jira story.",
            "question": "Which requirement would fail silently if this case did not exist?",
            "source_ids": ["role-brief", "jira-board"],
        },
        {
            "id": "execute",
            "label": "3. Execution — manual and automated",
            "ticket": "IAMPAM-8195",
            "what": (
                "Run the cycle, capture evidence per case, and keep the automated suite and "
                "the manual checks pointing at the same expected behaviour."
            ),
            "artefact": "Execution results with evidence attached to each case.",
            "question": "Is this failure product, environment or automation?",
            "source_ids": ["role-brief", "jira-board"],
        },
        {
            "id": "close",
            "label": "4. Defect management and test closure",
            "ticket": "IAMPAM-8341",
            "what": (
                "Root-cause every defect, link it to the case that caught it, add the "
                "regression that would catch it again, and write the closure report."
            ),
            "artefact": "Defect record, regression case, test closure report.",
            "question": "What would stop this class of defect, not just this instance?",
            "source_ids": ["role-brief", "jira-board"],
        },
    ],
}


QUESTIONS = [
    {
        "id": "admiral-role",
        "prompt": "Tell me about your current role at Admiral Group.",
        "evidence": "internal",
        "why": (
            "This is the anchor answer. If it is vague, every later answer sounds "
            "rehearsed; if it is concrete, the interviewer starts testing depth."
        ),
        "answer": (
            "\"I'm an SDET in the Identity Governance and Administration team at Admiral "
            "Group, inside the wider IAM function. The platforms I test are Saviynt for "
            "IGA, Transmit Security for customer identity, Entra ID and Active Directory, "
            "with ServiceNow in the approval path. My work is a mix of automated harnesses "
            "and structured manual testing: CIAM reconciliation and correlation, joiner-"
            "mover-leaver, access certifications and the integrations that connect them. "
            "The thing I own most clearly is the evidence — Zephyr cases traced to Jira, "
            "execution results, and a closure report that someone else can pick up. The "
            "current sprint is certification escalation analytics and ServiceNow delegation.\""
        ),
        "key_points": [
            "Name the team and the platforms in one breath.",
            "Separate automation from structured manual testing — both are real work.",
            "Name the current sprint, because it proves you are active, not reciting a CV.",
            "End on the evidence trail: Zephyr, Jira, closure report.",
        ],
        "follow_ups": [
            "Which part of that is yours versus the team's?",
            "What does a normal sprint look like for you?",
            "What is the hardest defect you have investigated there?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-ciam-stages",
        "prompt": "Walk me through the CIAM reconciliation stages you tested.",
        "evidence": "jira",
        "why": (
            "The phased CIAM integration is the strongest evidence that you can own a "
            "multi-environment security integration end to end."
        ),
        "answer": (
            "\"It ran as a sequence of gates. Stage 1A reconciled and correlated Entra "
            "groups into the CIAM Development tenant — population and correlation, because "
            "groups determine who is in scope. Stage 1B validated application accounts and "
            "assigned roles coming through the REST API. Stage 1C repeated the reconciliation "
            "in Pre-Production, and Stage 1E in Production. Each stage had the same shape: "
            "counts reconcile, every unmatched record has a reason, role removals propagate, "
            "and a second run changes nothing. The later stages were not a formality — "
            "Pre-Prod is where configuration drift showed up, and Production is where the "
            "evidence had to be clean enough for audit.\""
        ),
        "key_points": [
            "Phases are gates, not a single test run.",
            "Groups first — they define the population.",
            "REST API for accounts and roles; assert the removal, not just the add.",
            "Pre-Prod and Prod repeat the same assertions against different data.",
        ],
        "follow_ups": [
            "What did you do when counts did not reconcile?",
            "How did you handle duplicates and unmatched records?",
            "What was different about Production testing?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-reconciliation-method",
        "prompt": "How do you test reconciliation and correlation?",
        "evidence": "internal",
        "why": (
            "This separates a tester who reads a dashboard from one who can find the "
            "record that is missing behind a green status."
        ),
        "answer": (
            "\"Count math first: source records, records read, processed, failed, and "
            "present in the target all have to reconcile. Any gap is a defect with a name, "
            "not a percentage to wave away. Then record level: I take the difference and "
            "chase it through the failure table, the correlation-rule rejects, and the "
            "pagination behaviour of the source API. For correlation specifically, I test "
            "the join key — duplicates, missing attributes, and identities that should not "
            "correlate but do. And idempotency: run it twice and the second run must be a "
            "no-op. In CIAM that mattered because the same person can exist in more than one "
            "tenant, and a bad correlation creates a duplicate identity that later looks "
            "like a legitimate user.\""
        ),
        "key_points": [
            "Counts first, records second.",
            "Every mismatch needs a named reason, not a retry.",
            "Correlation is a join-key problem: duplicates and non-matches.",
            "Idempotency is part of correctness.",
        ],
        "follow_ups": [
            "How would you automate the count reconciliation?",
            "What is the most common correlation failure you have seen?",
            "How do you test pagination edge cases?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-termination",
        "prompt": "How do you test termination for a user with accounts in several environments?",
        "evidence": "jira",
        "why": (
            "Stage 2 is the highest-severity JML surface, and the multi-environment "
            "angle is specific to your real work."
        ),
        "answer": (
            "\"I treat each environment as its own assertion. The user may hold an active "
            "account in Development, test and Production CIAM at the same time, so a test "
            "that checks one console proves almost nothing. I enumerate every account for "
            "that identity, trigger termination, then assert each account is disabled and "
            "each session or token is invalidated — not just the account row. Then I attempt "
            "a real login at the API and expect failure. Finally the audit trail: the "
            "termination event, the connector task and the resulting state all have to line "
            "up. If one environment fails, that is a live account for a leaver, so it is a "
            "severity-one finding rather than a test failure.\""
        ),
        "key_points": [
            "One assertion per environment — enumerate the accounts first.",
            "Sessions and tokens are separate from the account state.",
            "A real login attempt is the proof.",
            "Audit trail alignment is part of the requirement.",
        ],
        "follow_ups": [
            "What if the connector is down during termination?",
            "How do you test a rehire after termination?",
            "How do you stop test identities polluting production reporting?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-joiner",
        "prompt": "How did you test external joiner onboarding?",
        "evidence": "jira",
        "why": (
            "External joiners are the edge case where the standard notification and "
            "identity assumptions break."
        ),
        "answer": (
            "\"External joiners do not look like employees, so the first question is which "
            "assumptions still hold. The identity arrives through a different path, may not "
            "have the standard directory attributes, and may not receive the normal EUI "
            "notification. I tested the creation and correlation, the birthright roles, the "
            "target accounts, and then the communication path — including the secondary "
            "email handling for non-EUI users. The negative cases matter as much: a joiner "
            "without a manager, a duplicate external identity, and an end date that expires "
            "silently. Each of those is a real onboarding defect that the happy path never "
            "sees.\""
        ),
        "key_points": [
            "External identities break employee-shaped assumptions.",
            "Test the notification path separately from the account creation.",
            "Missing manager, duplicate identity and silent expiry are the real defects.",
            "Birthright roles still have to be least-privilege.",
        ],
        "follow_ups": [
            "How do you test the joiner email content?",
            "What happens if the external identity already exists?",
            "How do you handle a contractor end date?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-leaver-dashboards",
        "prompt": "What do you test on the leaver manual-action dashboards?",
        "evidence": "jira",
        "why": (
            "Manual-action queues are where automation hands off to a human, and where "
            "ownership and notification defects hide."
        ),
        "answer": (
            "\"The dashboard is a work queue, so I test it as one: is every leaver that needs "
            "a manual action actually in it, is the owner correct, and can the action be "
            "completed without ambiguity? Then the downstream effect — a post-recertification "
            "removal should remove the entitlement, and an ownership transfer should move the "
            "objects and notify the right manager. The defects I look for are the quiet ones: "
            "an item that disappears from the queue without being actioned, a queue that "
            "shows complete while an account is still active, or a notification that goes to "
            "the leaver instead of the manager. I verify the queue against SQL, not just the "
            "rendered page.\""
        ),
        "key_points": [
            "A dashboard is a queue: completeness, ownership, actionability.",
            "Verify the downstream removal, not just the task closure.",
            "Watch for items that vanish without action.",
            "Notification recipients are part of the test.",
        ],
        "follow_ups": [
            "How would you detect a leaver missing from the queue?",
            "Who owns an item when the manager has also left?",
            "How do you test the ownership transfer itself?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-certifications",
        "prompt": "How do you test access certification campaigns?",
        "evidence": "jira",
        "why": (
            "Certification is the governance control auditors care about, and your SQLMD1 "
            "and escalation work gives you concrete material."
        ),
        "answer": (
            "\"In three layers. Mechanics: the campaign population matches the in-scope "
            "query, reviewer assignment follows the hierarchy, and certify, revoke, delegate "
            "and bulk all work with an audit entry. Enforcement: a revoke decision has to "
            "remove the entitlement downstream — I verify that with SQL joining decisions to "
            "current assignments, because a closed campaign is not the same claim as removed "
            "access. Analytics and communication: escalation analytics must select the right "
            "population and trigger the right email template, to the right recipient, once. "
            "I run the SQLMD1 regression bucket around the campaign surface so a release does "
            "not break a control we have already proved.\""
        ),
        "key_points": [
            "Mechanics, enforcement, reporting — three separate claims.",
            "Revoke must mean removed downstream, proved with SQL.",
            "Escalation: population, template, recipient, frequency.",
            "SQLMD1 is the regression bucket around the campaign surface.",
        ],
        "follow_ups": [
            "How do you stop a campaign becoming a rubber stamp?",
            "How do you test a delegated reviewer?",
            "What does your SQL check for a revoke look like?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-sqlmd1",
        "prompt": "What is a certification regression bucket, and how do you run one?",
        "evidence": "jira",
        "why": (
            "It shows you understand regression as a risk-scoped set, not 'run everything'."
        ),
        "answer": (
            "\"A bucket is the minimum set of cases that proves the certification surface "
            "still works after a change — campaign creation, population, reviewer assignment, "
            "decisions, delegation, escalation and enforcement. SQLMD1 is that set for access "
            "certifications. I run it as a gate: every case has an expected result and "
            "evidence, failures are triaged as product, environment or automation, and the "
            "cycle result is attached to the release. The point is not coverage percentage; "
            "it is that a release cannot quietly break a governance control. If a case is "
            "missing from the bucket, I add it when a defect escapes — the bucket learns from "
            "the defects it did not catch.\""
        ),
        "key_points": [
            "A bucket is risk-scoped regression, not everything.",
            "Every case has expected result and evidence.",
            "Triage classification before filing.",
            "The bucket grows when a defect escapes.",
        ],
        "follow_ups": [
            "How do you decide what enters the bucket?",
            "How long does the bucket take, and what do you cut first?",
            "How do you keep it from becoming stale?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-servicenow",
        "prompt": "How do you test ServiceNow delegation?",
        "evidence": "jira",
        "why": (
            "Delegation is an authorization feature disguised as a workflow, which makes "
            "it a strong answer for a security QA role."
        ),
        "answer": (
            "\"I model it as a permission matrix: delegator, delegate, scope and time window. "
            "The allowed cell is the easy part — the delegate can approve within scope before "
            "the end date. The value is in the neighbouring denials: outside the scope, after "
            "expiry, on the delegator's own request, on their own request, and after the "
            "delegation is revoked, including items already in flight. Then attribution: the "
            "approval record must name both the delegate and the original approver, or the "
            "decision is unattributable in an audit. I also test circular delegation, because "
            "A delegates to B and B delegates to A can create an approval loop if the platform "
            "does not reject it.\""
        ),
        "key_points": [
            "Delegation is authorization: matrix, not happy path.",
            "Test expiry, scope, self-delegation, circular delegation, revocation.",
            "In-flight items after revocation are the sneaky case.",
            "Attribution in the audit trail is a requirement.",
        ],
        "follow_ups": [
            "What should happen to approvals already delegated when the delegation is revoked?",
            "How do you test delegation across a manager hierarchy?",
            "Where would you expect the enforcement to live?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-ars",
        "prompt": "How do you test access request forms end to end?",
        "evidence": "jira",
        "why": (
            "The ARS is the front door to access, so a routing or approval defect is an "
            "access-control defect."
        ),
        "answer": (
            "\"I test it as a state machine. Submit: required fields, invalid combinations, "
            "duplicate submissions. Route: the request reaches the correct approver tier, "
            "including custom end-user approval roles, and not a default approver. Decide: "
            "approve, reject, delegate and expire each produce the right state and audit "
            "entry. Provision: the entitlement exists in the target only after approval, "
            "verified by API or SQL. The negative cases get equal weight — self-approval, "
            "approving through the API as the requester, tampering with a request ID, and "
            "replaying an approval. A request form that grants early is an approval bypass "
            "with a friendly interface.\""
        ),
        "key_points": [
            "State machine: submit → route → decide → provision.",
            "Check the routing tier, including custom approval roles.",
            "Provisioning only after approval, verified downstream.",
            "Negative paths are the security tests.",
        ],
        "follow_ups": [
            "How do you test a custom end-user approver role?",
            "What happens on duplicate requests?",
            "How do you test an emergency approval?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-race",
        "prompt": "Tell me about the race condition between attribute updates and absence records.",
        "evidence": "jira",
        "why": (
            "This is a genuine complex-defect story: concurrency, data integrity and a "
            "regression that keeps the trigger in place."
        ),
        "answer": (
            "\"The symptom was an identity in a state that was individually valid but "
            "jointly wrong: an attribute update and an absence record landing close together, "
            "with the final state depending on which write won. The first job was to make it "
            "reproducible — control the ordering instead of hoping for it, and capture both "
            "systems' timestamps. That gave a timeline showing which write was lost. The fix "
            "was in the ordering and conflict handling, not a retry. For the regression I kept "
            "both writes inside the same window, so a retry-based 'fix' would fail the test. "
            "The wider lesson is that identity state has invariants across records, and "
            "single-record assertions will never catch a violation of them.\""
        ),
        "key_points": [
            "Reproduce by controlling order, not by re-running until it fails.",
            "Build a timeline from both systems before blaming a component.",
            "Retry is not a fix for a data-integrity race.",
            "Keep the race in the regression test.",
        ],
        "follow_ups": [
            "How did you prove which write was lost?",
            "What invariant would you assert across the two records?",
            "How would you prevent this class of defect elsewhere?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-credentials",
        "prompt": "How do you handle credentials and TLS in an automation framework?",
        "evidence": "jira",
        "why": (
            "Security QA candidates are expected to hold their own tooling to the standard "
            "they test."
        ),
        "answer": (
            "\"Credentials come from a vault or the CI secret store at run time — never from "
            "a properties file, never committed, never echoed in a log or a report. The test "
            "user has only the permissions the scenario needs, so a bug cannot escalate "
            "through the harness. TLS validation stays on; disabling certificate checks to "
            "make a test pass is a security defect in the test itself. When I migrated the "
            "framework credentials into vault storage and enforced TLS validation, the "
            "interesting part was the failure path: a missing secret should fail the run "
            "clearly, not fall back to a default account. That fallback is how a 'test' "
            "account quietly becomes a shared privileged one.\""
        ),
        "key_points": [
            "Vault or CI secret store at run time.",
            "Least-privilege test identities.",
            "TLS validation on — never bypassed for convenience.",
            "Missing secret fails closed, no default fallback.",
        ],
        "follow_ups": [
            "How do you rotate a secret without breaking the suite?",
            "What do you do when a test environment has a self-signed certificate?",
            "How do you keep secrets out of failure artefacts?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-release",
        "prompt": "How do you manage automation branch hygiene at a release cut-off?",
        "evidence": "jira",
        "why": (
            "Release discipline is a reliability signal: the branch you tested must be the "
            "branch you ship."
        ),
        "answer": (
            "\"The rule is simple: the release branch contains exactly the reviewed automation "
            "that was tested. Before a cut-off like IGA_RELEASE_2026 I check what is on the "
            "PRE-PROD automation branch, make sure fixes are merged and reviewed, merge into "
            "master in a controlled order, and confirm the pipeline runs the merged commit — "
            "not a local copy. The failure mode I guard against is a fix that exists on a "
            "branch but never reaches the release, so the suite passes in the wrong place. I "
            "treat the merge as a testable change: run the suite after it, compare the result "
            "to the pre-merge baseline, and keep the release evidence with the cut-off.\""
        ),
        "key_points": [
            "Tested branch equals shipped branch.",
            "Merge is itself a change that needs a suite run.",
            "Compare post-merge results to the baseline.",
            "Keep release evidence with the cut-off.",
        ],
        "follow_ups": [
            "How do you handle a hotfix after the cut-off?",
            "What do you do when master and the release branch diverge?",
            "How do you prove the pipeline ran the merged commit?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-regression-triage",
        "prompt": "A regression suite fails in DEV but passes in PRE-PROD. How do you triage it?",
        "evidence": "jira",
        "why": (
            "Cross-environment debugging is daily work in this role and a common interview "
            "scenario."
        ),
        "answer": (
            "\"First classify, then fix. The environment delta is the prime suspect: endpoint, "
            "credential, data, schedule or configuration. I reproduce the failure in DEV, "
            "capture the request and response, and compare against the PRE-PROD run. If the "
            "product behaviour is identical and only the harness environment differs, it is "
            "automation or environment. If the product genuinely behaves differently, that is "
            "a defect — and the more serious kind, because it means the environments are not "
            "equivalent. I only file after I can say which of the three it is. Then the fix "
            "gets a regression that runs in both environments, so the difference cannot "
            "return silently.\""
        ),
        "key_points": [
            "Classify: product, environment or automation.",
            "Diff the environment before diffing the code.",
            "A real DEV/PRE-PROD behavioural difference is a defect in itself.",
            "Add the regression in both environments.",
        ],
        "follow_ups": [
            "What if you cannot access the environment to reproduce it?",
            "How do you stop the same failure recurring in another suite?",
            "What evidence do you attach to the defect?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-traceability",
        "prompt": "How do you maintain requirement-to-test traceability?",
        "evidence": "internal",
        "why": (
            "Traceability is what turns testing into evidence an auditor or a release board "
            "can use."
        ),
        "answer": (
            "\"Every Zephyr case links to the Jira story it proves, and the case states the "
            "expected result in observable terms — not 'verify it works'. When the story "
            "changes, the case changes in the same change, because a stale case is worse than "
            "no case: it produces a green result for behaviour nobody asked for. At closure I "
            "can answer three questions from the artefacts: which requirements were tested, "
            "which cases proved them, and what evidence exists for each execution. That is "
            "also what makes a handover possible without a meeting — the next person can "
            "follow the links.\""
        ),
        "key_points": [
            "Case linked to story, expected result observable.",
            "Change the case in the same change as the story.",
            "Closure answers: requirements, cases, evidence.",
            "Handover without a meeting is the test of good traceability.",
        ],
        "follow_ups": [
            "What do you do when a requirement has no acceptance criteria?",
            "How do you handle a case that covers several stories?",
            "How do you spot coverage gaps?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-onboarding-app",
        "prompt": "How do you test onboarding a new application into the IGA platform?",
        "evidence": "jira",
        "why": (
            "Application onboarding is where platform-generic assumptions meet a vendor's "
            "real user model."
        ),
        "answer": (
            "\"I start with the target's user model, not ours. Workiva, AEP and Anaplan each "
            "represent users, roles and licences differently, so the test has to assert in "
            "their language. Then the lifecycle: create, update, disable, and — the one that "
            "gets skipped — removal. A role that is added and never removed is the defect that "
            "survives. I force the API error path too: if the target rejects a call, the sync "
            "must report a failure, not a success with a swallowed error. Finally idempotency: "
            "the same sync twice must not duplicate the account or the licence.\""
        ),
        "key_points": [
            "Read the target's model first.",
            "Test create, update, disable and removal.",
            "Force the API error path; no swallowed failures.",
            "Idempotency prevents duplicate accounts and licences.",
        ],
        "follow_ups": [
            "How do you test a licence count?",
            "What if the application has no API for removal?",
            "How do you keep vendor differences from leaking into the test code?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-lifecycle",
        "prompt": "Describe your testing lifecycle from story to closure.",
        "evidence": "internal",
        "why": (
            "This is the process answer that shows you can own quality, not just execute "
            "cases someone handed you."
        ),
        "answer": (
            "\"Four gates. Preparation: agree the environment, build deterministic data, and "
            "prove the connector and schedule are healthy. Design: turn the story and "
            "acceptance criteria into Zephyr cases with observable expected results, "
            "including the negative and authorization paths. Execution: run manual and "
            "automated, capture evidence per case, and classify every failure as product, "
            "environment or automation before filing. Closure: root cause the defects, add "
            "the regression that would catch the class again, and write the closure report so "
            "the release has evidence and the next person has a handover. The gate that gets "
            "skipped in a hurry is preparation, and it is the one that causes the most "
            "false failures later.\""
        ),
        "key_points": [
            "Four gates: prepare, design, execute, close.",
            "Observable expected results, including negative paths.",
            "Classify before filing.",
            "Closure produces evidence and a handover.",
        ],
        "follow_ups": [
            "Which gate do teams skip most often?",
            "What goes in your closure report?",
            "How do you handle a story with no test data available?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
    {
        "id": "admiral-automate-or-not",
        "prompt": "What do you automate in IGA, and what do you deliberately keep manual?",
        "evidence": "internal",
        "why": (
            "Risk-based automation judgement is the difference between an SDET and a "
            "script runner."
        ),
        "answer": (
            "\"I automate what is repeatable and high-risk: lifecycle assertions, "
            "reconciliation counts, role removal propagation, certification enforcement and "
            "the API-level negatives. I keep manual the work that needs judgement — "
            "exploratory testing of a new ARS form, a visual review of a dashboard, and the "
            "first pass on a complex defect where I do not yet know what 'correct' looks like. "
            "The test is whether a check will still be valuable in three months. A regression "
            "that proves a leaver loses access in every environment is worth automating every "
            "run. A screenshot comparison of a page about to be redesigned is maintenance "
            "debt.\""
        ),
        "key_points": [
            "Automate repeatable, high-risk, stable assertions.",
            "Keep judgement-heavy and exploratory work manual.",
            "Prefer API/data assertions over UI where possible.",
            "Maintenance cost is part of the decision.",
        ],
        "follow_ups": [
            "Give an example of something you automated too early.",
            "How do you keep the automated suite from becoming a second product?",
            "How do you decide when a manual check is ready to automate?",
        ],
        "source_ids": ["role-brief", "jira-board"],
    },
]


SCHWAB_MAP = [
    {
        "schwab_topic": "Joiner-mover-leaver",
        "admiral_evidence": (
            "External joiner processing (IAMPAM-7937), termination across Dev/test/Prod "
            "(IAMPAM-8351), leaver dashboards (IAMPAM-8152, IAMPAM-8146)."
        ),
        "use_it": "Use the multi-environment termination story when they ask about leavers.",
    },
    {
        "schwab_topic": "Access certification",
        "admiral_evidence": (
            "SQLMD1 regression bucket (IAMPAM-8455), escalation analytics and email "
            "templates (IAMPAM-9031), Neo UI campaigns (IAMPAM-7494)."
        ),
        "use_it": "Answer with the three layers: mechanics, enforcement, analytics.",
    },
    {
        "schwab_topic": "CIAM / identity integration",
        "admiral_evidence": (
            "Stages 1A-1E of the Transmit Security CIAM integration (IAMPAM-8347 to "
            "IAMPAM-8350), accounts and roles through REST (IAMPAM-8348)."
        ),
        "use_it": "This is your reconciliation depth; lead with counts then records.",
    },
    {
        "schwab_topic": "API and SQL testing",
        "admiral_evidence": (
            "Entra/Saviynt REST integrations, account and role synchronisation, "
            "certification-to-entitlement SQL checks."
        ),
        "use_it": "Describe asserting downstream in the target, not just the IGA console.",
    },
    {
        "schwab_topic": "Automation framework",
        "admiral_evidence": (
            "Static-user harnesses (IAMPAM-8692 to IAMPAM-8694), regression triage in DEV "
            "and PRE-PROD (IAMPAM-8753), vaulted credentials and TLS (IAMPAM-7674), "
            "release branch hygiene (IAMPAM-8612, IAMPAM-6924)."
        ),
        "use_it": "Frame the harness as determinism, and the vault work as holding your own tooling to the standard.",
    },
    {
        "schwab_topic": "Incident and complex defects",
        "admiral_evidence": (
            "Stage 2 termination (IAMPAM-8351), out-of-band revocations (IAMPAM-7477), "
            "the attribute/absence race condition (IAMPAM-7109)."
        ),
        "use_it": "Contain, evidence, chain, fix, then the regression that keeps the trigger.",
    },
]


DISCLAIMER = (
    "This page is built only from the Admiral Group IGA role brief you provided and "
    "the internal IAMPAM ticket keys it names. No Admiral source was queried or "
    "researched for it, and the app never fetches an Admiral URL. The Jira links "
    "require Admiral SSO and are not public sources. No measured number on this page "
    "is invented: where a metric would strengthen an answer, the answer says what you "
    "would measure instead."
)


def get_admiral() -> dict:
    return {
        "title": "Admiral IGA Playbook",
        "subtitle": (
            "Your current role as an SDET in Admiral Group's Identity Governance & "
            "Administration team: CIAM reconciliation, JML, certifications, ServiceNow "
            "delegation, automation and the defects worth telling stories about."
        ),
        "question_count": len(QUESTIONS),
        "ticket_count": len(
            {t["key"] for d in DOMAINS for t in d["tickets"]}
            | {s["ticket"] for s in CIAM_STAGES}
        ),
        "role": ROLE,
        "team": TEAM,
        "sprint": SPRINT,
        "ciam_stages": CIAM_STAGES,
        "domains": DOMAINS,
        "lifecycle": LIFECYCLE,
        "questions": QUESTIONS,
        "schwab_map": SCHWAB_MAP,
        "sources": SOURCES,
        "disclaimer": DISCLAIMER,
    }
