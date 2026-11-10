"""SQL interview challenges on the IAM dataset. Graded by comparing result sets."""
from __future__ import annotations

SQL_CHALLENGES = [
    {
        "id": "sql-inactive-users-with-roles",
        "title": "Inactive users who still hold roles",
        "difficulty": "easy",
        "category": "JOIN",
        "problem": "Find every user whose status is not ACTIVE but who still has at least one role assignment. Return username, status and role_name.",
        "hints": ["Join USERS to USER_ROLES to ROLES.", "status != 'ACTIVE' catches both INACTIVE and TERMINATED.", "This is a security finding, not just a query result."],
        "expected_sql": (
            "SELECT u.username, u.status, r.role_name FROM USERS u "
            "JOIN USER_ROLES ur ON u.user_id = ur.user_id "
            "JOIN ROLES r ON ur.role_id = r.role_id "
            "WHERE u.status <> 'ACTIVE' ORDER BY u.username, r.role_name"
        ),
        "explanation": (
            "Every row returned is an access-control violation: an inactive or terminated identity "
            "that can still authenticate and act. In a Schwab-style answer you connect this to the "
            "deprovisioning workflow: this query is exactly what your automated JML regression must "
            "run after a termination event."
        ),
        "security_note": "Terminated/INACTIVE users with live role assignments are the single most common audit finding in IGA platforms.",
        "followups": ["How would you automate this check after every termination test?", "What if status has more values than ACTIVE/INACTIVE/TERMINATED?"],
    },
    {
        "id": "sql-admin-privileges",
        "title": "Users with administrative privileges",
        "difficulty": "easy",
        "category": "Filtering",
        "problem": "List the usernames of all users holding a role with privilege_level >= 10. Include duplicates only if a user holds several such roles; return username and role_name.",
        "hints": ["privilege_level >= 10 marks administrative roles.", "The join order does not matter for correctness."],
        "expected_sql": (
            "SELECT u.username, r.role_name FROM USERS u "
            "JOIN USER_ROLES ur ON u.user_id = ur.user_id "
            "JOIN ROLES r ON ur.role_id = r.role_id "
            "WHERE r.privilege_level >= 10 ORDER BY u.username, r.role_name"
        ),
        "explanation": (
            "Admin-privilege inventory is the first query every auditor asks for. Pair it with the "
            "approval trail: in an interview, immediately mention you would cross-check ACCESS_REQUESTS "
            "to see whether each grant has a matching APPROVED request — unapproved admin access is a finding."
        ),
        "security_note": "Least privilege review: every admin grant should trace back to an approved access request.",
        "followups": ["How would you check whether each admin role has an APPROVED request behind it?", "Which index would speed this query on a large USERS table?"],
    },
    {
        "id": "sql-duplicate-usernames",
        "title": "Find duplicate usernames",
        "difficulty": "easy",
        "category": "GROUP BY",
        "problem": "Find usernames that appear more than once in USERS. Return username and the number of occurrences.",
        "hints": ["GROUP BY username, then filter groups with HAVING COUNT(*) > 1.", "WHERE cannot filter aggregates; HAVING can."],
        "expected_sql": (
            "SELECT username, COUNT(*) AS cnt FROM USERS GROUP BY username HAVING COUNT(*) > 1 ORDER BY username"
        ),
        "explanation": (
            "Duplicate identities break correlation rules and cause double provisioning — the classic "
            "reconciliation defect. Also mention alternate duplicate detection: same email, or same "
            "name with different IDs (fuzzy matching is where IGA platforms earn their money)."
        ),
        "security_note": "Duplicate identities often mean duplicate entitlements and double the attack surface.",
        "followups": ["How would you find duplicates by email instead?", "How would you detect probable duplicates when IDs differ but names are similar?"],
    },
    {
        "id": "sql-stale-pending-requests",
        "title": "Pending access requests older than 7 days",
        "difficulty": "easy",
        "category": "Filtering",
        "problem": "Find PENDING access requests created more than 7 days before '2025-11-10'. Return request_id, username and entitlement.",
        "hints": ["The reference date is '2025-11-10' (seeded 'today').", "Date arithmetic: created_at < '2025-11-10' minus 7 days.", "Join USERS for the username."],
        "expected_sql": (
            "SELECT ar.request_id, u.username, ar.entitlement FROM ACCESS_REQUESTS ar "
            "JOIN USERS u ON ar.user_id = u.user_id "
            "WHERE ar.status = 'PENDING' AND ar.created_at < date('2025-11-10', '-7 day') "
            "ORDER BY ar.request_id"
        ),
        "explanation": (
            "SLA monitoring for access requests: a request pending beyond policy is a governance gap, "
            "and in regulated environments it can be a compliance finding. The date arithmetic differs "
            "per engine (DATEADD in SQL Server, INTERVAL in Oracle/Postgres) — name your dialect."
        ),
        "security_note": "Stuck approvals leave users either blocked (availability) or over-granted via workarounds (risk).",
        "followups": ["How would you compute '7 days before today' without hardcoding the date?", "How do you test this rule across DB engines?"],
    },
    {
        "id": "sql-users-without-roles",
        "title": "Users without any assigned role",
        "difficulty": "easy",
        "category": "JOIN",
        "problem": "List users who have no role assignment at all. Return username and status.",
        "hints": ["LEFT JOIN USER_ROLES and keep rows where the join key IS NULL.", "NOT EXISTS is the alternative that many interviewers prefer."],
        "expected_sql": (
            "SELECT u.username, u.status FROM USERS u "
            "LEFT JOIN USER_ROLES ur ON u.user_id = ur.user_id "
            "WHERE ur.user_id IS NULL ORDER BY u.username"
        ),
        "explanation": (
            "LEFT JOIN + IS NULL vs NOT EXISTS: both are correct; NOT EXISTS often performs better "
            "and is safer under NULL semantics and duplicates. A user with no roles may be "
            "under-provisioned (cannot work) or a cleanup candidate (should the account exist at all?)."
        ),
        "security_note": "Orphan accounts with no roles are also worth investigating: why do they exist?",
        "followups": ["Rewrite it with NOT EXISTS — which do you prefer and why?", "How would you find users with roles but no account in a target application?"],
    },
    {
        "id": "sql-terminated-with-accounts",
        "title": "Terminated users with live application accounts",
        "difficulty": "medium",
        "category": "JOIN",
        "problem": "Find TERMINATED users who still show a provisioning log entry for account creation or privileged access grant (status SUCCESS) after termination, or any FAILED disable/revoke. Return username, application_name and operation.",
        "hints": ["PROVISIONING_LOGS holds per-application operations.", "You want evidence that deprovisioning did not complete.", "Terminated users should show DISABLE/REVOKE SUCCESS — anything else is a finding."],
        "expected_sql": (
            "SELECT u.username, p.application_name, p.operation FROM USERS u "
            "JOIN PROVISIONING_LOGS p ON u.user_id = p.user_id "
            "WHERE u.status = 'TERMINATED' "
            "AND (p.status = 'FAILED' OR p.operation LIKE '%CREATE%' OR p.operation LIKE '%GRANT%') "
            "ORDER BY u.username, p.application_name"
        ),
        "explanation": (
            "This is the core evidence query for a termination audit: the identity is TERMINATED but "
            "the target-system operations tell the truth. FAILED disable/revoke entries are direct "
            "deprovisioning defects; CREATE/GRANT successes after termination are worse — they mean "
            "provisioning ran when it should never have run."
        ),
        "security_note": "The IGA dashboard may say 'terminated' while downstream accounts live on — always validate the target systems.",
        "followups": ["How would you prove the timeline (operation after termination date)?", "What reconciliation job would fix this, and how would you test it?"],
    },
    {
        "id": "sql-failed-provisioning",
        "title": "Failed provisioning operations by application",
        "difficulty": "easy",
        "category": "Aggregation",
        "problem": "Count FAILED provisioning operations per application_name. Return application_name and the failure count, sorted by count descending.",
        "hints": ["GROUP BY application_name.", "Filter with WHERE status = 'FAILED' before grouping.", "Sort by the count descending."],
        "expected_sql": (
            "SELECT application_name, COUNT(*) AS failures FROM PROVISIONING_LOGS "
            "WHERE status = 'FAILED' GROUP BY application_name ORDER BY failures DESC, application_name"
        ),
        "explanation": (
            "Connector health view: which integration is failing most? In a real platform you would "
            "also compute a failure RATE (failures / total per app) — a 3/10 failure rate is worse "
            "than 3/10000, and COUNT alone hides that."
        ),
        "security_note": "Failing deprovisioning operations mean access removal silently did not happen.",
        "followups": ["How would you compute the failure RATE per application?", "How would you alert on a spike in failures for one connector?"],
    },
    {
        "id": "sql-multiple-privileged-roles",
        "title": "Users holding more than one privileged role",
        "difficulty": "medium",
        "category": "HAVING",
        "problem": "Find users who hold two or more roles with privilege_level >= 5. Return username and the number of such roles.",
        "hints": ["Filter rows to privileged roles first, then group.", "HAVING COUNT(*) >= 2.", "privilege_level >= 5 defines privileged here."],
        "expected_sql": (
            "SELECT u.username, COUNT(*) AS privileged_roles FROM USERS u "
            "JOIN USER_ROLES ur ON u.user_id = ur.user_id "
            "JOIN ROLES r ON ur.role_id = r.role_id "
            "WHERE r.privilege_level >= 5 "
            "GROUP BY u.username HAVING COUNT(*) >= 2 ORDER BY u.username"
        ),
        "explanation": (
            "Privilege accumulation is a classic IGA risk: two privileged roles can combine into "
            "unintended capabilities (separation of duties). The WHERE-before-GROUP discipline is the "
            "technical point: filtering rows early keeps the aggregate honest."
        ),
        "security_note": "Separation-of-duties conflicts often hide inside combinations of individually-approved roles.",
        "followups": ["How would you detect specific SoD-violating role PAIRS rather than any two privileged roles?", "Why filter in WHERE instead of HAVING here?"],
    },
    {
        "id": "sql-certification-revocation-not-applied",
        "title": "Revoked certifications where access still exists",
        "difficulty": "medium",
        "category": "JOIN",
        "problem": "Find certifications with decision 'REVOKE' where the user STILL holds the corresponding role (role_name equals the entitlement). Return username, entitlement and role_name.",
        "hints": ["Join CERTIFICATIONS to USERS and then to USER_ROLES/ROLES.", "A REVOKE decision should mean the role assignment is gone.", "Correlate entitlement text with role_name."],
        "expected_sql": (
            "SELECT u.username, c.entitlement, r.role_name FROM CERTIFICATIONS c "
            "JOIN USERS u ON c.user_id = u.user_id "
            "JOIN USER_ROLES ur ON ur.user_id = c.user_id "
            "JOIN ROLES r ON r.role_id = ur.role_id "
            "WHERE c.decision = 'REVOKE' AND r.role_name = c.entitlement "
            "ORDER BY u.username, c.entitlement"
        ),
        "explanation": (
            "This is the exact query behind the classic interview scenario: 'the manager revoked "
            "access in the campaign, but the user still has it.' The gap means the revocation "
            "workflow, the provisioning connector or the reconciliation job failed — and your test "
            "must run this query after the campaign completes."
        ),
        "security_note": "Certification decisions are compliance evidence; unenforced revocations invalidate the whole campaign.",
        "followups": ["Which system component would you investigate first for this mismatch?", "How would you test the full revocation path end-to-end?"],
    },
    {
        "id": "sql-count-by-department",
        "title": "User count by department",
        "difficulty": "easy",
        "category": "GROUP BY",
        "problem": "Count users per department, including departments with a single user. Return department and user count, ordered by count descending then department.",
        "hints": ["Plain GROUP BY on department.", "Order by count desc, then department for ties."],
        "expected_sql": (
            "SELECT department, COUNT(*) AS users FROM USERS GROUP BY department "
            "ORDER BY users DESC, department"
        ),
        "explanation": (
            "Baseline query, but connect it to dashboard validation: the IAM analytics dashboard shows "
            "'users by department' — your automation compares the API/UI number against this SQL "
            "result. That database-vs-dashboard reconciliation is exactly the kind of validation "
            "employers want to hear about."
        ),
        "security_note": "Dashboard numbers must match the database — stale dashboards hide orphaned access.",
        "followups": ["How would you validate this against a dashboard widget in automation?", "What does a count mismatch between UI and SQL tell you?"],
    },
    {
        "id": "sql-users-by-role-count",
        "title": "Roles per user, top holders first",
        "difficulty": "easy",
        "category": "Aggregation",
        "problem": "For every user with at least one role, return username and role_count, sorted by role_count descending then username.",
        "hints": ["GROUP BY user after joining.", "COUNT(DISTINCT ur.id) or COUNT(*) — decide which is safer.", "DESC ordering with a username tiebreaker."],
        "expected_sql": (
            "SELECT u.username, COUNT(*) AS role_count FROM USERS u "
            "JOIN USER_ROLES ur ON u.user_id = ur.user_id "
            "GROUP BY u.username ORDER BY role_count DESC, u.username"
        ),
        "explanation": (
            "Entitlement volume per identity — a top-N attack-surface view. Mention COUNT(*) vs "
            "COUNT(DISTINCT role_id): if the same role could be assigned twice to one user (a data "
            "defect), COUNT(*) would overstate access while DISTINCT would hide the duplicate. "
            "A tester should flag the duplicate assignment itself."
        ),
        "security_note": "Role inflation per user is an early warning for privilege creep.",
        "followups": ["COUNT(*) vs COUNT(DISTINCT role_id) — what changes if duplicates exist?", "How would you write the equivalent top-N with LIMIT?"],
    },
    {
        "id": "sql-pending-by-status",
        "title": "Access request pipeline by status",
        "difficulty": "easy",
        "category": "GROUP BY",
        "problem": "For each request status, count requests and list how many distinct users are waiting or processed. Return status, request count and distinct user count.",
        "hints": ["COUNT(*) plus COUNT(DISTINCT user_id).", "GROUP BY status."],
        "expected_sql": (
            "SELECT status, COUNT(*) AS requests, COUNT(DISTINCT user_id) AS users "
            "FROM ACCESS_REQUESTS GROUP BY status ORDER BY status"
        ),
        "explanation": (
            "The difference between COUNT(*) and COUNT(DISTINCT user_id) tells you whether users "
            "submit multiple requests — request storms are a real pattern in access-request UIs "
            "when feedback is slow. Two aggregates in one query is a common interview probe."
        ),
        "security_note": "Duplicate submissions can duplicate grants if the request pipeline is not idempotent.",
        "followups": ["How would you detect duplicate submissions for the same user+entitlement?", "What does a REJECTED request that still granted access look like in this data?"],
    },
    {
        "id": "sql-rejected-but-granted",
        "title": "Requests rejected but access granted anyway",
        "difficulty": "medium",
        "category": "Correlation",
        "problem": "Find users who have a REJECTED request for an entitlement but still hold the matching role (role_name = entitlement). Return username and entitlement.",
        "hints": ["Two sources: ACCESS_REQUESTS with status REJECTED, and current USER_ROLES.", "EXISTS or a join between them on user + entitlement = role_name."],
        "expected_sql": (
            "SELECT DISTINCT u.username, ar.entitlement FROM USERS u "
            "JOIN ACCESS_REQUESTS ar ON ar.user_id = u.user_id "
            "JOIN USER_ROLES ur ON ur.user_id = u.user_id "
            "JOIN ROLES r ON r.role_id = ur.role_id "
            "WHERE ar.status = 'REJECTED' AND r.role_name = ar.entitlement "
            "ORDER BY u.username, ar.entitlement"
        ),
        "explanation": (
            "The unauthorized-admin-access scenario in one query: a request was denied, yet the "
            "entitlement exists. Possible causes: a parallel approval path, a provisioning job "
            "that ran before the rejection, or a direct grant bypassing the workflow. Any row here "
            "is a P1 security defect — say that out loud."
        ),
        "security_note": "This is privilege escalation evidence: denial of a request must guarantee denial of access.",
        "followups": ["How would you determine WHEN the role was assigned relative to the rejection?", "What logs would you pull to find the granting path?"],
    },
    {
        "id": "sql-orphaned-assignments",
        "title": "Orphaned role assignments",
        "difficulty": "medium",
        "category": "Data integrity",
        "problem": "Find USER_ROLES rows whose role_id does not exist in ROLES. Return id, user_id and role_id.",
        "hints": ["LEFT JOIN ROLES and keep NULL matches.", "Alternative: WHERE role_id NOT IN (SELECT role_id FROM ROLES) — but beware NULLs."],
        "expected_sql": (
            "SELECT ur.id, ur.user_id, ur.role_id FROM USER_ROLES ur "
            "LEFT JOIN ROLES r ON ur.role_id = r.role_id "
            "WHERE r.role_id IS NULL ORDER BY ur.id"
        ),
        "explanation": (
            "Referential integrity validation — the same class of check you run after a database "
            "migration: counts, orphans, duplicates, constraints. NOT IN breaks silently if the "
            "subquery returns a NULL; NOT EXISTS is NULL-safe. Interviewers reward knowing that trap."
        ),
        "security_note": "Orphaned entitlements are invisible to governance: they appear in no campaign and no role model.",
        "followups": ["Why can NOT IN give wrong results with NULLs?", "How would you validate orphan counts before and after a data migration?"],
    },
    {
        "id": "sql-terminated-unprovisioned",
        "title": "Terminated users with no disable attempts at all",
        "difficulty": "medium",
        "category": "NOT EXISTS",
        "problem": "Find TERMINATED users for whom no DISABLE_ACCOUNT operation exists in PROVISIONING_LOGS (neither success nor failure). Return username.",
        "hints": ["NOT EXISTS against PROVISIONING_LOGS for that user.", "The absence of an attempt is worse than a failed attempt."],
        "expected_sql": (
            "SELECT u.username FROM USERS u "
            "WHERE u.status = 'TERMINATED' "
            "AND NOT EXISTS (SELECT 1 FROM PROVISIONING_LOGS p WHERE p.user_id = u.user_id AND p.operation = 'DISABLE_ACCOUNT') "
            "ORDER BY u.username"
        ),
        "explanation": (
            "A FAILED disable at least proves the workflow tried; a MISSING disable means the "
            "termination event never reached the connector — an event-driven integration defect. "
            "Your JML regression suite should assert both: attempts exist AND all succeeded."
        ),
        "security_note": "Missing deprovisioning attempts indicate the HR termination event was never processed.",
        "followups": ["How would you distinguish 'never attempted' from 'attempt failed' in your test assertions?", "Which integration log would you check first?"],
    },
    {
        "id": "sql-managers-with-reports",
        "title": "Managers and their report counts",
        "difficulty": "medium",
        "category": "Self join",
        "problem": "For every manager (user who appears as manager_id), return the manager's username and how many direct reports they have. Sort by report count descending.",
        "hints": ["Self join: USERS employee JOIN USERS manager.", "GROUP BY the manager.", "COUNT(*) counts reports."],
        "expected_sql": (
            "SELECT m.username AS manager, COUNT(*) AS reports FROM USERS e "
            "JOIN USERS m ON e.manager_id = m.user_id "
            "GROUP BY m.username ORDER BY reports DESC, manager"
        ),
        "explanation": (
            "Self joins model hierarchies: managers are exactly who access-certification campaigns "
            "assign as reviewers. A manager with zero reports cannot certify anything; a manager "
            "with fifty is your overdue-certification risk. Connect this query to campaign design."
        ),
        "security_note": "Certification campaigns depend on the manager hierarchy being correct and non-empty.",
        "followups": ["How would you find users whose manager_id references a nonexistent user?", "How would you build a full management chain (recursive CTE)?"],
    },
    {
        "id": "sql-broken-manager-refs",
        "title": "Users pointing to non-existent managers",
        "difficulty": "medium",
        "category": "Data integrity",
        "problem": "Find users whose manager_id is set but does not match any user_id in USERS. Return username and manager_id.",
        "hints": ["LEFT JOIN USERS manager ON e.manager_id = m.user_id.", "Keep rows where m.user_id IS NULL.", "manager_id IS NULL itself is legal (top of hierarchy)."],
        "expected_sql": (
            "SELECT e.username, e.manager_id FROM USERS e "
            "LEFT JOIN USERS m ON e.manager_id = m.user_id "
            "WHERE e.manager_id IS NOT NULL AND m.user_id IS NULL ORDER BY e.username"
        ),
        "explanation": (
            "Broken manager references mean certification campaigns route to nobody — reviews get "
            "lost and access silently persists. In interview terms: the identity data quality "
            "directly undermines the governance control built on top of it."
        ),
        "security_note": "Unroutable reviews default to inaction, which is how revoked access survives.",
        "followups": ["How would you test that a campaign assigns every user a valid reviewer?", "How does this relate to user correlation failures during reconciliation?"],
    },
    {
        "id": "sql-overdue-certifications",
        "title": "Overdue certifications without a decision",
        "difficulty": "easy",
        "category": "Filtering",
        "problem": "Find certification rows where the decision is NULL. Return username and entitlement.",
        "hints": ["decision IS NULL.", "Join USERS for username."],
        "expected_sql": (
            "SELECT u.username, c.entitlement FROM CERTIFICATIONS c "
            "JOIN USERS u ON c.user_id = u.user_id "
            "WHERE c.decision IS NULL ORDER BY u.username, c.entitlement"
        ),
        "explanation": (
            "Overdue reviews. A NULL decision is different from an empty string — NULL means the "
            "reviewer never acted, while '' could mean a UI default or a data load defect. "
            "Campaign SLAs escalate these; your automation should report them before the campaign "
            "auto-completes with a default decision."
        ),
        "security_note": "Undecided certifications block campaign completion and delay revocations.",
        "followups": ["What does your platform do with overdue items — auto-revoke, auto-confirm, or escalate?", "How would you test each of those policies?"],
    },
    {
        "id": "sql-recent-provisioning-volume",
        "title": "Provisioning volume in the last 30 days",
        "difficulty": "medium",
        "category": "Date logic",
        "problem": "Count provisioning operations per application with execution_time on or after '2025-10-11'. Return application_name and operation count, ordered by count descending.",
        "hints": ["execution_time is TEXT in ISO format — compare lexically with >=.", "GROUP BY application_name."],
        "expected_sql": (
            "SELECT application_name, COUNT(*) AS ops FROM PROVISIONING_LOGS "
            "WHERE execution_time >= '2025-10-11' "
            "GROUP BY application_name ORDER BY ops DESC, application_name"
        ),
        "explanation": (
            "Volume trending per connector — the baseline for performance and load testing of "
            "scheduled jobs. ISO-8601 text dates sort lexically in SQLite; in Oracle/Postgres you "
            "would cast or use a real date type. Knowing why the lexical comparison works here is "
            "the actual interview point."
        ),
        "security_note": "Unusual provisioning volume spikes can indicate bulk changes that need review.",
        "followups": ["Why does a lexical >= work on ISO dates but fail on other formats?", "How would you convert this to a per-day time series for load analysis?"],
    },
    {
        "id": "sql-rank-privilege-holders",
        "title": "Rank users by maximum privilege level",
        "difficulty": "medium",
        "category": "Window function",
        "problem": "For each user holding roles, compute their maximum privilege_level and rank users by that maximum descending. Return username, max privilege and rank. Users tie on the same maximum share the same rank (use RANK semantics).",
        "hints": ["Aggregate first (MAX per user), then apply RANK() OVER (ORDER BY max DESC).", "In a subquery: GROUP BY user, then window over the result.", "RANK() leaves gaps after ties; DENSE_RANK() does not — either is acceptable if you explain it."],
        "expected_sql": (
            "SELECT username, max_priv, RANK() OVER (ORDER BY max_priv DESC) AS rnk FROM ("
            "  SELECT u.username, MAX(r.privilege_level) AS max_priv FROM USERS u "
            "  JOIN USER_ROLES ur ON u.user_id = ur.user_id "
            "  JOIN ROLES r ON ur.role_id = r.role_id "
            "  GROUP BY u.username"
            ") ORDER BY rnk, username"
        ),
        "explanation": (
            "Window functions post-process aggregates: aggregate in a subquery, then RANK() OVER the "
            "result. The RANK vs DENSE_RANK distinction (gaps after ties) is a favourite follow-up. "
            "This query is a risk-scored user inventory — exactly what a security dashboard ranks."
        ),
        "security_note": "Prioritise certification and monitoring effort on the highest-privilege users.",
        "followups": ["RANK vs DENSE_RANK vs ROW_NUMBER — when does each matter?", "How would you add a running total of privileged users with a window frame?"],
    },
    {
        "id": "sql-certification-campaign-stats",
        "title": "Campaign outcome statistics",
        "difficulty": "medium",
        "category": "Aggregation",
        "problem": "For campaign 'CAMP-2025-Q4', return decision (including NULL as 'PENDING') and the count of certifications with that decision.",
        "hints": ["GROUP BY decision with NULLs collapsed.", "COALESCE(decision, 'PENDING') labels the NULL group."],
        "expected_sql": (
            "SELECT COALESCE(decision, 'PENDING') AS decision, COUNT(*) AS cnt "
            "FROM CERTIFICATIONS WHERE campaign_id = 'CAMP-2025-Q4' "
            "GROUP BY COALESCE(decision, 'PENDING') ORDER BY decision"
        ),
        "explanation": (
            "GROUP BY treats each NULL as its own group; COALESCE renames it for reporting. This is "
            "the dashboard-validation query for campaign statistics: your automation compares the UI "
            "campaign summary widget against exactly these numbers, row by row."
        ),
        "security_note": "Campaign completion statistics are audit artefacts — they must match the database exactly.",
        "followups": ["How would you automate dashboard-vs-database comparison for these numbers?", "What NULL-handling traps exist in GROUP BY?"],
    },
    {
        "id": "sql-duplicate-role-assignments",
        "title": "Duplicate role assignments for the same user",
        "difficulty": "medium",
        "category": "Data integrity",
        "problem": "Find users assigned the SAME role more than once. Return username, role_name and the assignment count.",
        "hints": ["GROUP BY user_id, role_id.", "HAVING COUNT(*) > 1.", "Join for readable names."],
        "expected_sql": (
            "SELECT u.username, r.role_name, COUNT(*) AS assignments FROM USERS u "
            "JOIN USER_ROLES ur ON u.user_id = ur.user_id "
            "JOIN ROLES r ON ur.role_id = r.role_id "
            "GROUP BY u.user_id, u.username, r.role_name "
            "HAVING COUNT(*) > 1 ORDER BY u.username"
        ),
        "explanation": (
            "Duplicate assignments usually mean a retry bug or a reconciliation defect: the job "
            "re-ran and re-granted what already existed. That is why provisioning operations must "
            "be idempotent — same input, same final state, no duplicates."
        ),
        "security_note": "Non-idempotent provisioning is a classic integration defect; retries must not duplicate grants.",
        "followups": ["How would you prove whether a retry or a duplicate correlation caused this?", "How do you test idempotency of a provisioning API?"],
    },
    {
        "id": "sql-null-email-data-quality",
        "title": "Users with missing emails",
        "difficulty": "easy",
        "category": "Data quality",
        "problem": "Find users whose email is NULL or an empty string. Return username and status.",
        "hints": ["NULL is not '' — check both.", "email IS NULL OR email = ''."],
        "expected_sql": (
            "SELECT username, status FROM USERS "
            "WHERE email IS NULL OR email = '' ORDER BY username"
        ),
        "explanation": (
            "NULL vs empty string trips up juniors constantly: WHERE email = '' alone misses NULLs, "
            "and = NULL is never true. In IAM, a missing email breaks correlation, notifications "
            "and MFA enrolment — data quality is a security control here."
        ),
        "security_note": "Broken notification channels mean users never learn about access changes affecting them.",
        "followups": ["Why does WHERE email = NULL never match?", "How would you validate email uniqueness as part of a data quality suite?"],
    },
    {
        "id": "sql-users-needing-certification",
        "title": "Privileged users not covered by any certification",
        "difficulty": "hard",
        "category": "NOT EXISTS",
        "problem": "Find users holding at least one role with privilege_level >= 5 who have NO certification row at all in CERTIFICATIONS. Return username and the privileged role_name.",
        "hints": ["Filter to privileged roles first.", "NOT EXISTS a certification row for that user.", "DISTINCT if a user holds multiple privileged roles — keep user+role pairs."],
        "expected_sql": (
            "SELECT DISTINCT u.username, r.role_name FROM USERS u "
            "JOIN USER_ROLES ur ON u.user_id = ur.user_id "
            "JOIN ROLES r ON ur.role_id = r.role_id "
            "WHERE r.privilege_level >= 5 "
            "AND NOT EXISTS (SELECT 1 FROM CERTIFICATIONS c WHERE c.user_id = u.user_id) "
            "ORDER BY u.username, r.role_name"
        ),
        "explanation": (
            "Governance coverage analysis: privileged access exists but was never reviewed. "
            "This is the query that turns a routine campaign test into an audit finding — "
            "reviewers review who is IN the campaign; nobody checks who is MISSING from it."
        ),
        "security_note": "Privileged access outside certification scope is unreviewed access — an audit finding by definition.",
        "followups": ["How would you test that campaign population rules include every privileged user?", "What population rule (query) generates the campaign members?"],
    },
    {
        "id": "sql-provisioning-source-comparison",
        "title": "Compare provisioning records against current access",
        "difficulty": "hard",
        "category": "Correlation",
        "problem": "Find users with a SUCCESS 'CREATE_ACCOUNT' log for 'Jira' but no QA_AUTOMATION or EMPLOYEE role — i.e. an account exists in a target application without matching entitlements recorded. Return username and application_name.",
        "hints": ["SUCCESS CREATE_ACCOUNT rows define accounts provisioned.", "NOT EXISTS the matching role assignment.", "This is reconciliation: source-of-truth vs target state."],
        "expected_sql": (
            "SELECT u.username, p.application_name FROM USERS u "
            "JOIN PROVISIONING_LOGS p ON u.user_id = p.user_id "
            "WHERE p.application_name = 'Jira' AND p.operation = 'CREATE_ACCOUNT' AND p.status = 'SUCCESS' "
            "AND NOT EXISTS ("
            "  SELECT 1 FROM USER_ROLES ur JOIN ROLES r ON ur.role_id = r.role_id "
            "  WHERE ur.user_id = u.user_id AND r.role_name IN ('QA_AUTOMATION','EMPLOYEE')"
            ") "
            "ORDER BY u.username"
        ),
        "explanation": (
            "Reconciliation in miniature: the provisioning log says the target account was created, "
            "but the entitlement store disagrees about what the user should have. Direction matters — "
            "log-without-role can mean a failed entitlement step; role-without-log can mean drift "
            "(access granted outside the platform). Both are findings with different root causes."
        ),
        "security_note": "Drift between the entitlement store and target systems is what reconciliation jobs exist to catch.",
        "followups": ["How would you distinguish missing entitlement records from connector logging gaps?", "Design the reconciliation test for 10k users, nightly."],
    },
    {
        "id": "sql-privilege-by-department",
        "title": "Maximum privilege level by department",
        "difficulty": "medium",
        "category": "Aggregation",
        "problem": "For each department, return the maximum privilege_level held by any user in it, plus the number of users in the department who hold at least one role. Order by maximum privilege descending.",
        "hints": ["Aggregate over the three-way join.", "MAX(privilege_level) per department.", "COUNT(DISTINCT user_id) counts role-holding users."],
        "expected_sql": (
            "SELECT u.department, MAX(r.privilege_level) AS max_priv, COUNT(DISTINCT u.user_id) AS users_with_roles "
            "FROM USERS u "
            "JOIN USER_ROLES ur ON u.user_id = ur.user_id "
            "JOIN ROLES r ON ur.role_id = r.role_id "
            "GROUP BY u.department ORDER BY max_priv DESC, u.department"
        ),
        "explanation": (
            "Risk heat map by department: where does the highest privilege live, and how many people "
            "hold roles there? Multi-aggregate GROUP BY (MAX plus a distinct count) is standard "
            "interview material, and the security interpretation is what elevates the answer."
        ),
        "security_note": "Departments with high max privilege and many role holders deserve priority certification.",
        "followups": ["How would you exclude terminated users from this report and why does that matter?", "How would you trend this monthly for a security dashboard?"],
    },
]


def list_challenges() -> list[dict]:
    out = []
    for c in SQL_CHALLENGES:
        meta = {k: v for k, v in c.items() if k not in {"expected_sql", "hints", "explanation"}}
        out.append(meta)
    return out


def get_challenge(challenge_id: str) -> dict | None:
    for c in SQL_CHALLENGES:
        if c["id"] == challenge_id:
            return c
    return None
