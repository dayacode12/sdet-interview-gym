"""Scenario simulator: 30 enterprise cybersecurity QA scenarios with scoring keys."""
from __future__ import annotations

SCENARIOS = [
    {
        "id": "scen-terminated-retains-access",
        "title": "Terminated employee retains access",
        "severity": "critical",
        "topic": "IGA / JML",
        "situation": (
            "HR marked an employee as TERMINATED yesterday. Today the helpdesk received a ticket "
            "from the manager: the former employee's account still logs into a claims application."
        ),
        "interviewer_question": (
            "An employee leaves the organisation and HR processes the termination, but the employee "
            "can still access an enterprise application. How would you test this, and what would "
            "you check?"
        ),
        "key_points": [
            "Validate the termination event in the HR source system first (event exists, timestamp, payload).",
            "Confirm the IGA platform received and processed the event (identity status = TERMINATED).",
            "Verify a deprovisioning task was generated for EVERY connected application.",
            "Check provisioning logs per target: DISABLE/REVOKE operations and their status.",
            "Verify the target application's database: account disabled, roles/entitlements removed.",
            "Attempt login with the terminated user's credentials — access must be denied.",
            "Check privileged accounts too: CyberArk vault entry, active sessions, API keys.",
            "Verify audit logs record the full chain for compliance evidence.",
            "Test delayed HR events (event arrives late), partial failures (1 of 5 apps), retry behaviour.",
            "Do not accept the IGA dashboard status as proof — the target system is the truth.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Termination revokes all access", "expected": "All target accounts disabled; login denied; audit trail complete."},
            {"type": "negative", "title": "Delayed HR event", "expected": "Access remains until event arrives; SLA breach alerted, not silent."},
            {"type": "negative", "title": "Deprovisioning fails on one application", "expected": "Retry fires; escalation/alert; identity marked incomplete, not 'done'."},
            {"type": "boundary", "title": "User has privileged + regular accounts", "expected": "Both revoked, including vault entries and API keys."},
        ],
        "api_checks": "GET /api/users/{id} status TERMINATED; deprovisioning task status per application; login attempt returns 401/403.",
        "db_checks": "USERS.status; USER_ROLES rows for the user gone; PROVISIONING_LOGS show DISABLE/REVOKE SUCCESS per app; CyberArk vault entry removed.",
        "job_checks": "Deprovisioning/reconciliation jobs triggered by the termination event; verify execution and retry counts.",
        "security_consideration": "Terminated users with live access are the highest-silent-risk JML defect; verify in every downstream system, not just the dashboard.",
        "root_cause_paths": [
            "HR event never delivered to IGA (integration down, queue backlog).",
            "Event received but deprovisioning workflow failed to trigger.",
            "Provisioning task failed on the connector (credentials, API 500) and retry gave up.",
            "Target application received the call but processed it partially (role removed, account still enabled).",
            "Reconciliation job has not run to correct drift.",
        ],
        "strong_answer": (
            "I would treat the HR system as the source of truth and walk the chain: event exists -> "
            "IGA processed it -> deprovisioning tasks generated -> per-application operations "
            "succeeded -> target database shows the account disabled and roles removed -> an "
            "actual login attempt is denied. I would test failure variants deliberately: the event "
            "arriving late, one application failing while others succeed, retries, and privileged "
            "credentials including CyberArk vault entries. And I would never certify the workflow on "
            "the IGA status field alone — the dashboard can say TERMINATED while the target "
            "application still accepts the login. The target system is the evidence."
        ),
        "followups": [
            "What if the deprovisioning job succeeded but the application still allows login?",
            "How do you test this at scale (100 terminations a day)?",
            "What reconciliation report would catch this automatically?",
        ],
    },
    {
        "id": "scen-unauthorized-admin-access",
        "title": "Unauthorized user receives admin access",
        "severity": "critical",
        "topic": "Authorization / RBAC",
        "situation": (
            "A routine entitlement review finds a standard employee with SYS_ADMIN on a production "
            "system. Nobody recalls approving it."
        ),
        "interviewer_question": (
            "A normal employee requests administrative access and somehow receives it without "
            "proper approval. How would you investigate and test?"
        ),
        "key_points": [
            "RBAC: which role grants admin; who holds it; what the approval policy says.",
            "Access request trail: does an APPROVED request exist for this grant?",
            "Test the approval workflow cannot be bypassed (self-approval, skipped stage).",
            "API authorization: employee token calling admin endpoints must get 403.",
            "IDOR/privilege escalation attempts: modify request IDs, call provisioning APIs directly.",
            "Database: who inserted the role assignment and when (assigned_date vs request date).",
            "Audit logs: the exact path that granted the entitlement.",
            "Role definitions: is SYS_ADMIN incorrectly inheriting from a lower role?",
            "Emergency/break-glass paths: was an emergency approval used and did it expire?",
            "Regression: once fixed, an automated test must keep proving the bypass is closed.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Admin request with full approval grants access", "expected": "Grant happens only after final approver signs off."},
            {"type": "negative", "title": "Request rejected at any stage", "expected": "No entitlement granted; audit entry records rejection."},
            {"type": "negative", "title": "Employee calls admin API directly", "expected": "403 Forbidden; attempt logged."},
            {"type": "negative", "title": "Requester approves own request", "expected": "Blocked in UI and API; security log entry."},
            {"type": "boundary", "title": "Emergency grant expires", "expected": "Time-boxed elevation auto-revokes at expiry."},
        ],
        "api_checks": "POST /api/requests with employee token; approve endpoint as requester (403); admin endpoints with employee token (403); request ID tampering.",
        "db_checks": "USER_ROLES assigned_date vs ACCESS_REQUESTS decision/created_at mismatch; grants without request rows.",
        "job_checks": "Any provisioning job that could grant roles outside the workflow (bulk imports, birthright rules) with overly broad filters.",
        "security_consideration": "401 vs 403 distinction; grants must always trace to approvals; direct API testing is mandatory because UI checks alone miss bypasses.",
        "root_cause_paths": [
            "Approval workflow bug allowed self-approval or stage skipping.",
            "Birthright/provisioning rule matched too broadly (wildcard department filter).",
            "Bulk import granted the role without the request pipeline.",
            "Role inheritance pulled admin capability into a standard role.",
            "Emergency break-glass access was never expired.",
        ],
        "strong_answer": (
            "First establish the facts: which role, granted when, through which path — the audit "
            "trail and the ACCESS_REQUESTS table answer that. Then I test the control: request the "
            "admin role through the UI as a normal employee and confirm approval is required and "
            "self-approval is impossible; then attack the API directly — the approve endpoint with "
            "my own token must return 403, request-ID tampering must fail, and calling the "
            "provisioning API directly must not grant anything. In SQL I look for role assignments "
            "whose dates do not line up with any approved request. The fix depends on the root "
            "cause — workflow bug, over-broad birthright rule, or a bulk import path — and whatever "
            "it is, I add a regression test so the bypass cannot silently return."
        ),
        "followups": [
            "How do you distinguish a workflow defect from a rule misconfiguration?",
            "What SoD checks would you add to prevent two roles combining into admin?",
            "How would you test break-glass access end-to-end including expiry?",
        ],
    },
    {
        "id": "scen-certification-revocation-fails",
        "title": "Access certification revocation not enforced",
        "severity": "critical",
        "topic": "IGA / Certifications",
        "situation": (
            "A manager revoked an entitlement during the Q4 access certification campaign. The "
            "campaign shows complete, but the user still has the entitlement in the target application."
        ),
        "interviewer_question": (
            "How would you test a certification campaign, and specifically the case where the "
            "manager revokes access but the application still shows it active?"
        ),
        "key_points": [
            "Campaign creation and population rules: every in-scope user/entitlement appears.",
            "Reviewer assignment correctness (right manager, delegation works).",
            "Approve / revoke / delegate / bulk actions behave per policy.",
            "Overdue items: auto-complete policy (confirm-all vs revoke-all) is a test condition.",
            "REVOKED decisions must trigger provisioning revocation downstream.",
            "Statistics: campaign dashboard numbers match database counts.",
            "Audit evidence for every decision including bulk actions.",
            "Failure paths: revocation task fails -> retry/escalation -> campaign cannot be marked complete.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Revoke decision removes entitlement downstream", "expected": "Target app role removed within policy time; database reflects it."},
            {"type": "negative", "title": "Revocation connector fails", "expected": "Retry; campaign marked incomplete; alert raised; no silent success."},
            {"type": "boundary", "title": "Overdue campaign auto-completes", "expected": "Default decision applied per policy (e.g. revoke-all) and audited."},
            {"type": "negative", "title": "Reviewer revoked the wrong item via bulk", "expected": "Undo/audit trail allows correction; revocation still accurate."},
        ],
        "api_checks": "Campaign status API; decision POST; campaign statistics endpoint vs database query.",
        "db_checks": "CERTIFICATIONS decision recorded; USER_ROLES rows actually removed for REVOKED entitlements; mismatch query is the key regression.",
        "job_checks": "The post-campaign revocation/provisioning job: schedule, execution, retry, completion status vs actual entitlement state.",
        "security_consideration": "A certification is a compliance artefact; unenforced decisions invalidate the entire campaign and its audit value.",
        "root_cause_paths": [
            "Decision saved but the revocation workflow never triggered.",
            "Revocation provisioning task failed and the campaign was marked complete anyway.",
            "Connector call succeeded but the target ignored it (partial processing).",
            "Reconciliation job not run / failed silently.",
            "The user was re-granted the same entitlement after the campaign by another path.",
        ],
        "strong_answer": (
            "I test the campaign as a pipeline: population rules (nobody missing), reviewer "
            "assignment, the decision actions including bulk and delegation, and then — the part "
            "most teams forget — enforcement. After a REVOKE decision I verify the entitlement is "
            "actually gone from the target application database, not just flagged in the campaign "
            "UI. For the specific failure I would compare the certification decision table against "
            "current role assignments with a SQL join, check the provisioning logs for the revoke "
            "operation and its retries, and inspect the post-campaign job. Then I test the failure "
            "paths deliberately: connector down during revocation, decision during a bulk action, "
            "and an overdue campaign auto-completing. A campaign that marks itself complete with "
            "unenforced decisions is the defect class my regression suite exists to catch."
        ),
        "followups": [
            "What does auto-complete-on-overdue do in your platform and how do you test it?",
            "How would you test population rules for 50,000 users efficiently?",
            "How do you validate campaign statistics dashboards against SQL?",
        ],
    },
    {
        "id": "scen-reconciliation-misses-records",
        "title": "Scheduled reconciliation job misses records",
        "severity": "high",
        "topic": "Scheduled jobs / Integration",
        "situation": (
            "The nightly reconciliation job reports SUCCESS. A QA data check finds 500 of "
            "10,000 HR records never reached the IGA platform."
        ),
        "interviewer_question": (
            "A scheduled job runs successfully according to the scheduler, but some user accounts "
            "are missing from the platform. How would you test it?"
        ),
        "key_points": [
            "Scheduler status is NOT business success: verify counts, not exit codes.",
            "Compare source count vs read vs processed vs failed vs target count.",
            "API pagination: was a page skipped or a continuation token mishandled?",
            "Correlation rules: which records failed to match (null emails, changed IDs, duplicates)?",
            "Rate limiting and timeouts mid-run: partial failure handling.",
            "Duplicate execution: idempotency — no duplicate identities created.",
            "Retries: failed records retried, and eventually escalated.",
            "Logs: per-record failure reasons, not just a job summary.",
        ],
        "test_cases": [
            {"type": "negative", "title": "API returns page 3 twice / skips page 4", "expected": "Job detects gap; re-reads; no records lost."},
            {"type": "negative", "title": "500 records fail correlation", "expected": "Failure table lists them with reasons; alert raised."},
            {"type": "boundary", "title": "Job executes twice in one night", "expected": "No duplicates; second run is a no-op (idempotent)."},
            {"type": "negative", "title": "Network timeout halfway through", "expected": "Partial progress persisted; resume from checkpoint, not full restart."},
        ],
        "api_checks": "Source API pagination behaviour, rate limit headers (429 handling), record counts per page, response schema drift.",
        "db_checks": "Count of identities vs source count; failure/exception tables; duplicate username check; missing email check.",
        "job_checks": "The job itself: schedule adherence, start/end times, checkpointing, retry counts, alerting on partial failure.",
        "security_consideration": "Missing identities mean missing governance (never certified, never deprovisioned); duplicate identities mean double provisioning.",
        "root_cause_paths": [
            "Pagination bug (skipped/duplicated page).",
            "Correlation rule rejects (changed employee ID, null email, duplicate match).",
            "Rate limiting caused silent drops.",
            "Timeout mid-batch with no checkpoint/resume.",
            "Transformation error on specific records (encoding, field length).",
        ],
        "strong_answer": (
            "The scheduler said SUCCESS, so I do not start from the scheduler — I start from counts: "
            "source records, records read by the job, records processed, records failed, and "
            "records present in the target. 10,000 vs 9,500 gives me exactly 500 to chase. I look "
            "at the failure table for correlation rejects, the API logs for pagination and rate "
            "limiting, and I test the failure modes deliberately: page skipping, timeouts halfway, "
            "duplicate execution. The acceptance criteria I write for any scheduled job are "
            "count-based and record-level, not 'the scheduler ticked success'. And idempotency is "
            "non-negotiable: running the job twice must never create duplicate identities."
        ),
        "followups": [
            "How would you design reconciliation count checks for 1M records nightly?",
            "What alerting would you add so this is caught before QA?",
            "How do you test that a job resumes from a checkpoint instead of restarting?",
        ],
    },
    {
        "id": "scen-duplicate-identities",
        "title": "Duplicate identities created for the same person",
        "severity": "high",
        "topic": "Reconciliation / Correlation",
        "situation": (
            "An employee re-joined after a 6-month break. Two identities now exist: one from the "
            "old HR record and one from the new one."
        ),
        "interviewer_question": "How would you test user correlation to prevent duplicate identities?",
        "key_points": [
            "Correlation rules: which fields match an incoming record to an identity (employee ID, email, name+DOB).",
            "Rehire scenarios: should the old identity be reactivated or a new one created per policy?",
            "Duplicate detection queries (username, email, fuzzy name).",
            "Merge behaviour: what happens to entitlements of both identities after a merge.",
            "Source data quality: duplicate employee IDs in HR, changed email format.",
            "No-match handling: create new vs reject and alert.",
            "Multiple-match handling: when two candidates match, the job must NOT pick arbitrarily.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Exact correlation match updates existing identity", "expected": "No duplicate created; identity updated."},
            {"type": "negative", "title": "Two candidate matches for one record", "expected": "Job rejects/escalates for manual review; no automatic wrong merge."},
            {"type": "boundary", "title": "Rehire after termination", "expected": "Policy applied (reactivate or new) consistently; old access NOT silently restored."},
            {"type": "negative", "title": "Null email and changed employee ID", "expected": "Record lands in the failure queue with reason, not a new identity."},
        ],
        "api_checks": "HR feed record shape; correlation API or import endpoint behaviour with ambiguous records.",
        "db_checks": "Duplicate username/email queries; two identities sharing an employee ID; entitlement counts on both.",
        "job_checks": "Nightly import: correlation-rule logs, reject counts, merge jobs.",
        "security_consideration": "Two identities for one person doubles attack surface and lets revoked access survive on the duplicate.",
        "root_cause_paths": [
            "Correlation rule too strict (exact email match, email changed).",
            "HR sent the rehire as a new employee ID instead of the original.",
            "Rule too loose: matched the wrong person and merged them (worse).",
            "Import ran twice non-idempotently.",
        ],
        "strong_answer": (
            "Correlation is a matching problem, so I test it like one: exact matches update, "
            "no-matches go to a failure queue with reasons, and multiple matches escalate rather "
            "than guess. I test rehire explicitly because old identities carry old entitlements — "
            "the policy must decide reactivate-vs-new, and either way the old access must not "
            "silently return. Duplicate detection is a set of SQL checks I keep in the regression: "
            "duplicate usernames, duplicate emails, and two identities for one employee ID. The "
            "scariest failure mode is a loose rule merging two DIFFERENT people — that is a data "
            "integrity incident, not a cleanup task, and it deserves its own test."
        ),
        "followups": [
            "How would you test a merge of two identities without losing entitlement evidence?",
            "What correlation rule would you recommend and why?",
            "How do you monitor for duplicates continuously rather than in campaigns?",
        ],
    },
    {
        "id": "scen-api-correct-ui-wrong",
        "title": "API returns correct data but UI displays wrong role",
        "severity": "medium",
        "topic": "Cross-layer debugging",
        "situation": (
            "GET /api/users/42 returns role RISK_ANALYST. The UI profile page for the same user "
            "shows ADMIN."
        ),
        "interviewer_question": (
            "The API returns the correct entitlement, but the UI shows an incorrect role. "
            "What would you do?"
        ),
        "key_points": [
            "Confirm the API response with an independent call (curl/Postman), not the app's own client.",
            "Inspect the actual network request/response the UI made (DevTools) — maybe a different endpoint.",
            "Check the frontend mapping: role code to display label transformation.",
            "Cache layers: browser cache, CDN, API gateway cache, frontend state management.",
            "Verify the database value as ground truth for what SHOULD be returned.",
            "Data transformation: response field used by UI (role vs effectiveRole vs roleName).",
            "Environment mismatch: which env is the UI pointed at vs the API call.",
            "Reproduce across browsers/users; find the exact trigger condition.",
        ],
        "test_cases": [
            {"type": "positive", "title": "API value matches database", "expected": "Confirms backend is correct; defect is frontend or cache."},
            {"type": "negative", "title": "UI renders stale cached value", "expected": "Cache invalidation on role change; hard refresh resolves it."},
            {"type": "negative", "title": "Frontend maps role code to wrong label", "expected": "Mapping table defect; unit-test the mapping."},
        ],
        "api_checks": "Direct API call with same token; response of the endpoint the UI actually hits; ETag/cache headers.",
        "db_checks": "USERS/USER_ROLES truth for user 42 — defines which layer is wrong.",
        "job_checks": "Any cache-warming or sync job between backend and frontend store.",
        "security_consideration": "A UI displaying higher privileges than the user has is alarming; the reverse (showing fewer) can hide real access from reviewers.",
        "root_cause_paths": [
            "Frontend uses a different endpoint or field than the one tested.",
            "Role code-to-label mapping table defect.",
            "Stale cache (browser/gateway/state store) after a role change.",
            "UI pointed at a different environment.",
            "Effective-role calculation includes an inherited role the API call omits.",
        ],
        "strong_answer": (
            "I start by establishing the truth in layers: the database says what SHOULD be true, "
            "the API says what the backend serves, and the network tab says what the UI actually "
            "requested and received. If the API matches the database but the UI differs, the "
            "defect is frontend-side or cache-side: wrong field mapping, a different endpoint, or "
            "a stale cache. I have debugged exactly this class of issue across UI, API, SQL and "
            "integration logs — the discipline is to pin the boundary where correct becomes "
            "incorrect, and only then file a defect against the right team. And I add the "
            "cross-layer check to automation: UI role display must equal API role must equal "
            "database role."
        ),
        "followups": [
            "How would you automate this three-layer comparison?",
            "Which cache layers would you inspect in order?",
            "What if the UI is right and both API and database are wrong?",
        ],
    },
    {
        "id": "scen-provisioning-partial-failure",
        "title": "Provisioning job fails halfway",
        "severity": "high",
        "topic": "Provisioning",
        "situation": (
            "Onboarding 50 new joiners, the provisioning job created accounts in 3 of 6 "
            "applications and then stopped."
        ),
        "interviewer_question": "How would you test a provisioning workflow that fails partway through?",
        "key_points": [
            "Per-application task status visibility: which succeeded, which failed, which never started.",
            "Retry semantics: only failed/pending tasks retry; successes are not duplicated.",
            "Idempotency: re-running creates no duplicate accounts.",
            "Partial-failure state exposed to the user/admin (not silently 'done').",
            "Error classification: transient (network) vs permanent (validation) with different retry policies.",
            "Compensation/rollback expectations where applicable.",
            "Ordering: apps with dependencies (account before role).",
            "Alerting and escalation for stuck tasks.",
        ],
        "test_cases": [
            {"type": "negative", "title": "Connector down on app 4 of 6", "expected": "Apps 1-3 complete; app 4 retried/alerted; apps 5-6 behaviour documented (continue or pause)."},
            {"type": "boundary", "title": "Retry the whole job after partial failure", "expected": "No duplicates; only incomplete work executes."},
            {"type": "negative", "title": "Validation error on one user", "expected": "That user fails permanently with reason; other users unaffected."},
        ],
        "api_checks": "Provisioning task API statuses; connector error responses (500/429/timeout) handling.",
        "db_checks": "PROVISIONING_LOGS per user+app; account existence per target; duplicate check.",
        "job_checks": "Job checkpointing; retry count and backoff; completion criteria (all tasks or documented partial).",
        "security_consideration": "Half-provisioned users may get partial access — access without governance (no certification) because the identity is incomplete.",
        "root_cause_paths": [
            "Job aborts on first error (no per-item isolation).",
            "Retry storm after a transient outage.",
            "Non-idempotent connector creating duplicates on retry.",
            "Checkpoint corruption after a crash.",
        ],
        "strong_answer": (
            "I test partial failure as a first-class scenario, not an edge case afterthought: "
            "fail one connector out of six, verify the other five complete, the failed one retries "
            "with backoff, statuses are visible per application, and re-running the job is "
            "idempotent — no duplicate accounts. Then the nastier variants: the connector "
            "returning 500 mid-batch, rate limiting, and a crash between checkpoint writes. The "
            "acceptance criteria I hold any provisioning workflow to: every task has a final "
            "status, failures are retried or escalated, and the job can never report success with "
            "silent gaps."
        ),
        "followups": [
            "How would you test crash recovery (checkpointing)?",
            "When is rollback the right design vs retry?",
            "How do you verify idempotency at the connector level?",
        ],
    },
    {
        "id": "scen-downstream-unavailable",
        "title": "Downstream application unavailable during provisioning",
        "severity": "medium",
        "topic": "Integration resilience",
        "situation": "During a termination event, the CRM application was down for maintenance. The deprovisioning workflow could not complete.",
        "interviewer_question": "How would you test integration behaviour when a downstream application is unavailable?",
        "key_points": [
            "Failure mode of the integration: fail-open vs fail-closed per documented policy.",
            "Retry policy: attempts, backoff, terminal failure.",
            "State after terminal failure: identity marked incomplete, escalation opened.",
            "Recovery: when the app returns, does a reconciliation catch up the missed change.",
            "Timeouts vs connection refused vs 500 vs 429 — each handled distinctly.",
            "Queue durability: events not lost while the target is down.",
            "Monitoring/alerting on integration health.",
        ],
        "test_cases": [
            {"type": "negative", "title": "Target down during deprovisioning", "expected": "Retry with backoff; identity shows incomplete; alert raised."},
            {"type": "boundary", "title": "Target returns before retries exhausted", "expected": "Change applies on next retry; no duplicates."},
            {"type": "boundary", "title": "Target returns after retries exhausted", "expected": "Reconciliation or manual retry path completes the change."},
            {"type": "negative", "title": "Timeout vs refused vs 500", "expected": "Each handled per policy (retryable vs not); no lost events."},
        ],
        "api_checks": "Connector behaviour on timeouts, refused connections, 5xx, 429; queue depth monitoring.",
        "db_checks": "PROVISIONING_LOGS failures; identity 'incomplete' state; eventual consistency after recovery.",
        "job_checks": "Retry scheduler; reconciliation sweep as the safety net.",
        "security_consideration": "Fail-open on deprovisioning means revoked access stays live; the missing change must be visible, not silent.",
        "root_cause_paths": [
            "Retry policy too shallow (gave up before maintenance window ended).",
            "Event queue not durable — the change was lost entirely.",
            "Terminal failure marked silently complete.",
            "Reconciliation disabled or too infrequent to catch up.",
        ],
        "strong_answer": (
            "I read the designed failure policy first — that is my oracle — then force each failure "
            "mode: connection refused, timeout, 500, 429, and a long maintenance outage. I verify "
            "retries with backoff, an incomplete state on the identity rather than a silent "
            "success, an alert, and — critically — that when the application comes back the "
            "change eventually applies, either through retry or reconciliation. For security "
            "operations like deprovisioning I check fail-closed semantics: an unavailable target "
            "must never be treated as 'probably fine'. Lost events are the worst defect here, so "
            "I verify queue durability too."
        ),
        "followups": [
            "How would you design the reconciliation safety net for this?",
            "What backoff schedule would you recommend?",
            "How do you prove no events were lost?",
        ],
    },
    {
        "id": "scen-mfa-bypass",
        "title": "MFA bypass attempt succeeds",
        "severity": "critical",
        "topic": "Authentication",
        "situation": "A penetration test found that calling the session API directly after a password-only login returns a valid session.",
        "interviewer_question": "How would you test MFA to make sure it cannot be bypassed?",
        "key_points": [
            "Test the full flow: password -> OTP -> session; each stage enforced server-side.",
            "Direct API calls must not skip stages (session endpoint requires MFA-complete state).",
            "OTP validity window: expired OTP rejected; consumed OTP cannot be replayed.",
            "Lockout after N wrong OTPs; cooldown and notification.",
            "Recovery flows must re-verify identity, not become a bypass.",
            "Remember-device flows: trusted device flags must expire per policy.",
            "OTP delivery failures: retry limits, alternate channel.",
            "Race conditions: concurrent attempts, multiple valid OTPs.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Valid password + valid OTP", "expected": "Session issued with MFA claim."},
            {"type": "negative", "title": "Call session API after password only", "expected": "403/401; MFA incomplete; attempt logged."},
            {"type": "negative", "title": "Replay a consumed OTP", "expected": "Rejected as invalid."},
            {"type": "boundary", "title": "OTP at expiry boundary", "expected": "Exactly at exp rejected (NotOnOrAfter semantics)."},
            {"type": "negative", "title": "5 wrong OTPs", "expected": "Account locks; notification sent."},
        ],
        "api_checks": "Session/login endpoints called out of order; MFA state token tampering; response codes 401 vs 403.",
        "db_checks": "MFA enrolment state; OTP consumption records; lockout counters.",
        "job_checks": "Lockout reset/cooldown jobs; trusted-device expiry cleanup.",
        "security_consideration": "Client-side MFA gating without server-side enforcement is a critical auth bypass — test at the API layer always.",
        "root_cause_paths": [
            "MFA check enforced in UI flow only, not on the session API.",
            "MFA-complete flag forgeable in the token/cookie.",
            "Recovery path skips MFA entirely.",
            "Trusted-device flag never expires.",
        ],
        "strong_answer": (
            "MFA is only real if the SERVER enforces the sequence, so I test at the API layer: "
            "after password-only login, every session-issuing endpoint must refuse me. Then the "
            "lifecycle: expired and replayed OTPs rejected, lockout after N failures, recovery "
            "re-verifying identity instead of bypassing, and trusted-device flags that actually "
            "expire. I also probe race conditions — two concurrent logins, one OTP used twice in "
            "parallel. Any UI-enforced-only MFA is a critical finding, and my automated regression "
            "keeps the direct-API attempt in the suite permanently so the bypass stays closed."
        ),
        "followups": [
            "How would you test OTP delivery failures?",
            "What race conditions exist in concurrent MFA attempts?",
            "How do you test 'remember this device' securely?",
        ],
    },
    {
        "id": "scen-expired-token",
        "title": "Expired access token still accepted",
        "severity": "critical",
        "topic": "Tokens",
        "situation": "A token captured 3 days ago still authorises API calls although policy says 60 minutes.",
        "interviewer_question": "How would you test token expiry and revocation?",
        "key_points": [
            "Expiry enforced server-side from claims (exp), not from client clock.",
            "Boundary: token used at exactly exp must be rejected.",
            "Refresh token flow: rotation, reuse detection.",
            "Revocation: logout/kill-session must invalidate or deny-list tokens.",
            "Clock skew tolerance documented and tested.",
            "Token audience and issuer validated along with expiry.",
            "Session vs token lifetime: UI session may outlive API token or vice versa.",
        ],
        "test_cases": [
            {"type": "boundary", "title": "Token at exact expiry", "expected": "Rejected; 401 with expiry error code."},
            {"type": "positive", "title": "Refresh before expiry", "expected": "New access token issued; old one still honoured until exp."},
            {"type": "negative", "title": "Reuse a rotated refresh token", "expected": "Rejected; possibly revokes the token family per policy."},
            {"type": "negative", "title": "Revoked token after logout", "expected": "Rejected by deny-list or short expiry window."},
        ],
        "api_checks": "Bearer token with manipulated exp; wrong aud/iss; signature tampering.",
        "db_checks": "Token deny-list/jti store; session records.",
        "job_checks": "Deny-list cleanup jobs; session reaper.",
        "security_consideration": "Long-lived unrevocable tokens extend the blast radius of any token leak.",
        "root_cause_paths": [
            "Expiry validated client-side only.",
            "exp claim ignored (signature checked, claims not).",
            "Refresh token reuse not detected.",
            "Deny-list lookup skipped under load.",
        ],
        "strong_answer": (
            "I treat the token as a contract and test every clause: signature, issuer, audience, "
            "and expiry — including the exact boundary where exp is now. I verify the server uses "
            "its own clock, not a client-sent timestamp. Refresh flows get their own tests: "
            "rotation works, reuse of an old refresh token is detected, and after logout the "
            "refresh path is dead even if the access token has minutes left. Revocation testing "
            "matters because JWTs are stateless — the system needs short expiry or a deny-list, "
            "and whichever it claims, I verify the actual behaviour."
        ),
        "followups": [
            "How do you test clock skew between issuer and resource server?",
            "What is token family revocation on refresh reuse?",
            "How would you load-test deny-list lookups?",
        ],
    },
    {
        "id": "scen-unauthorized-api-access",
        "title": "Unauthorized API access attempts",
        "severity": "high",
        "topic": "API security",
        "situation": "The new entitlement API is supposed to be admin-only. A curious employee found it in the API docs.",
        "interviewer_question": "How would you test authorization on a security-sensitive API?",
        "key_points": [
            "Every endpoint: default deny, allow only per role.",
            "401 vs 403 correctness.",
            "IDOR: access other users' resources by ID manipulation.",
            "Method-level checks: GET allowed, POST forbidden for viewer role.",
            "Vertical privilege escalation (user -> admin) and horizontal (user -> other user).",
            "Rate limiting and brute-force protection.",
            "Injection probes (SQL, command) on parameters.",
            "Audit logging of denied attempts.",
        ],
        "test_cases": [
            {"type": "negative", "title": "Employee token on admin endpoint", "expected": "403; no data leak in error body; logged."},
            {"type": "negative", "title": "IDOR: user A requests user B's record", "expected": "403/404, never 200 with data."},
            {"type": "negative", "title": "No token at all", "expected": "401."},
            {"type": "boundary", "title": "Role with overlapping scopes", "expected": "Most restrictive policy applies per documentation."},
        ],
        "api_checks": "This whole scenario is API-level testing: status codes, bodies, headers, rate limits.",
        "db_checks": "Confirm no writes occurred from denied requests (server-side enforcement, not just response filtering).",
        "job_checks": "Rate-limit counters reset; audit log shipping.",
        "security_consideration": "Response filtering (hiding a button) is not authorization; enforcement must be server-side.",
        "root_cause_paths": [
            "Endpoint missing role annotation/middleware.",
            "Object-level checks absent (IDOR).",
            "Authorization only in the UI layer.",
            "Overly broad default policy.",
        ],
        "strong_answer": (
            "I build an authorization matrix first — roles vs endpoints vs methods — and execute "
            "it as an API suite: every cell either allows or denies per policy, with 401 and 403 "
            "semantics exact. Then the attacks: IDOR by swapping IDs, tampering with request "
            "bodies, and vertical escalation attempts. I verify server-side enforcement by "
            "checking the database after denied calls — nothing should have been written. Denied "
            "attempts must be logged, because authorization failures are security events. This "
            "matrix suite is cheap to maintain and catches regressions the moment a new endpoint "
            "ships without its role guard."
        ),
        "followups": [
            "How would you keep the authorization matrix suite in sync with new endpoints?",
            "What is the difference between horizontal and vertical escalation?",
            "How do you test rate limiting without locking out real users?",
        ],
    },
    {
        "id": "scen-privilege-escalation",
        "title": "Privilege escalation through role inheritance",
        "severity": "critical",
        "topic": "RBAC",
        "situation": "A new QA_LEAD role was created inheriting from both QA_AUTOMATION and SYS_ADMIN 'temporarily' during testing.",
        "interviewer_question": "How would you test for unintended privilege escalation through role definitions?",
        "key_points": [
            "Role hierarchy: inherited permissions must be enumerated and reviewed.",
            "Effective permissions = direct + inherited; test the union, not the direct list.",
            "SoD conflicts: role combinations that violate separation of duties.",
            "Creation/modification of roles requires approval and is audited.",
            "Wildcard or overly broad entitlements inside role definitions.",
            "Assignment of the role follows the same request/approval path as any entitlement.",
            "Regression: role model changes must trigger an effective-permission re-computation.",
        ],
        "test_cases": [
            {"type": "negative", "title": "QA_LEAD effective permissions enumerated", "expected": "Contains exactly the documented set; SYS_ADMIN inherited is a finding."},
            {"type": "boundary", "title": "SoD pair check", "expected": "Roles flagged as conflicting cannot be co-assigned (or require exception approval)."},
            {"type": "positive", "title": "Role change triggers re-computation", "expected": "All holders' effective permissions update within policy time."},
        ],
        "api_checks": "Effective-permissions endpoint for a user vs documented role model.",
        "db_checks": "Role inheritance table; join to compute effective permissions per user.",
        "job_checks": "Permission re-computation job after role model changes.",
        "security_consideration": "Privilege creep through inheritance is silent: nobody 'granted' admin, the model grew into it.",
        "root_cause_paths": [
            "Temporary inheritance never removed.",
            "Role created by copying an admin role as a template.",
            "Inheritance chain longer than governance review covers.",
            "SoD matrix not enforced at assignment time.",
        ],
        "strong_answer": (
            "Roles are code — they need regression tests too. I test effective permissions, not "
            "role labels: for every user holding the new role, enumerate the union of direct and "
            "inherited entitlements and compare against the approved definition. Any undocumented "
            "permission is a finding. I also test the governance around roles: creating or editing "
            "a role requires approval, is audited, and triggers re-computation for all holders. "
            "The temporary-inheritance story in this scenario is exactly how real incidents "
            "happen — nobody granted admin to QA, a role MODEL change did it silently."
        ),
        "followups": [
            "How would you visualise/report a role inheritance tree for auditors?",
            "What SoD rule pairs would you propose for an IAM platform?",
            "How often should role models be re-certified?",
        ],
    },
    {
        "id": "scen-stale-sessions",
        "title": "Stale user sessions after deactivation",
        "severity": "critical",
        "topic": "Session management",
        "situation": "A user was deactivated at 10:00. Their browser session from 09:30 still works at 11:00.",
        "interviewer_question": "How would you test that deactivating or terminating a user kills active sessions?",
        "key_points": [
            "Deactivation must invalidate sessions server-side, not just block new logins.",
            "Token-based sessions: deny-list or short expiry to enforce revocation.",
            "SSO: IdP logout propagation to all SPs including downstream apps.",
            "Absolute and idle timeouts enforced per policy.",
            "API sessions and mobile clients, not just browser.",
            "Concurrent-session limits per policy.",
            "Delay tolerance: how quickly after deactivation must sessions die (SLA).",
        ],
        "test_cases": [
            {"type": "negative", "title": "Active session after deactivation", "expected": "Terminated within policy SLA; next request 401."},
            {"type": "boundary", "title": "In-flight request during deactivation", "expected": "Documented behaviour: completed or rejected, not zombie."},
            {"type": "negative", "title": "SSO logout propagation", "expected": "All SP sessions dead after IdP logout."},
        ],
        "api_checks": "Call protected APIs with pre-deactivation tokens; verify 401 after policy window.",
        "db_checks": "Session store records; token deny-list entries.",
        "job_checks": "Session reaper job; deny-list propagation.",
        "security_consideration": "The gap between deactivation and session death is a live attack window with valid credentials.",
        "root_cause_paths": [
            "Sessions validated only against local token expiry, not user state.",
            "Deny-list propagation lag or failure.",
            "SSO SP sessions not terminated on IdP logout.",
            "Session reaper interval too long.",
        ],
        "strong_answer": (
            "I test the time window explicitly: establish a session, deactivate the user, then "
            "poll protected endpoints — the session must die within the documented SLA, and the "
            "next request must return 401. I test all client types (browser, API token, mobile) "
            "and the SSO case where IdP logout must propagate to every SP. The root cause is "
            "usually sessions that validate only against token expiry instead of user state, so "
            "my regression asserts the server-side check. The window between deactivation and "
            "session death is a live attack window — that framing gets attention in defect "
            "reports."
        ),
        "followups": [
            "What session invalidation SLA would you demand?",
            "How would you test this for 50 downstream applications?",
            "How do refresh tokens complicate this?",
        ],
    },
    {
        "id": "scen-missing-audit-logs",
        "title": "Audit logs missing for a security event",
        "severity": "high",
        "topic": "Auditability",
        "situation": "An admin made a bulk role change. The audit search returns no entry for it.",
        "interviewer_question": "How would you test audit logging of security-relevant actions?",
        "key_points": [
            "Every security action logged: who, what, when, from where, result.",
            "Bulk operations logged per-item AND as a summary.",
            "Log integrity: entries cannot be edited or deleted by the actor.",
            "Denied attempts logged, not just successes.",
            "Correlation IDs linking UI action -> API call -> DB change -> provisioning.",
            "Retention per policy; no silent drops (queue durability).",
            "Timestamps consistent (UTC) and ordered.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Single role change logged", "expected": "Entry with actor, target, old/new value, timestamp, source IP."},
            {"type": "boundary", "title": "Bulk change of 100 users", "expected": "Per-item entries plus a bulk summary; count matches."},
            {"type": "negative", "title": "Failed/denied action logged", "expected": "Denied attempts recorded with reason."},
            {"type": "negative", "title": "Actor attempts to delete own audit entry", "expected": "Impossible; attempt itself logged."},
        ],
        "api_checks": "Audit API search by correlation ID; completeness of fields.",
        "db_checks": "Audit table inserts per action; bulk item counts.",
        "job_checks": "Log shipping/retention jobs; queue backlog monitoring.",
        "security_consideration": "Unlogged security actions break compliance (SOX/GDPR evidence) and incident response.",
        "root_cause_paths": [
            "Bulk path bypassed the single-item logging wrapper.",
            "Async log queue dropped entries under load.",
            "New endpoint shipped without the audit middleware.",
            "Log write failure swallowed silently.",
        ],
        "strong_answer": (
            "Audit logging is a functional requirement of a security platform, so I test it like "
            "one: for a representative action set — single change, bulk change, denied attempt, "
            "login, provisioning — I assert an entry exists with the full context (actor, target, "
            "old/new values, timestamp, source) and that the count matches for bulk operations. "
            "I test integrity: the actor cannot edit or delete entries. And I test durability: "
            "log shipping under load must not drop entries. The most common real bug is the bulk "
            "path bypassing the single-item logging wrapper — so bulk gets its own test with "
            "exact count assertions."
        ),
        "followups": [
            "How would you verify log completeness for 10k events under load?",
            "What correlation ID design links layers end-to-end?",
            "What retention policy checks would you automate?",
        ],
    },
    {
        "id": "scen-rbac-mapping-wrong",
        "title": "Incorrect RBAC mapping between systems",
        "severity": "high",
        "topic": "Integration / RBAC",
        "situation": "The IGA role RISK_ANALYST maps to target-app group 'risk-users' — but in the target app that group has write access to claims data.",
        "interviewer_question": "How would you test role-to-entitlement mappings between the IGA platform and target applications?",
        "key_points": [
            "Mapping table completeness: every IGA role has a defined target mapping (or documented none).",
            "Mapping accuracy: the target-side group actually grants what the design says.",
            "Direction of trust: target permissions can drift even when the mapping is unchanged.",
            "Unmapped roles fail loudly (visible error) not silently (no access).",
            "Mapping changes follow change control and are regression-tested.",
            "Effective access validation: log in as a user with the role and observe real capabilities.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Every mapped role grants the designed target permission", "expected": "Matrix verified per application."},
            {"type": "negative", "title": "Unmapped role assignment", "expected": "Provisioning reports unmapped role; flagged, not silent."},
            {"type": "boundary", "title": "Target group permissions drift", "expected": "Reconciliation/mapping validation detects drift."},
        ],
        "api_checks": "Target app group membership API after provisioning.",
        "db_checks": "Mapping table vs target group definitions vs actual permissions.",
        "job_checks": "Mapping validation job; reconciliation sweep.",
        "security_consideration": "A correct IGA decision executed through a wrong mapping becomes wrong access — governance is only as good as the mapping layer.",
        "root_cause_paths": [
            "Mapping configured against the wrong target group.",
            "Target-side group permissions changed without IGA knowledge.",
            "Wildcards in mapping matched unintended groups.",
            "New role created without a mapping review.",
        ],
        "strong_answer": (
            "I test mappings as data contracts: every role must map to a documented target "
            "definition, and I verify the target side too — because the target group's own "
            "permissions can drift even when the IGA mapping never changed. The strongest test "
            "is capability-based: provision a test user with the role, then exercise the target "
            "application and observe what they can actually DO, comparing it to the design. "
            "Unmapped roles must fail loudly — silent no-access is a defect that looks like a "
            "user problem. And mapping changes go through the same regression as code, because "
            "they ARE code."
        ),
        "followups": [
            "How would you automate capability checks across 20 target apps?",
            "Who owns fixing drift — the IGA team or the app team?",
            "How do you version control mappings?",
        ],
    },
    {
        "id": "scen-dlp-fails-to-block",
        "title": "DLP policy fails to block sensitive data",
        "severity": "critical",
        "topic": "DLP",
        "situation": "A tester emailed a spreadsheet of card numbers to a personal Gmail address. The mail was delivered.",
        "interviewer_question": "How would you test a DLP policy that should block sensitive data leaving the organisation?",
        "key_points": [
            "Policy as test oracle: read the documented rule (content, channels, action).",
            "Labelled corpus: known-sensitive and benign samples per classification.",
            "Channel coverage: email, upload, USB, print, clipboard, sharing links.",
            "Obfuscation: renamed files, zip, split archives, spaced digits, images of text.",
            "Context rules: internal vs external recipient, group membership.",
            "False positive rate on benign corpus measured, not anecdotal.",
            "Fail-open/fail-closed behaviour when the engine is down.",
            "Incident records created for every enforcement action.",
        ],
        "test_cases": [
            {"type": "negative", "title": "Card numbers to external domain", "expected": "Blocked/quarantined per policy; incident logged."},
            {"type": "positive", "title": "Same content to internal recipient", "expected": "Allowed per policy (or encrypted) — proves context rules."},
            {"type": "boundary", "title": "Renamed/re-zipped file", "expected": "Still detected (content inspection)."},
            {"type": "boundary", "title": "Benign lookalike content", "expected": "Allowed — false positive measured and trending."},
        ],
        "api_checks": "Where the channel is an API (upload endpoints, sharing APIs), probe directly for enforcement.",
        "db_checks": "Incident/quarantine records; policy evaluation logs.",
        "job_checks": "Quarantine retention, retro-scan jobs after engine downtime.",
        "security_consideration": "Every false negative is potential data exfiltration; every false positive erodes trust and drives users to workarounds.",
        "root_cause_paths": [
            "Rule scoped to wrong channel or direction.",
            "Content pattern does not cover the format used (spaced digits, different locale).",
            "Attachment type not inspected (inside zip/new format).",
            "Policy disabled after a change; no regression test existed.",
        ],
        "strong_answer": (
            "I start from the policy document because that is the oracle, then build a labelled "
            "corpus — sensitive samples per classification and benign lookalikes — and run it "
            "through every channel: email, upload, USB, print. I test obfuscation deliberately "
            "because attackers and users do: renamed files, zip, spaced digits, partial masking. "
            "I measure both false negatives (leaks) and false positives (blocked legitimate work) "
            "as rates over the corpus, so rule tuning has numbers behind it. And I test the "
            "engine-down behaviour — fail-open for email means sensitive data can flow "
            "uninspected, and if policy says fail-closed, mail must queue. Honest framing: I "
            "haven't implemented DLP, but policy-engine testing is exactly the pattern I've used "
            "on IAM entitlement rules."
        ),
        "followups": [
            "How would you keep the corpus current as detection rules evolve?",
            "What metrics would you report to the security team monthly?",
            "How do you test encrypted channels like TLS webmail uploads?",
        ],
    },
    {
        "id": "scen-duplicate-job-execution",
        "title": "Scheduled job runs twice",
        "severity": "medium",
        "topic": "Scheduled jobs",
        "situation": "The provisioning job overlapped with itself due to a scheduler misconfiguration — accounts were created twice for some users.",
        "interviewer_question": "How would you test that a scheduled job executing twice does not corrupt data?",
        "key_points": [
            "Idempotency: same input -> same final state, no duplicates.",
            "Locking/leader election prevents overlap; overlapping attempts logged.",
            "Duplicate detection queries after double execution.",
            "Checkpoint/resume semantics under double-trigger.",
            "Monitoring: job duration vs interval (overlap detection).",
            "Data uniqueness constraints at the DB level as the last line of defence.",
        ],
        "test_cases": [
            {"type": "boundary", "title": "Trigger job twice concurrently", "expected": "One effective run; second blocked or a clean no-op."},
            {"type": "boundary", "title": "Second run starts before first finishes", "expected": "Lock prevents overlap; alert on contention."},
            {"type": "negative", "title": "Duplicate suppression missing", "expected": "Finding raised with duplicate row evidence."},
        ],
        "api_checks": "Trigger endpoint double-invocation; scheduler API overlap configuration.",
        "db_checks": "Duplicate username/account queries; unique constraint violations.",
        "job_checks": "The job itself: lock acquisition, overlap alerts, run history.",
        "security_consideration": "Duplicate accounts can mean duplicate entitlements and inconsistent audit identity.",
        "root_cause_paths": [
            "No distributed lock across scheduler nodes.",
            "Retry policy re-ran completed work (no checkpoint check).",
            "Cron misconfiguration (interval shorter than duration).",
            "No unique constraint on the target table.",
        ],
        "strong_answer": (
            "The test is simple to state and rare to see executed: trigger the job twice, "
            "concurrently, and assert the final state is identical to a single run — no duplicate "
            "accounts, no duplicated grants, no double emails. Then verify the guard rails: "
            "locking behaviour with an alert when overlap is attempted, checkpointing so a retry "
            "resumes instead of redoing, and database unique constraints as the last line of "
            "defence. I keep a duplicate-detection SQL pair in the regression for exactly this "
            "class of defect: duplicate usernames and duplicate role assignments."
        ),
        "followups": [
            "How would you design locking for a multi-node scheduler?",
            "What DB constraints would you recommend on identity tables?",
            "How do you detect overlap in production monitoring?",
        ],
    },
    {
        "id": "scen-db-ui-inconsistency",
        "title": "Database and UI disagreement",
        "severity": "medium",
        "topic": "Cross-layer debugging",
        "situation": "The entitlement count on the governance dashboard says 1,204. The database query returns 1,187.",
        "interviewer_question": "The dashboard count does not match the database. How would you investigate and test it?",
        "key_points": [
            "Reproduce with exact filters — dashboards apply filters the raw query may not.",
            "Identify which layer computes the number: UI aggregation, API aggregation, or a materialised table.",
            "Time skew: cached aggregates vs live data (jobs refresh frequency).",
            "Off-by-one/row-limit bugs in aggregation.",
            "Distinguish stale data (refresh problem) from wrong logic (calculation problem).",
            "Cross-layer automated check: UI number == API number == SQL number.",
            "Document acceptable staleness SLA for dashboards.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Fresh change reflected in dashboard within SLA", "expected": "Counts converge after the refresh window."},
            {"type": "negative", "title": "Numbers differ beyond staleness window", "expected": "Defect with exact reproducible filter set."},
            {"type": "boundary", "title": "Row at page/filter boundary", "expected": "Count logic consistent at edges."},
        ],
        "api_checks": "The aggregation API behind the widget vs a direct query with the same filters.",
        "db_checks": "The ground-truth query — replicate the dashboard's documented filter logic.",
        "job_checks": "The refresh/materialisation job schedule and last success.",
        "security_consideration": "Stale dashboards hide orphaned access — reviewers certify against wrong numbers.",
        "root_cause_paths": [
            "Dashboard uses a cached aggregate refreshed on a lagging schedule.",
            "Aggregation logic differs from the documented filter definition.",
            "Materialised table partially refreshed (job failure).",
            "Timezone boundary in date filters.",
        ],
        "strong_answer": (
            "First I make the comparison fair: same filters, same time window, same definitions — "
            "half of these defects are filter mismatch, not bugs. Then I locate where the number "
            "is computed — a live API, a cached aggregate or a materialised table — because that "
            "decides whether this is staleness or wrong logic. I reproduce, capture both numbers "
            "with timestamps, and file with a precise filter set. Long term I automate the "
            "three-way check — UI number, API number, SQL number — as part of my dashboard "
            "validation suite, which is exactly the kind of SQL-based validation I did on IAM "
            "analytics dashboards at Admiral."
        ),
        "followups": [
            "How would you automate dashboard-vs-database validation at scale?",
            "What staleness SLA is acceptable for governance dashboards?",
            "How do filters usually cause these mismatches?",
        ],
    },
    {
        "id": "scen-high-api-latency",
        "title": "High API latency under load",
        "severity": "medium",
        "topic": "Performance",
        "situation": "The entitlement search API takes 8 seconds at P95 during peak hours; SLA is 2 seconds.",
        "interviewer_question": "How would you investigate and test an API performance bottleneck?",
        "key_points": [
            "Baseline first: single-user latency, then load steps (not a jump to peak).",
            "Percentiles over averages: P50/P95/P99 tell the real story.",
            "Correlate latency with concurrency, data volume and DB query time.",
            "Bottleneck isolation: app tier, DB (missing index, N+1), network, external calls.",
            "Soak tests for degradation over time (memory leaks, connection pool exhaustion).",
            "Compare against SLA with the team's agreed percentile definition.",
            "Environment realism: data volume comparable to production.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Baseline single-user", "expected": "Latency profile recorded before load."},
            {"type": "boundary", "title": "Step load to peak concurrency", "expected": "P95 within SLA; throughput scales; errors 0."},
            {"type": "negative", "title": "Stress beyond peak", "expected": "Graceful degradation, no crash, recovery after load drops."},
            {"type": "boundary", "title": "Soak for hours", "expected": "No drift, no leak, latency stable."},
        ],
        "api_checks": "Latency measurement per endpoint; percentiles not just mean; error rates under load.",
        "db_checks": "Slow query logs; execution plans for the underlying queries; index coverage.",
        "job_checks": "Cache warming, connection pool sizing, batch jobs competing for the DB during peak.",
        "security_consideration": "Under stress, some systems skip deny-list lookups or degrade logging — verify security controls under load too.",
        "root_cause_paths": [
            "Missing DB index on the filter column.",
            "N+1 query pattern in the API implementation.",
            "Connection pool exhausted under concurrency.",
            "External call inside the request path without timeout.",
        ],
        "strong_answer": (
            "I baseline before I load: single-user latency, then step up concurrency while "
            "watching P50/P95/P99 — averages hide the tail that users actually feel. I correlate "
            "latency with database query time to localise the bottleneck: app tier, query plan, "
            "or an external call in the request path. Then soak tests for degradation over time. "
            "The report I hand over includes percentile graphs against the SLA line, the "
            "bottleneck evidence (slow query log, pool metrics), and a rerun after the fix to "
            "prove the improvement. One thing I always add for security platforms: verify "
            "authorization checks and audit logging still happen under load — performance "
            "features must never be bought by skipping security."
        ),
        "followups": [
            "How do you choose the SLA percentile to report?",
            "What tooling would you use and why?",
            "How do you keep performance tests reproducible in CI?",
        ],
    },
    {
        "id": "scen-broken-regression-pipeline",
        "title": "Broken CI/CD regression pipeline",
        "severity": "medium",
        "topic": "CI/CD",
        "situation": "The nightly regression failed 40% of tests after a shared test environment was rebuilt. Nobody trusts the suite's results anymore.",
        "interviewer_question": "Your regression pipeline is red and flaky. How do you restore trust in it?",
        "key_points": [
            "Triage first: classify failures — product defect, environment issue, automation defect, test data.",
            "Quarantine true flaky tests with owners and dates; do not delete.",
            "Environment: verify config, seeded data, service versions, credentials before blaming tests.",
            "Stabilise: explicit waits, isolated test data per test, no inter-test dependencies.",
            "Make results actionable: failure categories, links to logs/screenshots, dashboard trend.",
            "Definition of done: pipeline green means trustworthy signal, not noise.",
            "Parallel execution and retry budgets: retries are for known flakes, with reporting.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Failure categorisation workflow", "expected": "Every red test classified within a day."},
            {"type": "boundary", "title": "Rebuild environment reproducibly", "expected": "Same infra-as-code + seed = same result."},
            {"type": "negative", "title": "Flaky test identified", "expected": "Quarantined with ticket; not silently retried forever."},
        ],
        "api_checks": "Health checks as pipeline pre-flight gates: environment readiness before suites.",
        "db_checks": "Test data state assertions before suites (seed checksums).",
        "job_checks": "The pipeline itself: ordering, parallel isolation, retry policy, notifications.",
        "security_consideration": "A suite nobody trusts is a governance gap — security regressions ship unnoticed.",
        "root_cause_paths": [
            "Environment rebuild changed config/data (not test changes at all).",
            "Shared mutable test data across parallel tests.",
            "Implicit waits removed or timing regressions.",
            "Credential/token expiry in the pipeline.",
        ],
        "strong_answer": (
            "Trust is restored by making failure signals meaningful. I triage the 40% into "
            "categories — product, environment, automation, data — because each has a different "
            "owner and fix. In this scenario the environment rebuild is the prime suspect: I "
            "verify service versions, config and seeded data before touching any test. Then I "
            "quarantine genuinely flaky tests with owners and expiry dates so the pipeline "
            "signal becomes honest again, and I fix root causes: isolated test data, proper "
            "waits, no inter-test dependencies. When I migrated our Selenium framework to "
            "Playwright I cut our regression from roughly 60 to 40 minutes while improving "
            "reliability — the mechanism was exactly this: fewer races, better isolation, "
            "honest reporting."
        ),
        "followups": [
            "How do you decide a test is flaky versus intermittent product behaviour?",
            "What retry policy is defensible?",
            "How would you structure environment pre-flight checks?",
        ],
    },
    {
        "id": "scen-incomplete-deprovisioning",
        "title": "Incomplete account deprovisioning",
        "severity": "critical",
        "topic": "IGA / JML",
        "situation": "Deprovisioning disabled the main account but left a secondary service account and an API key active.",
        "interviewer_question": "How would you test completeness of deprovisioning across account types?",
        "key_points": [
            "Inventory every credential type: user account, service account, API keys, tokens, vault entries, group memberships.",
            "Each type must have a defined deprovisioning action.",
            "Verify per type in the target system, not just the primary account.",
            "API keys are the classic miss: long-lived, invisible in UI lists.",
            "CyberArk vault entries and active privileged sessions must be revoked.",
            "Shared/group memberships the user held must be cleaned or reassigned.",
            "A completeness checklist encoded as automated assertions.",
        ],
        "test_cases": [
            {"type": "negative", "title": "Service account remains after user termination", "expected": "Finding: deprovisioning must cover owned service accounts."},
            {"type": "negative", "title": "API key remains active", "expected": "Key revoked; calls with it return 401."},
            {"type": "boundary", "title": "User owned shared resources", "expected": "Ownership transferred or disabled per policy."},
        ],
        "api_checks": "Calls with old API keys and tokens post-deprovisioning must fail.",
        "db_checks": "All credential tables for the user: accounts, keys, memberships, vault references.",
        "job_checks": "Deprovisioning task list per credential type; reconciliation sweep finds leftovers.",
        "security_consideration": "Attackers prefer the forgotten credential types — service accounts and API keys — over the well-guarded main login.",
        "root_cause_paths": [
            "Deprovisioning workflow covers only the primary account object.",
            "Service account ownership not modelled in the platform.",
            "API keys managed outside the IAM scope.",
            "Vault entry cleanup step skipped on a connector error.",
        ],
        "strong_answer": (
            "I test deprovisioning against a credential inventory, not just 'the account': user "
            "login, service accounts the user owned, API keys, tokens, group memberships and "
            "vault entries. Each type gets an assertion in the target system — an actual API call "
            "with the old key must return 401. The recurring real-world miss is API keys because "
            "they are invisible in UI lists and managed outside the IAM scope, so I enumerate "
            "them directly from the database. My termination regression includes the full "
            "checklist, because partial deprovisioning is the failure mode nobody notices until "
            "an audit does."
        ),
        "followups": [
            "How do you discover credential types you don't know about?",
            "Who should own API key lifecycle in an IAM programme?",
            "How would you report deprovisioning completeness as a metric?",
        ],
    },
    {
        "id": "scen-wrong-user-correlation",
        "title": "Reconciliation correlates the wrong user",
        "severity": "critical",
        "topic": "Correlation",
        "situation": "Two employees share a surname and birthday. The nightly job merged their entitlements into one identity.",
        "interviewer_question": "How would you test correlation correctness and prevent wrong-user merges?",
        "key_points": [
            "Correlation rule strength: single weak field (surname) must never be sufficient.",
            "Multiple candidate matches must escalate, never auto-choose.",
            "Merge is destructive: test reversibility/audit evidence.",
            "Test data must include near-duplicate humans (same name, same DOB, adjacent IDs).",
            "Merge consequences: entitlements union vs intersection per policy.",
            "Alerting on merge actions for human review.",
            "Reconciliation dry-run mode compared to applied run.",
        ],
        "test_cases": [
            {"type": "negative", "title": "Two candidate matches", "expected": "No automatic merge; flagged for review."},
            {"type": "boundary", "title": "Same person re-appears with changed email", "expected": "Correlated correctly via employee ID."},
            {"type": "negative", "title": "Weak-field-only match", "expected": "Insufficient evidence; record queued, not merged."},
        ],
        "api_checks": "Correlation/merge API requires review confirmation for ambiguous cases.",
        "db_checks": "Merged identity audit trail; entitlement history of both sources preserved.",
        "job_checks": "Nightly job logs for correlation decisions; ambiguous-match queue.",
        "security_consideration": "A wrong merge grants one person another's access — a self-inflicted privilege escalation.",
        "root_cause_paths": [
            "Rule weighted on weak identifiers (name, DOB).",
            "Ambiguity not detected (first match wins).",
            "Email format change forced fallback to weak fields.",
            "Manual merge with insufficient review.",
        ],
        "strong_answer": (
            "Correlation errors are worse than duplicate identities: a duplicate is clutter, a "
            "wrong merge is access being granted to the wrong human. So I test the decision "
            "boundary: two people sharing weak identifiers must NOT match; a single strong "
            "identifier (employee ID) must match even when email changed; and any ambiguous "
            "case must escalate for human review instead of auto-resolving. My test data "
            "deliberately includes near-twins. And because merges are destructive, I verify "
            "the audit trail preserves both entitlement histories so a wrong merge can be "
            "investigated and reversed."
        ),
        "followups": [
            "What identifiers make a strong correlation key?",
            "How would you design a merge-undo capability?",
            "How do you monitor for wrong merges after they happen?",
        ],
    },
    {
        "id": "scen-grant-after-rejection",
        "title": "Access granted after request rejection",
        "severity": "critical",
        "topic": "Authorization",
        "situation": "A request for CIAM_SUPPORT was REJECTED. The entitlement appeared on the user's profile three days later.",
        "interviewer_question": "How would you test that a rejected request can never result in access?",
        "key_points": [
            "State machine: request statuses must be terminal-safe (REJECTED is final).",
            "Race conditions: rejection racing with approval/provisioning.",
            "Retry of a provisioning task created before rejection.",
            "Other grant paths: birthright rules, bulk import, direct API grants.",
            "Idempotency keys: a retried task must check current request state.",
            "SQL cross-check: rejected requests vs current entitlements — the standing regression query.",
        ],
        "test_cases": [
            {"type": "negative", "title": "Reject after provisioning task created", "expected": "Task cancelled or compensating revoke executes."},
            {"type": "negative", "title": "Retry a pre-rejection task", "expected": "Task revalidates request state; no grant."},
            {"type": "boundary", "title": "Simultaneous approve and reject calls", "expected": "Exactly one terminal state wins; outcome audited."},
        ],
        "api_checks": "Transition API attempts from REJECTED; concurrent decision calls.",
        "db_checks": "The rejected-but-granted query: REJECTED requests joined to current role assignments.",
        "job_checks": "Provisioning retry jobs that must revalidate request state before executing.",
        "security_consideration": "This is the unauthorized-access scenario in its purest form: the control said no and the system granted anyway.",
        "root_cause_paths": [
            "Provisioning task not cancelled on rejection.",
            "Retry re-executed stale task state.",
            "Another path (birthright, import) granted the same entitlement.",
            "Race between decision API calls.",
        ],
        "strong_answer": (
            "I treat request statuses as a state machine and REJECTED as terminal: no path may "
            "transition it back, and any in-flight provisioning task must be cancelled or "
            "compensated. I test the race explicitly — reject while the provisioning task is "
            "queued, retry a task created before rejection, and fire approve/reject "
            "concurrently. Then I hunt the alternate grant paths, because the entitlement "
            "arrived three days later, which smells like a birthright rule or bulk import "
            "rather than the request pipeline. My standing regression is the SQL cross-check: "
            "any REJECTED request joined to a live role assignment is a P1 finding."
        ),
        "followups": [
            "How do you design cancellation for in-flight provisioning tasks?",
            "Which grant paths exist outside the request workflow?",
            "How would you alert on this condition continuously?",
        ],
    },
    {
        "id": "scen-recon-creates-duplicates",
        "title": "Reconciliation creates duplicate accounts",
        "severity": "high",
        "topic": "Reconciliation",
        "situation": "After a reconciliation run, users who already had accounts gained a second account with a '-1' suffix.",
        "interviewer_question": "How would you test reconciliation to ensure it never duplicates existing accounts?",
        "key_points": [
            "Correlation-before-create: the job must correlate existing accounts first.",
            "Account-naming collision policies (suffixing can silently create duplicates).",
            "Idempotency: re-running reconciliation is always safe.",
            "Duplicate detection as an automated post-run assertion.",
            "Correlation attribute changes (user changed email mid-run).",
            "Log evidence: correlate vs create decisions per record.",
        ],
        "test_cases": [
            {"type": "boundary", "title": "Run reconciliation twice", "expected": "Second run correlates everything; zero creates."},
            {"type": "negative", "title": "Account exists with different naming", "expected": "Correlated via identity attributes, not suffixed duplicate."},
            {"type": "boundary", "title": "User changes email between runs", "expected": "Correlated via stable ID; no duplicate."},
        ],
        "api_checks": "Target app account search API used for correlation by the job.",
        "db_checks": "Duplicate account queries (same user, two accounts); suffix-pattern detection.",
        "job_checks": "Reconciliation decision logs; correlate/create counts per run.",
        "security_consideration": "Duplicate accounts mean one is governed and one is not — the ungoverned one is the attack path.",
        "root_cause_paths": [
            "Correlation query missed the existing account (different attribute).",
            "Auto-suffix naming policy created a 'new' account instead of escalating.",
            "Partial run then full run treated processed records as new.",
            "Concurrent reconciliation runs without locking.",
        ],
        "strong_answer": (
            "The invariant is simple: reconciliation may correlate or update, and create only "
            "when nothing exists — and creation must be proven safe by correlation first. I "
            "test the invariant by running reconciliation twice on the same data and asserting "
            "zero creates on the second run. The '-1 suffix' detail in this scenario points at "
            "a naming collision policy papering over a correlation miss: the system should have "
            "escalated the ambiguity instead of inventing a new account. I verify per-record "
            "correlate-vs-create decisions in logs, and my post-run assertion is a duplicate "
            "account query that must return zero rows."
        ),
        "followups": [
            "When is creating a new account ever correct during reconciliation?",
            "How would you fix data where duplicates already exist?",
            "How do you test correlation with changed attributes?",
        ],
    },
    {
        "id": "scen-manager-approval-misassigned",
        "title": "Manager approval assigned to the wrong reviewer",
        "severity": "high",
        "topic": "Workflows",
        "situation": "A high-risk access request was routed to a team lead instead of the department head per policy.",
        "interviewer_question": "How would you test approval routing rules?",
        "key_points": [
            "Routing rules matrix: entitlement risk x user department x requester role -> approver.",
            "Manager hierarchy data quality (the classic broken manager_id).",
            "Delegation and out-of-office routing.",
            "Escalation when the routed approver is unavailable or inactive.",
            "Thresholds: value/risk boundaries change the approver tier.",
            "Approval cannot be granted by the requester under any routing path.",
            "Routing changes are versioned and regression-tested.",
        ],
        "test_cases": [
            {"type": "positive", "title": "High-risk request routes to department head", "expected": "Correct tier per policy matrix."},
            {"type": "boundary", "title": "Exactly at risk threshold", "expected": "Documented tier (>= vs >) applies consistently."},
            {"type": "negative", "title": "Manager inactive/unavailable", "expected": "Escalates per policy, never auto-approves."},
            {"type": "negative", "title": "Self-approval under any routing", "expected": "Impossible; logged."},
        ],
        "api_checks": "Routing decision API: given request attributes, returns expected approver.",
        "db_checks": "Manager hierarchy integrity (no broken manager_id, no cycles).",
        "job_checks": "Escalation timer jobs; delegation expiry.",
        "security_consideration": "Wrong-tier approvals dilute control strength while still looking compliant in audit records.",
        "root_cause_paths": [
            "Routing rule priority misconfigured (generic rule outranked specific one).",
            "Stale or broken manager hierarchy data.",
            "Delegation rule without expiry.",
            "Risk classification of the entitlement wrong.",
        ],
        "strong_answer": (
            "Approval routing is a rules engine, so I build the matrix — entitlement risk, "
            "department, thresholds — and test every cell plus the boundaries between tiers, "
            "because the >= vs > at a threshold is exactly where routing bugs live. Then the "
            "operational cases: approver inactive, delegation, escalation timers. And the "
            "invariant under all paths: the requester can never end up as their own approver. "
            "Underneath it all sits data quality — routing through a broken manager_id "
            "reference silently misroutes, so hierarchy integrity is part of my test suite."
        ),
        "followups": [
            "How do you test rule priority conflicts?",
            "What delegation expiry policy would you recommend?",
            "How would you detect misrouting in production?",
        ],
    },
    {
        "id": "scen-sso-logout-incomplete",
        "title": "SSO logout does not terminate downstream sessions",
        "severity": "high",
        "topic": "SSO",
        "situation": "After portal logout, pressing back restores an authenticated CRM tab.",
        "interviewer_question": "How would you test SSO logout across an application portfolio?",
        "key_points": [
            "IdP logout vs SP logout vs front-channel vs back-channel logout.",
            "Every SP must invalidate its session on logout notification.",
            "Browser back button must not resurrect an authenticated page (cache headers).",
            "Tokens issued before logout must stop working.",
            "Idle and absolute session timeouts per policy still apply.",
            "Logout with multiple open tabs and multiple applications.",
            "Test both SP-initiated and IdP-initiated logout.",
        ],
        "test_cases": [
            {"type": "negative", "title": "Back button after logout", "expected": "Cached authenticated page not served; redirect to login."},
            {"type": "negative", "title": "Other SP session after IdP logout", "expected": "All SP sessions terminated (back-channel)."},
            {"type": "boundary", "title": "Token issued one second before logout", "expected": "Rejected after logout per policy."},
        ],
        "api_checks": "Pre-logout tokens on APIs must fail; logout endpoints on IdP and each SP.",
        "db_checks": "Session store entries removed per SP.",
        "job_checks": "Session reaper jobs; SLO message delivery.",
        "security_consideration": "Shared machines (kiosks, hospitals, trading floors) make incomplete logout a genuine account-takeover vector.",
        "root_cause_paths": [
            "Only IdP session cleared; SP sessions untouched.",
            "Back-channel logout not implemented per SP.",
            "Cache headers allow authenticated page restore.",
            "Tokens stateless with no deny-list.",
        ],
        "strong_answer": (
            "Logout is the most commonly under-tested SSO feature, so I treat it as its own "
            "suite. For each application I verify: IdP-initiated and SP-initiated logout both "
            "work; back-channel logout reaches every SP and kills its session; the browser back "
            "button cannot restore an authenticated page (cache-control headers); and tokens "
            "issued before logout are rejected afterwards. I test with multiple tabs and "
            "multiple apps open because that is the real usage pattern. Incomplete logout on a "
            "shared machine is effectively an account takeover — that framing makes the defect "
            "priority obvious."
        ),
        "followups": [
            "What are front-channel vs back-channel logout?",
            "How do you handle SPs that cannot receive logout notifications?",
            "How would you automate logout testing across 30 apps?",
        ],
    },
    {
        "id": "scen-api-pagination-misses",
        "title": "API pagination misses users",
        "severity": "high",
        "topic": "API testing",
        "situation": "The users API returns 100 per page. A tester's script only ever saw 950 of 1,050 users; the reconciliation built on it silently under-imported.",
        "interviewer_question": "How would you test pagination correctness on an API?",
        "key_points": [
            "Page boundaries: exact multiples (100, 200), off-by-one at page edges.",
            "Empty page vs end-of-data signalling (cursor vs offset semantics).",
            "Items created/deleted during pagination.",
            "Stable ordering: does page content shift between calls?",
            "Total count consistency vs paged fetch count.",
            "Cursor expiry and invalid cursor handling.",
            "Rate limiting across paged calls.",
        ],
        "test_cases": [
            {"type": "boundary", "title": "Exactly 100, 200, 1000 records", "expected": "Page counts and totals correct at multiples."},
            {"type": "negative", "title": "Record deleted mid-pagination", "expected": "Documented semantics: skip or duplicate-free iteration."},
            {"type": "negative", "title": "Invalid/expired cursor", "expected": "Explicit error, not silently empty page."},
            {"type": "positive", "title": "Paged sum equals total", "expected": "Sum of items across pages == total count reported."},
        ],
        "api_checks": "Page size limits, next-cursor semantics, 429 handling, ordering guarantees.",
        "db_checks": "Total record count vs sum fetched across pages.",
        "job_checks": "Consumers of the API: import jobs handle page edges identically.",
        "security_consideration": "Under-imported users escape governance: never certified, never deprovisioned — invisible identities.",
        "root_cause_paths": [
            "Off-by-one on the last partial page.",
            "Loop stops on first empty page that is actually rate-limit noise.",
            "Cursor semantics misunderstood by the consumer.",
            "Unstable ordering causing skipped/duplicated items.",
        ],
        "strong_answer": (
            "I test the boundaries mathematically: page sizes of exactly 100, 200 and 1000 "
            "records, then 950 and 1,050 to force partial pages, and I assert that the sum of "
            "items across pages equals the reported total — that single invariant catches most "
            "pagination bugs. Then the dynamics: a record deleted mid-pagination, cursor expiry, "
            "and rate limiting masquerading as empty pages. The security angle is what makes "
            "this scenario matter: users skipped by pagination escape governance entirely — "
            "never certified, never deprovisioned — so the reconciliation consumer needs the "
            "count-based assertion as much as the API does."
        ),
        "followups": [
            "Cursor vs offset pagination — what breaks in each?",
            "How would you test pagination under concurrent writes?",
            "How do you verify ordering stability?",
        ],
    },
    {
        "id": "scen-integration-retry-duplicates",
        "title": "Integration retries duplicate transactions",
        "severity": "high",
        "topic": "Integration",
        "situation": "A connector timed out on an account-disable call, retried, and the target application logged two disable events and a duplicate role-revoke side effect.",
        "interviewer_question": "How would you test that integration retries do not duplicate side effects?",
        "key_points": [
            "Idempotency keys on every mutating operation.",
            "Duplicate detection on the target side.",
            "Timeout handling: retry only after confirming non-completion.",
            "Exactly-once vs at-least-once delivery semantics — know which the design uses.",
            "Compensation when duplicate side effects already occurred.",
            "Ordering guarantees between retries and concurrent operations.",
            "Log correlation across retries (same logical operation ID).",
        ],
        "test_cases": [
            {"type": "negative", "title": "Timeout then retry on disable", "expected": "Exactly one disable effect; duplicate detected by idempotency key."},
            {"type": "boundary", "title": "Retry arrives while original in flight", "expected": "Serialised or deduplicated; no interleave."},
            {"type": "negative", "title": "Target already processed the operation", "expected": "Second attempt is a no-op returning success."},
        ],
        "api_checks": "Retry semantics of the connector; idempotency key propagation.",
        "db_checks": "Duplicate side-effect rows; operation log correlation IDs.",
        "job_checks": "Retry scheduler: backoff, max attempts, dead-lettering.",
        "security_consideration": "Duplicated revokes are annoying; duplicated GRANTS are security incidents.",
        "root_cause_paths": [
            "No idempotency key on mutating calls.",
            "Retry fired while the original request was still in flight.",
            "Timeout interpreted as failure when the operation succeeded.",
            "Target lacks duplicate detection.",
        ],
        "strong_answer": (
            "Retries are safe only with idempotency, so I test for it directly: force a timeout, "
            "let the retry fire, and assert the final state equals a single execution — no "
            "duplicate rows, no duplicated notifications. The subtle case is the timeout where "
            "the operation actually succeeded: the retry must be recognised as a no-op, which "
            "requires an idempotency key or operation ID the target can dedupe on. I also test "
            "the in-flight overlap, where the retry arrives before the original finishes. And I "
            "distinguish severity: duplicated revokes are hygiene, duplicated grants are "
            "security incidents — the test priority follows that."
        ),
        "followups": [
            "How would you design an idempotency key scheme?",
            "At-least-once vs exactly-once: what does your platform actually need?",
            "How do you clean up duplicates already created?",
        ],
    },
    {
        "id": "scen-production-defect-after-release",
        "title": "Production defect after release",
        "severity": "high",
        "topic": "Process / Root cause",
        "situation": "Two days after release, terminated users were still visible in an entitlement export used by a downstream security tool.",
        "interviewer_question": "A defect escaped to production. Walk me through your investigation, the fix validation, and the prevention you add.",
        "key_points": [
            "Containment first: quantify scope (how many users, which exports, what downstream effect).",
            "Reproduce in a lower environment with production-like data shape.",
            "Root cause: code, config, data or environment — with evidence, not guesses.",
            "Fix validation: regression test that fails before the fix and passes after.",
            "Gap analysis: why did existing suites miss it? Which layer was untested?",
            "Add the missing assertion permanently; review similar paths for the same class of bug.",
            "Communication: clear timeline and impact for stakeholders.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Regression test for the defect", "expected": "Fails on pre-fix build, passes post-fix — the proof it guards the fix."},
            {"type": "negative", "title": "Defect not reproducible in lower environment", "expected": "Escalate with production-shaped data request; never mark it non-reproducible and drop it."},
            {"type": "boundary", "title": "Same defect class on adjacent exports", "expected": "Checked and covered; not assumed fine."},
        ],
        "api_checks": "Reproduce the export API behaviour with a terminated user in a test environment.",
        "db_checks": "Which records were affected; the SQL that quantifies scope for stakeholders.",
        "job_checks": "The export job change history and its filters.",
        "security_consideration": "Security-relevant defects need scope quantification for potential breach assessment and reporting decisions.",
        "root_cause_paths": [
            "Export query joined on the wrong status field.",
            "New status value (TERMINATED_PENDING) not covered by the filter.",
            "The defect shipped in an untested code path (nightly job, not UI/API).",
            "Environment-specific data shape not represented in test data.",
        ],
        "strong_answer": (
            "I start with containment and quantification: a SQL query that names exactly which "
            "terminated users leaked into the export and which downstream consumers received "
            "it — stakeholders need numbers, not adjectives. Then reproduction in a lower "
            "environment with production-shaped data, root cause with evidence, and a fix "
            "validation that is a real regression test: red before the fix, green after. The "
            "part I insist on is the gap analysis: why did my suites miss it — usually an "
            "untested scheduled-job path — and then closing that gap so the class of defect is "
            "covered, not just the instance. I also sweep adjacent exports for the same pattern, "
            "because the same join bug rarely lives in exactly one query."
        ),
        "followups": [
            "How do you decide severity and whether it is reportable?",
            "What do you do when root cause is ambiguous?",
            "How do you prioritise which test gaps to close first?",
        ],
    },
    {
        "id": "scen-certification-dashboard-mismatch",
        "title": "Certification dashboard count mismatch",
        "severity": "medium",
        "topic": "Reporting / SQL validation",
        "situation": "The campaign dashboard reports 87% completion. Direct database queries of decisions show 79%.",
        "interviewer_question": "How would you test and resolve a certification dashboard statistics mismatch?",
        "key_points": [
            "Reproduce the exact denominator and numerator definitions from documentation.",
            "Identify computation location: live query, cached aggregate, or scheduled snapshot.",
            "Time-of-check skew between dashboard refresh and database state.",
            "Edge populations: revoked users, delegated items, bulk decisions, in-flight items.",
            "Three-way validation: UI number == API number == SQL number.",
            "Automated reconciliation of the campaign stats after every campaign in the suite.",
        ],
        "test_cases": [
            {"type": "positive", "title": "Definition-matched SQL equals dashboard", "expected": "Numbers reconcile when filters/definitions align."},
            {"type": "boundary", "title": "Decide a bulk action mid-refresh", "expected": "Final numbers converge after the refresh window."},
            {"type": "negative", "title": "Persistent mismatch beyond staleness window", "expected": "Defect filed with reproducible filter definition."},
        ],
        "api_checks": "Statistics endpoint payload vs dashboard rendering (transformation bugs).",
        "db_checks": "The ground truth query with the dashboard's documented definitions.",
        "job_checks": "Snapshot/refresh job schedule and success; queue backlog.",
        "security_consideration": "Auditors rely on campaign statistics; wrong numbers undermine the compliance evidence the campaign exists to produce.",
        "root_cause_paths": [
            "Numerator/denominator definitions differ (delegated vs pending).",
            "Cached snapshot stale after a late bulk decision.",
            "Timezone boundary in the campaign window filter.",
            "API aggregation differs from the UI's rendering of it.",
        ],
        "strong_answer": (
            "I make the comparison definition-fair first: pull the documented formulas for "
            "numerator and denominator, replicate them in SQL, and compare. Half of these "
            "mismatches are definition differences — delegated items counted as done in one "
            "layer and pending in another — not calculation bugs. Then I find where the number "
            "lives: live query, cached snapshot or materialised table, and whether the refresh "
            "window explains the gap. If the mismatch persists beyond the documented staleness "
            "SLA, it is a defect with a precise reproduction. And I leave behind automation: "
            "the three-way check — UI, API, SQL — for campaign statistics, which is exactly the "
            "dashboard validation I did against SQL in my current role."
        ),
        "followups": [
            "How would you encode 'definition fairness' in an automated check?",
            "What staleness SLA would you negotiate for campaign stats?",
            "How do bulk decisions typically break these calculations?",
        ],
    },
]


def list_scenarios() -> list[dict]:
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "severity": s["severity"],
            "topic": s["topic"],
            "situation": s["situation"],
            "interviewer_question": s["interviewer_question"],
        }
        for s in SCENARIOS
    ]


def get_scenario(scenario_id: str) -> dict | None:
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    return None
