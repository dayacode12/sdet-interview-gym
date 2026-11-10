"""IAM / cybersecurity learning modules for the Schwab SDET preparation."""
from __future__ import annotations

IAM_MODULES = [
    {
        "id": "iam-fundamentals",
        "title": "Module A: IAM Fundamentals",
        "summary": (
            "Identity and Access Management is the discipline that answers two questions for every "
            "request: who are you (authentication) and what are you allowed to do (authorization). "
            "Everything else in this gym — IGA, PAM, DLP — builds on these primitives."
        ),
        "concepts": [
            {
                "name": "Authentication vs Authorization",
                "explanation": (
                    "Authentication proves WHO you are (password, OTP, biometric, certificate). "
                    "Authorization decides WHAT you may do (roles, entitlements, policies). "
                    "A user can be fully authenticated and completely unauthorized: HTTP 401 means "
                    "the request had missing/invalid credentials; 403 means valid credentials that "
                    "lack permission. Testing them separately is the heart of security QA."
                ),
                "practical_example": (
                    "API test: GET /api/admin/users with a valid employee token returns 403 Forbidden "
                    "(authenticated, not authorized). With a garbage token it returns 401 "
                    "(not authenticated). Both must be asserted, never conflated."
                ),
            },
            {
                "name": "Identity lifecycle (JML)",
                "explanation": (
                    "Joiner-Mover-Leaver: an identity is created with initial access when someone "
                    "joins, entitlements are adjusted when they move between roles, and ALL access "
                    "is revoked when they leave. Deprovisioning failures are the highest-risk "
                    "lifecycle defects because terminated users with live access are invisible "
                    "attackers with valid credentials."
                ),
                "practical_example": (
                    "Termination test: HR marks a user TERMINATED -> IGA event fires -> "
                    "deprovisioning runs per application -> you verify in the DATABASE of each "
                    "target app, not just the IGA dashboard."
                ),
            },
            {
                "name": "SSO (Single Sign-On)",
                "explanation": (
                    "One authentication event grants access to many applications, usually via SAML "
                    "or OIDC with a central Identity Provider (IdP). The IdP asserts who the user is; "
                    "the Service Provider (SP) decides what that identity may access. "
                    "Logout is the hard part: SP-initiated logout must terminate every downstream "
                    "session, not just the IdP one."
                ),
                "practical_example": (
                    "SSO test: log in once on the portal, open the CRM in a new tab — you are in "
                    "without a second password. Then log out and reopen the CRM tab — you must be "
                    "redirected to login (session truly terminated)."
                ),
            },
            {
                "name": "MFA (Multi-Factor Authentication)",
                "explanation": (
                    "Two or more factors from different categories: something you know (password), "
                    "something you have (phone, hardware key), something you are (biometric). "
                    "Two passwords are NOT MFA. Testing centres on OTP validity windows, replay "
                    "attempts, lockout thresholds and recovery flows."
                ),
                "practical_example": (
                    "MFA tests: valid OTP passes; expired OTP fails; reusing a consumed OTP fails; "
                    "5 wrong OTPs lock the account; recovery flow re-verifies identity instead of "
                    "bypassing MFA entirely."
                ),
            },
            {
                "name": "RBAC vs ABAC",
                "explanation": (
                    "RBAC grants access through assigned roles; the role is the unit of permission. "
                    "ABAC evaluates attributes at decision time: user department, resource "
                    "classification, time of day, location. ABAC is more expressive and more "
                    "expensive to test — every attribute combination is a test condition."
                ),
                "practical_example": (
                    "RBAC: the UNDERWRITER role can approve policies. ABAC: an underwriter can "
                    "approve policies CLASSIFIED 'internal' DURING business hours FROM the "
                    "corporate network — change any attribute and access must change."
                ),
            },
            {
                "name": "Least privilege & Zero Trust",
                "explanation": (
                    "Least privilege: every identity holds the minimum access needed for its job, "
                    "verified against what was approved (assigned vs approved comparison). "
                    "Zero trust: no implicit trust from network location — every request is "
                    "authenticated, authorized and logged, as if it came from the open internet."
                ),
                "practical_example": (
                    "Least-privilege test: export the user's effective entitlements (API + database), "
                    "diff against the APPROVED request history, and raise a finding for anything "
                    "granted without approval."
                ),
            },
        ],
        "architecture": (
            "User -> Application (SP) -> Identity Provider (IdP)\n"
            "                              |\n"
            "                     Directory / HR source\n"
            "                              |\n"
            "                     IAM platform (authN + authZ + policy)\n"
            "                              |\n"
            "                     Target applications (Jira, Salesforce, CyberArk)\n"
            "\n"
            "AuthN decision at the IdP. AuthZ decision at the SP/policy layer. "
            "Audit logging at every hop."
        ),
        "interview_questions": [
            {
                "question": "Explain authentication vs authorization with an API example.",
                "answer": (
                    "Authentication answers 'who are you' — verified by credentials, tokens, MFA. "
                    "Authorization answers 'what may you do' — verified by roles, entitlements, "
                    "policies. Concretely: GET /api/users with an expired token returns 401 "
                    "(authentication failed). The same endpoint with a valid employee token but an "
                    "admin-only resource returns 403 (authorization failed). I test the two "
                    "independently: invalid tokens, valid tokens with wrong roles, role hierarchies, "
                    "and direct API calls that bypass the UI."
                ),
            },
            {
                "question": "What is the riskiest part of the identity lifecycle to test?",
                "answer": (
                    "The Leaver phase. A failed Joiner blocks someone from working (visible, noisy, "
                    "fixed fast). A failed Leaver leaves a terminated user with live credentials — "
                    "silent, invisible, exploited. My termination tests always validate the "
                    "downstream applications and databases, not just the IGA status field, "
                    "because 'terminated' in the dashboard does not revoke anything by itself."
                ),
            },
            {
                "question": "How would you test SSO logout?",
                "answer": (
                    "Logout is where SSO implementations leak. I test: SP-initiated logout "
                    "terminates the IdP session AND the downstream application sessions; the "
                    "back-channel logout reaches every SP; a browser back-button after logout does "
                    "not restore an authenticated page; and tokens issued before logout are rejected "
                    "afterwards. A stale session after logout is a real security defect, not a "
                    "cosmetic one."
                ),
            },
        ],
        "test_cases": [
            {
                "title": "Valid credentials authenticate successfully",
                "type": "positive",
                "steps": "Login with active user + correct password + valid OTP.",
                "expected": "Session established; landing page shows the user's role.",
            },
            {
                "title": "Valid authentication but unauthorized endpoint returns 403",
                "type": "negative",
                "steps": "Call GET /api/admin/users with an authenticated EMPLOYEE token.",
                "expected": "403 Forbidden; no user list in the response body.",
            },
            {
                "title": "Invalid token returns 401, not 403",
                "type": "negative",
                "steps": "Call the same endpoint with a malformed/expired bearer token.",
                "expected": "401 Unauthorized; audit log records the rejected attempt.",
            },
            {
                "title": "MFA lockout after repeated wrong OTPs",
                "type": "boundary",
                "steps": "Enter an incorrect OTP five times.",
                "expected": "Account locks after the configured threshold; audit event recorded.",
            },
        ],
        "quiz": [
            {
                "question": "A request carries a valid token but the user lacks permission for the resource. What status code should the API return?",
                "options": ["401 Unauthorized", "403 Forbidden", "200 OK with empty body", "302 Redirect"],
                "correct_index": 1,
                "explanation": "403 = authenticated but not authorized. 401 is for missing/invalid credentials.",
            },
            {
                "question": "A user enters their password and then a code from an authenticator app. This is MFA because the factors are:",
                "options": ["Something you know + something you have", "Two things you know", "Something you are + something you know", "Two instances of the same factor"],
                "correct_index": 0,
                "explanation": "Password (knowledge) + device-generated code (possession) are different factor categories.",
            },
            {
                "question": "Which statement describes least privilege most accurately?",
                "options": [
                    "Users get the access their peers have",
                    "Users get only the access approved for their role, nothing more",
                    "Admins decide access case by case without records",
                    "Access expires automatically after 30 days",
                ],
                "correct_index": 1,
                "explanation": "Least privilege = minimum necessary access, verifiable against the approved baseline.",
            },
            {
                "question": "RBAC grants access based on:",
                "options": ["Attributes like time and location", "Assigned roles", "Biometric identity", "Network segment"],
                "correct_index": 1,
                "explanation": "RBAC is role-driven; ABAC is attribute-driven.",
            },
        ],
    },
    {
        "id": "iga-saviynt",
        "title": "Module B: IGA (Identity Governance & Administration)",
        "summary": (
            "IGA adds governance to IAM: who has access, who approved it, whether it is still "
            "needed, and evidence that all of it was reviewed. This is the Saviynt territory from "
            "your resume — access requests, certifications, JML workflows, provisioning, "
            "deprovisioning and reconciliation."
        ),
        "concepts": [
            {
                "name": "Access requests",
                "explanation": (
                    "Users request entitlements; the workflow routes the request for approval "
                    "(manager, role owner, application owner, sometimes two-stage); approved "
                    "requests trigger provisioning. Governance requires that every grant maps to "
                    "an approved request — a grant without a request is a finding."
                ),
                "practical_example": (
                    "Request tests: approval required; rejection grants nothing; the requester cannot "
                    "approve their own request; duplicate requests are idempotent; escalation fires "
                    "when an approver is unavailable."
                ),
            },
            {
                "name": "Access certifications",
                "explanation": (
                    "Periodic campaigns where reviewers confirm or revoke each user's entitlements. "
                    "The certification decision is only half the story — enforcement of the decision "
                    "downstream is what you must verify. Overdue campaigns auto-complete per policy "
                    "(confirm-all or revoke-all), and that policy is itself a test condition."
                ),
                "practical_example": (
                    "Campaign tests: population rules include every in-scope user; approve/revoke/"
                    "delegate/bulk actions work; revoked entitlements disappear from the target "
                    "application; campaign statistics match the database."
                ),
            },
            {
                "name": "Provisioning & deprovisioning",
                "explanation": (
                    "Provisioning = creating/updating accounts and entitlements on target systems "
                    "through connectors. Deprovisioning = removing them. Both must be idempotent "
                    "(retries do not duplicate), observable (logs per operation), and eventually "
                    "consistent (a FAILED operation must be retried or escalated, never silently "
                    "dropped)."
                ),
                "practical_example": (
                    "Provisioning tests: happy path; connector down (retry policy); partial failure "
                    "across 5 of 6 apps (only the failing one retries); duplicate execution does not "
                    "create duplicate accounts."
                ),
            },
            {
                "name": "Reconciliation & user correlation",
                "explanation": (
                    "Reconciliation compares the IGA view with reality on each target system and "
                    "fixes drift. Correlation maps a source record (HR feed) to an existing identity "
                    "via rules (employee ID, email). Correlation failures create duplicate identities; "
                    "bad rules merge two different people — both are security incidents."
                ),
                "practical_example": (
                    "Reconciliation test: 10,000 source records, 9,500 imported — I chase the 500 "
                    "through failure logs, correlation-rule rejects and pagination, and verify "
                    "source-count == processed-count == target-count."
                ),
            },
            {
                "name": "Joiner-Mover-Leaver (JML)",
                "explanation": (
                    "HR is the source of truth: hire events create identities with birthright access; "
                    "transfers (mover) revoke old department roles and grant new ones — the mover gap "
                    "(keeping BOTH sets) is the classic defect; termination revokes everything "
                    "everywhere."
                ),
                "practical_example": (
                    "Mover test: transfer a user from Claims to Risk; assert Claims entitlements "
                    "are gone (not just Risk ones added). Leaver test: verify deprovisioning per "
                    "target application via database and login attempt."
                ),
            },
            {
                "name": "Saviynt-specific concepts",
                "explanation": (
                    "Saviynt Enterprise Identity Cloud models: security systems (target applications), "
                    "endpoint accounts, entitlements, request/provisioning workflows, AR (access "
                    "request) rules, certification campaigns, analytics dashboards, and rule-based "
                    "user import from HR. Your testing covered EIC workflows, CIAM integrations and "
                    "dashboard validation against SQL — describe those with concrete examples."
                ),
                "practical_example": (
                    "Saviynt test: create an access request in EIC, approve it, verify the "
                    "provisioning task completes for the endpoint, confirm the entitlement in the "
                    "target app database, then validate the analytics dashboard count via SQL."
                ),
            },
        ],
        "architecture": (
            "HR system (source of truth)\n"
            "      |  nightly feed / events\n"
            "      v\n"
            "IGA platform (Saviynt EIC)\n"
            "  - user correlation rules\n"
            "  - JML workflows\n"
            "  - access requests -> approvals -> provisioning\n"
            "  - certification campaigns\n"
            "  - analytics dashboards\n"
            "      |  connectors (REST / LDAP / DB / CyberArk)\n"
            "      v\n"
            "Target applications + audit logs\n"
            "\n"
            "Every arrow is an integration you can test: event delivery, transformation, "
            "error handling, retry, and reconciliation of counts."
        ),
        "interview_questions": [
            {
                "question": "How did you test JML workflows in Saviynt?",
                "answer": (
                    "For Joiners I validated identity creation from the HR feed, birthright "
                    "entitlements and the provisioning tasks generated per application. For Movers, "
                    "the critical assertion is that OLD department entitlements are revoked, not just "
                    "new ones added — that mover gap is where access accumulates. For Leavers, I "
                    "verified termination events, deprovisioning per target application, role "
                    "removal in the database, and a failed login attempt with the old credentials. "
                    "I never accepted the Saviynt status field alone as evidence of revocation — "
                    "the target system is the truth."
                ),
            },
            {
                "question": "A manager revoked access in a certification campaign but the user still has it. How do you investigate?",
                "answer": (
                    "First reproduce with data: query the certification decision, then the "
                    "entitlement in IGA, then the target application. The gap can be: the revocation "
                    "workflow did not trigger; the provisioning task was created but failed; the "
                    "connector call succeeded but the application ignored it; or the reconciliation "
                    "job has not run yet. I check provisioning logs for the revoke operation, its "
                    "status and retries, then verify the target system directly. The fix differs "
                    "completely depending on which hop broke — that is why evidence-first matters."
                ),
            },
            {
                "question": "How do you test reconciliation when records go missing?",
                "answer": (
                    "Counts first: source records, records read, records processed, records "
                    "failed, records created/updated in the target. If 10,000 came in and 9,500 "
                    "landed, I work the 500 through the failure tables and logs: correlation-rule "
                    "rejects (bad employee IDs, null emails), API pagination (was a page skipped?), "
                    "rate limiting, and timeouts mid-run. Then I verify retry behaviour and that a "
                    "re-run is idempotent — it must not create duplicates. A successful scheduler "
                    "status proves nothing about business processing; counts and record-level "
                    "reconciliation do."
                ),
            },
        ],
        "test_cases": [
            {
                "title": "Access request requires approval before any grant",
                "type": "positive",
                "steps": "Employee requests ADMIN role; check entitlement before and after approval.",
                "expected": "No access until approved; grant only after final approval step.",
            },
            {
                "title": "Rejected request grants nothing",
                "type": "negative",
                "steps": "Reject the request at the final approval stage.",
                "expected": "Entitlement absent in IGA and target application; audit entry records the rejection.",
            },
            {
                "title": "Requester cannot approve their own request",
                "type": "negative",
                "steps": "Attempt to approve your own pending request via UI and directly via API.",
                "expected": "Blocked in UI with 403 on the API path; attempt logged.",
            },
            {
                "title": "Termination revokes access in every downstream application",
                "type": "boundary",
                "steps": "Terminate a user with accounts in 5 applications; verify each.",
                "expected": "All 5 disabled/revoked; failed revocations retried and escalated; login denied.",
            },
            {
                "title": "Duplicate execution of a provisioning job does not duplicate accounts",
                "type": "boundary",
                "steps": "Trigger the same provisioning job twice concurrently.",
                "expected": "Exactly one account per user; second run is a no-op (idempotent).",
            },
        ],
        "quiz": [
            {
                "question": "What is the most reliable evidence that a terminated user's access was revoked?",
                "options": [
                    "The IGA dashboard shows status TERMINATED",
                    "The HR feed shows termination",
                    "The target application database shows the account disabled and login is denied",
                    "The certification campaign completed",
                ],
                "correct_index": 2,
                "explanation": "Only the target system state (and a failed login attempt) proves revocation.",
            },
            {
                "question": "A user transfers departments but keeps BOTH old and new entitlements. This is called:",
                "options": ["Idempotency defect", "Mover gap / privilege accumulation", "Correlation failure", "Fail-open policy"],
                "correct_index": 1,
                "explanation": "The classic mover defect: old access should be revoked when new access is granted.",
            },
            {
                "question": "Reconciliation compares:",
                "options": [
                    "Two HR systems with each other",
                    "The IGA view with actual state on target systems",
                    "Passwords across vaults",
                    "Dashboard charts with API latency",
                ],
                "correct_index": 1,
                "explanation": "Reconciliation detects and corrects drift between the platform and reality.",
            },
            {
                "question": "Why must provisioning be idempotent?",
                "options": [
                    "To run faster",
                    "So retries and duplicate job executions do not create duplicate accounts or grants",
                    "To encrypt data at rest",
                    "To satisfy OAuth",
                ],
                "correct_index": 1,
                "explanation": "Same input, same final state — retries must be safe.",
            },
        ],
    },
    {
        "id": "pam-cyberark",
        "title": "Module C: PAM (Privileged Access Management)",
        "summary": (
            "PAM treats admin and service accounts as the highest-value targets: vaulted "
            "credentials, automatic rotation, just-in-time elevation, session monitoring and "
            "auditing. Your CyberArk integration testing is directly relevant here."
        ),
        "concepts": [
            {
                "name": "Privileged accounts",
                "explanation": (
                    "Human admin accounts, service/application accounts and break-glass accounts. "
                    "Service accounts are the dangerous ones: shared, long-lived, often embedded in "
                    "scripts. PAM exists so that nobody knows a standing privileged password."
                ),
                "practical_example": (
                    "Test: a service account password embedded in a config file (not vaulted) is a "
                    "finding; retrieving it from the vault yields a CURRENT credential after rotation."
                ),
            },
            {
                "name": "Vaulting & password rotation",
                "explanation": (
                    "Credentials live in a vault; check-in/check-out or just-in-time access replaces "
                    "standing access. Rotation changes the credential automatically (on schedule, "
                    "on check-in, or on demand) so old copies die. Testing rotation means verifying "
                    "every consumer of the credential picks up the new value."
                ),
                "practical_example": (
                    "Rotation test: rotate a vaulted DB credential, then verify the old password is "
                    "rejected and the application using the vault integration still connects."
                ),
            },
            {
                "name": "Session monitoring & isolation",
                "explanation": (
                    "Privileged sessions are recorded, keystroke-logged or isolated (no direct "
                    "network path to the target). This is detective control on top of preventive "
                    "control. Testing covers session start/stop, recording completeness and "
                    "retrieval of recordings as evidence."
                ),
                "practical_example": (
                    "Test: run a privileged session performing known commands; verify the recording "
                    "contains them and that a session outside the PAM broker is blocked by network "
                    "isolation."
                ),
            },
            {
                "name": "Privileged access approvals & JIT",
                "explanation": (
                    "Elevation on demand with approval, time bound (4 hours, not forever), "
                    "with automatic expiry. The expiry is the control most likely to be broken "
                    "in implementations — access outliving its window is a defect you must catch."
                ),
                "practical_example": (
                    "Test: request JIT access for 1 hour; verify access works, expires at 60 minutes, "
                    "and that attempts after expiry are denied while everything is audited."
                ),
            },
        ],
        "architecture": (
            "Requester -> Approval workflow (manager / owner)\n"
            "                 |\n"
            "                 v\n"
            "        PAM vault (CyberArk)\n"
            "          - stores credentials (never in plaintext to the user)\n"
            "          - rotates on check-in / schedule\n"
            "                 |\n"
            "                 v\n"
            "        Session broker / isolation layer\n"
            "                 |\n"
            "                 v\n"
            "        Target system (DB, server, cloud console)\n"
            "                 |\n"
            "        Audit: who, what, when, recording, duration\n"
        ),
        "interview_questions": [
            {
                "question": "How did you test CyberArk integrations?",
                "answer": (
                    "I treated CyberArk as another integration target: provisioning privileged "
                    "accounts into safes, verifying role-to-safe mappings, validating that "
                    "rotation events keep dependent integrations working, and asserting that "
                    "access requests for privileged entitlements require the right approvals. "
                    "The failure modes I tested included the vault being unreachable "
                    "(fail-closed vs fail-open behaviour), rotation breaking a cached credential "
                    "consumer, and JIT expiry not actually revoking access."
                ),
            },
            {
                "question": "What does fail-open vs fail-closed mean for a PAM integration?",
                "answer": (
                    "If the vault is unreachable, does the integration deny everything (fail-closed, "
                    "secure but blocks work) or allow cached/last-known access (fail-open, available "
                    "but risky)? For privileged access the expected policy is almost always "
                    "fail-closed. The requirement is the test oracle: I verify actual behaviour "
                    "matches the documented policy and I report a mismatch as a security defect."
                ),
            },
        ],
        "test_cases": [
            {
                "title": "Vaulted credential is never exposed in plaintext",
                "type": "negative",
                "steps": "Retrieve a privileged credential through the API/UI and inspect logs and responses.",
                "expected": "Credential masked in UI/API responses and logs; only the broker can use it.",
            },
            {
                "title": "Rotation invalidates the old password everywhere",
                "type": "boundary",
                "steps": "Trigger rotation; attempt authentication with the old password from an app.",
                "expected": "Old password rejected; vault-integrated consumers continue to work.",
            },
            {
                "title": "JIT elevation expires on schedule",
                "type": "boundary",
                "steps": "Grant 1-hour elevation; attempt access at 61 minutes.",
                "expected": "Access denied after expiry; audit record shows the window.",
            },
            {
                "title": "Privileged session outside the broker is blocked",
                "type": "negative",
                "steps": "Attempt direct connection to the target bypassing the PAM session broker.",
                "expected": "Connection refused by network isolation; attempt logged as violation.",
            },
        ],
        "quiz": [
            {
                "question": "After a scheduled password rotation, a legacy script using the old password fails. This proves:",
                "options": [
                    "The rotation worked correctly and the script bypassed the vault",
                    "The vault is broken",
                    "Rotation should be disabled",
                    "The script has higher privileges",
                ],
                "correct_index": 0,
                "explanation": "Consumers must integrate with the vault; standing copies of credentials are the defect.",
            },
            {
                "question": "For privileged access, the expected behaviour when the vault is unreachable is usually:",
                "options": ["Fail-open with cached credentials", "Fail-closed and deny access", "Fallback to local admin passwords", "Email the credentials"],
                "correct_index": 1,
                "explanation": "Privileged access should fail closed; availability loss is accepted over exposure.",
            },
            {
                "question": "Session recording in PAM is an example of:",
                "options": ["Preventive control", "Detective control", "Authentication factor", "Data classification"],
                "correct_index": 1,
                "explanation": "Recording detects/investigates misuse rather than preventing it.",
            },
        ],
    },
    {
        "id": "auth-protocols",
        "title": "Module D: Authentication Protocols",
        "summary": (
            "OAuth 2.0, OIDC, SAML and JWT are the protocols your IAM tests ride on. You do not "
            "need to implement them; you must test their behaviour — token validity, expiry, "
            "audience, scopes and revocation."
        ),
        "concepts": [
            {
                "name": "OAuth 2.0",
                "explanation": (
                    "Delegated AUTHORIZATION framework: a client obtains an access token with "
                    "scoped permissions to act on a resource owner's behalf. Flows: authorization "
                    "code (with PKCE) for apps, client credentials for services, refresh token "
                    "grant to renew. OAuth alone does not authenticate the user — that is the "
                    "classic interview trap."
                ),
                "practical_example": (
                    "OAuth tests: token with scope 'read' cannot write; expired token returns 401; "
                    "refresh token yields a new access token; revoked token is rejected immediately; "
                    "wrong audience token is refused by the resource server."
                ),
            },
            {
                "name": "OpenID Connect (OIDC)",
                "explanation": (
                    "An identity layer ON TOP of OAuth 2.0: adds an ID token (a JWT) that asserts who "
                    "the user is. OAuth answers 'can this client do X'; OIDC answers 'who logged "
                    "in'. The ID token's claims (sub, iss, aud, exp) are your test oracles."
                ),
                "practical_example": (
                    "OIDC test: after login, decode the ID token and assert sub matches the user, "
                    "iss is the expected issuer, aud is your client, and exp is in the future — "
                    "each claim mismatch must be rejected."
                ),
            },
            {
                "name": "SAML 2.0",
                "explanation": (
                    "XML-based SSO used heavily in enterprises: the IdP issues signed assertions; "
                    "the SP validates the signature, audience and NotOnOrAfter window. "
                    "Replay of an old assertion and signature validation failure are the two "
                    "test cases interviewers expect you to name."
                ),
                "practical_example": (
                    "SAML tests: valid assertion logs in; tampered assertion (altered NameID) is "
                    "rejected; expired assertion rejected; assertion replayed after logout rejected; "
                    "unknown audience rejected."
                ),
            },
            {
                "name": "JWT",
                "explanation": (
                    "A token FORMAT: header.payload.signature, base64url-encoded, cryptographically "
                    "signed. Statelessness is the trade-off: the server cannot 'delete' a JWT, so "
                    "revocation needs short expiry or a deny-list. Never trust a JWT whose "
                    "signature you did not verify — that mistake is a top security finding."
                ),
                "practical_example": (
                    "JWT tests: modifying the payload invalidates the signature; exp in the past is "
                    "rejected; alg=none is rejected; a revoked token is refused on the deny-list."
                ),
            },
            {
                "name": "Token lifetime & sessions",
                "explanation": (
                    "Access tokens are short-lived (minutes); refresh tokens are longer and can be "
                    "rotated. Idle vs absolute session timeouts matter for UI testing: idle timeout "
                    "logs out after inactivity, absolute timeout caps the session regardless of "
                    "activity. Both must be tested against policy."
                ),
                "practical_example": (
                    "Session test: idle 30 minutes -> auto-logout; still-active use must not survive "
                    "the absolute 8-hour cap; the refresh flow works exactly at the boundary, not "
                    "just comfortably inside it."
                ),
            },
        ],
        "architecture": (
            "Authorization Code + PKCE (web app login):\n"
            "\n"
            "Browser -> App: login\n"
            "App -> IdP: redirect /authorize (client_id, scope, code_challenge, state)\n"
            "IdP -> User: authenticate (password + MFA)\n"
            "IdP -> App: redirect back with code + state (state must match!)\n"
            "App -> IdP: POST /token (code + code_verifier)  [back-channel]\n"
            "IdP -> App: access_token (+ id_token for OIDC)\n"
            "App -> API: call with Authorization: Bearer <token>\n"
            "API: verify signature, iss, aud, exp, scope -> allow/deny\n"
        ),
        "interview_questions": [
            {
                "question": "Explain OAuth 2.0 vs OIDC in one breath, then say how you test each.",
                "answer": (
                    "OAuth 2.0 is delegated authorization: the client gets a scoped access token to "
                    "act on the user's behalf. OIDC adds authentication: an ID token asserting who "
                    "the user is, on top of the OAuth flow. For OAuth I test scope enforcement, "
                    "expiry, refresh and revocation of access tokens. For OIDC I test ID token "
                    "claims: sub, iss, aud, exp — each mismatched value must be rejected. And I "
                    "always test the failure paths: tampered tokens, wrong audience, replayed "
                    "authorization codes, and state parameter mismatch."
                ),
            },
            {
                "question": "How would you test that a JWT is being validated properly?",
                "answer": (
                    "Attack the three parts: header (alg=none or algorithm downgrade must be "
                    "rejected), payload (modify sub or role — signature check must fail it), "
                    "signature (garbage signature rejected). Then temporal claims: exp in the past, "
                    "nbf in the future. Then context: wrong iss, wrong aud. If any of those still "
                    "authorize, that is a P1 authentication bypass, and I reproduce it with an API "
                    "test in the regression suite so it never returns."
                ),
            },
            {
                "question": "Why can a logged-out JWT still work, and what do you do about it?",
                "answer": (
                    "JWTs are stateless: the resource server validates them from the signature and "
                    "claims, without asking the issuer. Logging out usually clears the browser "
                    "session but cannot un-issue the token. Mitigations: short access-token expiry, "
                    "refresh-token revocation, and deny-lists of jti values checked by the API. "
                    "I test all three: after logout the access token ideally stops working within "
                    "policy, the refresh token definitely stops working, and deny-listed tokens are "
                    "refused."
                ),
            },
        ],
        "test_cases": [
            {
                "title": "Tampered JWT payload is rejected",
                "type": "negative",
                "steps": "Decode the access token, change the role claim, re-encode without re-signing, call the API.",
                "expected": "401; signature validation failure logged.",
            },
            {
                "title": "Expired access token returns 401",
                "type": "boundary",
                "steps": "Use a token whose exp is in the past.",
                "expected": "401 with token-expired error code; refresh flow can still obtain a new token.",
            },
            {
                "title": "Scope enforcement on a write endpoint",
                "type": "negative",
                "steps": "Call POST /api/requests with a token scoped 'read'.",
                "expected": "403 insufficient_scope; nothing created.",
            },
            {
                "title": "Authorization code replay is rejected",
                "type": "negative",
                "steps": "Exchange an authorization code at /token, then attempt the same exchange again.",
                "expected": "Second exchange rejected; first token remains valid; replay logged.",
            },
            {
                "title": "SAML assertion with tampered NameID is rejected",
                "type": "negative",
                "steps": "Capture a valid assertion, modify the NameID, post it to the SP.",
                "expected": "Signature validation fails; no session created.",
            },
        ],
        "quiz": [
            {
                "question": "OAuth 2.0 by itself provides:",
                "options": ["User authentication", "Delegated authorization", "Data loss prevention", "Password storage"],
                "correct_index": 1,
                "explanation": "Authentication of the end user is what OIDC adds on top of OAuth 2.0.",
            },
            {
                "question": "Which JWT claim mismatch should cause the resource server to reject a token?",
                "options": ["iat", "jti", "aud (audience)", "none of these"],
                "correct_index": 2,
                "explanation": "A token minted for a different audience must be refused; iss and exp matter too.",
            },
            {
                "question": "The 'state' parameter in the OAuth authorization code flow protects against:",
                "options": ["Token expiry", "CSRF / authorization code injection", "Password brute force", "Scope escalation"],
                "correct_index": 1,
                "explanation": "state ties the redirect back to the originating request, blocking forged redirects.",
            },
            {
                "question": "A resource server accepts a JWT with alg=none and an unsigned payload. Severity?",
                "options": ["Cosmetic logging issue", "Medium performance issue", "Critical authentication bypass", "Low usability issue"],
                "correct_index": 2,
                "explanation": "Anyone can forge tokens — a textbook critical auth bypass.",
            },
        ],
    },
    {
        "id": "dlp-module",
        "title": "Module E: DLP (Data Loss Prevention)",
        "summary": (
            "DLP detects and blocks sensitive data leaving the organisation through email, "
            "uploads, clipboard, printing or storage. Testing DLP is testing policy enforcement "
            "and its accuracy: false negatives leak data, false positives block legitimate work."
        ),
        "concepts": [
            {
                "name": "Sensitive data classification",
                "explanation": (
                    "PII (names, addresses, national IDs), financial data (card numbers, account "
                    "numbers), health data, credentials, and internal-confidential documents. "
                    "Classification drives policy: what is restricted, who may touch it, where it "
                    "may go. Testing starts from the classification catalogue."
                ),
                "practical_example": (
                    "Test matrix: for each classification, one valid sample, one near-miss "
                    "(partially masked), and one obfuscated variant (spaces in a card number) — "
                    "detection must not rely on exact formatting."
                ),
            },
            {
                "name": "Channels & exfiltration",
                "explanation": (
                    "Email, web uploads, cloud storage, messaging, printing, USB, screenshots. "
                    "Each channel is a policy enforcement point. Exfiltration testing tries every "
                    "channel because attackers and users do."
                ),
                "practical_example": (
                    "Email a file with card numbers to an external address — blocked or flagged per "
                    "policy; upload the same file to a personal cloud drive — policy enforced; "
                    "print it — printer channel policy applies."
                ),
            },
            {
                "name": "Content vs context inspection",
                "explanation": (
                    "Content inspection reads the data (regex for card patterns, keyword lists, "
                    "ML classifiers, fingerprints of known documents). Context inspection looks at "
                    "metadata: recipient domain, file type, size, source application. "
                    "Strong DLP needs both: content says WHAT, context says WHERE/WHO."
                ),
                "practical_example": (
                    "Test: a card number sent to an internal address (allowed) vs the same number "
                    "to an external domain (blocked). Same content, different context, different "
                    "outcome — that pair proves context rules work."
                ),
            },
            {
                "name": "False positives & false negatives",
                "explanation": (
                    "A false negative leaks sensitive data (severe). A false positive blocks a "
                    "legitimate business email (visible, costly, erodes trust in the tool). "
                    "Both are defects you measure with a labelled test corpus and trend over time."
                ),
                "practical_example": (
                    "Corpus testing: 200 known-sensitive samples (expect block) + 200 benign "
                    "lookalikes (expect allow); report precision and recall per policy, and "
                    "compare across builds to catch regressions."
                ),
            },
            {
                "name": "Policy enforcement & fail modes",
                "explanation": (
                    "Actions: allow, quarantine, block, notify, encrypt, require justification. "
                    "What happens when the DLP service is down — fail-open (email flows, "
                    "uninspected) or fail-closed (email queued)? The documented policy is the "
                    "oracle; the actual behaviour is the test result."
                ),
                "practical_example": (
                    "Test: with the DLP engine unavailable, send sensitive email. If policy is "
                    "fail-closed, mail must queue; if fail-open, it must be logged and "
                    "retroactively scanned if the product claims that."
                ),
            },
        ],
        "architecture": (
            "Sender/endpoint\n"
            "      |\n"
            "  Channel: email / upload / USB / print / clipboard\n"
            "      |\n"
            "  Enforcement point (mail gateway, proxy, agent)\n"
            "      - content inspection (regex, keywords, fingerprints)\n"
            "      - context rules (recipient, size, classification)\n"
            "      |\n"
            "  Policy decision: allow | warn | encrypt | quarantine | block\n"
            "      |\n"
            "  Logging & analytics -> incident response\n"
        ),
        "interview_questions": [
            {
                "question": "How would you test a DLP system with no prior DLP experience?",
                "answer": (
                    "Honestly: I have not implemented DLP, but the testing pattern transfers "
                    "directly from IAM. IAM asks 'is this user allowed this entitlement'; DLP asks "
                    'is this data allowed through this channel". Both are policy engines with '
                    "enforcement points, and both are tested as positive/negative/boundary "
                    "matrices against a documented policy. So I would: (1) read the policy catalogue "
                    "as the test oracle, (2) build a labelled corpus of sensitive and benign "
                    "samples per classification, (3) test each channel with content and context "
                    "variants, (4) measure false positives and false negatives as a rate, not "
                    "anecdotes, and (5) test the failure modes — service down, tampering, and "
                    "policy bypasses like renaming or re-encoding files."
                ),
            },
            {
                "question": "A DLP rule blocks a legitimate business email containing customer data. How do you handle it as QA?",
                "answer": (
                    "That is a false positive: classify it (which rule fired, which pattern "
                    "matched), quantify how often it happens (corpus run), and drive either a rule "
                    "tuning or an explicit allow with justification per policy. QA's job is not to "
                    "decide the policy but to prove the rule behaves as designed, measure the rate, "
                    "and prevent regressions when rules change — a tuned rule must not silently "
                    "introduce false negatives, so I re-run the sensitive corpus after every tuning."
                ),
            },
            {
                "question": "Why is renaming a file not a reliable bypass defence, and how do you test that?",
                "answer": (
                    "Because content inspection reads the data, not the filename. A file renamed "
                    "from report.docx to notes.txt still contains card numbers, and a strong DLP "
                    "catches it. I test with a matrix: same content under different names, "
                    "different formats (docx to zip, xlsx to csv), split archives, and embedded "
                    "content (a spreadsheet inside a zip). Detection must follow content through "
                    "transformation; anything that depends only on extension is a finding."
                ),
            },
        ],
        "test_cases": [
            {
                "title": "External email with card numbers is blocked",
                "type": "negative",
                "steps": "Email a file containing valid-format card numbers to an external domain.",
                "expected": "Blocked or quarantined per policy; sender notified; incident logged.",
            },
            {
                "title": "Internal email with the same content follows policy",
                "type": "positive",
                "steps": "Send the same content to an internal recipient.",
                "expected": "Allowed (or encrypted per policy); behaviour differs from the external case.",
            },
            {
                "title": "Renamed and re-encoded file is still detected",
                "type": "boundary",
                "steps": "Rename sensitive.docx to notes.txt and re-zip it before uploading.",
                "expected": "Content inspection still detects and enforces policy.",
            },
            {
                "title": "Partially masked PII is still detected",
                "type": "boundary",
                "steps": "Send data with partial masking, e.g. ****-1234 or spaced card digits.",
                "expected": "Detection handles common obfuscation patterns per policy.",
            },
            {
                "title": "DLP service unavailable behaves per fail policy",
                "type": "boundary",
                "steps": "Stop the DLP engine and send sensitive email.",
                "expected": "Fail-closed queues the mail; fail-open logs and retro-scans if claimed.",
            },
        ],
        "quiz": [
            {
                "question": "The more dangerous DLP defect is:",
                "options": ["False positive", "False negative", "Slow dashboard", "Verbose logging"],
                "correct_index": 1,
                "explanation": "A false negative leaks sensitive data silently; false positives are at least visible.",
            },
            {
                "question": "Detection that survives renaming and re-zipping relies on:",
                "options": ["File extension checks", "Content inspection", "Filename length", "Network speed"],
                "correct_index": 1,
                "explanation": "Content inspection reads the data itself, not metadata like names or extensions.",
            },
            {
                "question": "'Fail-closed' for a mail gateway means:",
                "options": [
                    "Email flows uninspected when DLP is down",
                    "Email is queued/rejected when DLP is unavailable",
                    "Only encrypted email is blocked",
                    "Attachments are always stripped",
                ],
                "correct_index": 1,
                "explanation": "Fail-closed prioritises security over availability: nothing passes uninspected.",
            },
            {
                "question": "The same card number sent internally vs externally produces different outcomes because of:",
                "options": ["Content inspection", "Context inspection (recipient domain)", "Data classification of the file", "Load balancer routing"],
                "correct_index": 1,
                "explanation": "Context rules evaluate recipient, channel and metadata around the content.",
            },
        ],
    },
]


def list_modules() -> list[dict]:
    return [
        {
            "id": m["id"],
            "title": m["title"],
            "summary": m["summary"],
            "concept_count": len(m["concepts"]),
            "interview_question_count": len(m["interview_questions"]),
            "test_case_count": len(m["test_cases"]),
            "quiz_count": len(m["quiz"]),
        }
        for m in IAM_MODULES
    ]


def get_module(module_id: str) -> dict | None:
    for m in IAM_MODULES:
        if m["id"] == module_id:
            return m
    return None
