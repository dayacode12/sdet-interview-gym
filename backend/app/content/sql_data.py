"""SQL playground: IAM challenge bank, seed data and schema.

Execution safety model:
- Queries run against a SEPARATE in-memory SQLite database built from SEED_STATEMENTS,
  never against the application database.
- A read-only connection is enforced: the SQL is wrapped in a SELECT from a subquery,
  and PRAGMA query_only=1 blocks writes at the driver level.
- The application database credentials are never exposed to the browser.
"""
from __future__ import annotations

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE USERS (
        user_id     INTEGER PRIMARY KEY,
        username    TEXT NOT NULL,
        email       TEXT,
        department  TEXT,
        status      TEXT NOT NULL,
        manager_id  INTEGER
    )
    """,
    """
    CREATE TABLE ROLES (
        role_id        INTEGER PRIMARY KEY,
        role_name      TEXT NOT NULL,
        privilege_level INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE USER_ROLES (
        id            INTEGER PRIMARY KEY,
        user_id       INTEGER NOT NULL,
        role_id       INTEGER NOT NULL,
        assigned_date TEXT
    )
    """,
    """
    CREATE TABLE ACCESS_REQUESTS (
        request_id   INTEGER PRIMARY KEY,
        user_id      INTEGER NOT NULL,
        entitlement  TEXT NOT NULL,
        status       TEXT NOT NULL,
        approver_id  INTEGER,
        created_at   TEXT
    )
    """,
    """
    CREATE TABLE CERTIFICATIONS (
        certification_id INTEGER PRIMARY KEY,
        user_id          INTEGER NOT NULL,
        entitlement      TEXT NOT NULL,
        reviewer_id      INTEGER,
        decision         TEXT,
        campaign_id      TEXT
    )
    """,
    """
    CREATE TABLE PROVISIONING_LOGS (
        log_id           INTEGER PRIMARY KEY,
        user_id          INTEGER NOT NULL,
        application_name TEXT NOT NULL,
        operation        TEXT NOT NULL,
        status           TEXT NOT NULL,
        execution_time   TEXT
    )
    """,
]

SEED_USERS = [
    # user_id, username, email, department, status, manager_id
    (1, "daya.nidhi", "daya.nidhi@admiral.example", "QA Engineering", "ACTIVE", 7),
    (2, "ravi.kumar", "ravi.kumar@admiral.example", "QA Engineering", "ACTIVE", 7),
    (3, "meera.iyer", "meera.iyer@admiral.example", "Risk", "ACTIVE", 8),
    (4, "arun.patel", "arun.patel@admiral.example", "Claims", "INACTIVE", 8),
    (5, "sneha.reddy", "sneha.reddy@admiral.example", "Underwriting", "ACTIVE", 7),
    (6, "vikram.singh", "vikram.singh@admiral.example", "IT Operations", "TERMINATED", 7),
    (7, "priya.menon", "priya.menon@admiral.example", "QA Engineering", "ACTIVE", 9),
    (8, "deepak.rao", "deepak.rao@admiral.example", "Risk", "ACTIVE", 9),
    (9, "latha.krishnan", "latha.krishnan@admiral.example", "IT Operations", "ACTIVE", None),
    (10, "omar.faruk", "omar.faruk@admiral.example", "Claims", "TERMINATED", 8),
    (11, "kavya.shetty", "kavya.shetty@admiral.example", "Underwriting", "ACTIVE", 7),
    (12, "nikhil.joshi", "nikhil.joshi@admiral.example", "QA Engineering", "ACTIVE", 7),
    (13, "farah.khan", "farah.khan@admiral.example", "Risk", "ACTIVE", 8),
    (14, "sanjay.gupta", "sanjay.gupta@admiral.example", "Finance", "ACTIVE", None),
    (15, "rita.dsa", "rita.dsa@admiral.example", "Finance", "INACTIVE", 14),
    (16, "amit.verma", "amit.verma@admiral.example", "IT Operations", "ACTIVE", 9),
    (17, "ananya.bose", "ananya.bose@admiral.example", "Underwriting", "ACTIVE", 7),
    (18, "tarun.mehta", "tarun.mehta@admiral.example", "Claims", "ACTIVE", 8),
    (19, "sameer.ali", "sameer.ali@admiral.example", "QA Engineering", "ACTIVE", 7),
    (20, "nithya.raman", "nithya.raman@admiral.example", "Risk", "ACTIVE", 8),
    (21, "gsuresh.babu", "gsuresh.babu@admiral.example", "QA Engineering", "ACTIVE", 7),
    (22, "varsha.nair", "varsha.nair@admiral.example", "Underwriting", "ACTIVE", 7),
    (23, "harish.pillai", "harish.pillai@admiral.example", "IT Operations", "INACTIVE", 9),
    (24, "zeba.hussain", "zeba.hussain@admiral.example", "Finance", "ACTIVE", 14),
    (25, "dinesh.kumar", "dinesh.kumar@admiral.example", "Claims", "ACTIVE", 8),
    # duplicate username: reconciliation defect
    (26, "daya.nidhi", "daya.nidhi2@admiral.example", "QA Engineering", "ACTIVE", 7),
    # null email: data quality defect
    (27, "mohan.lal", None, "Underwriting", "ACTIVE", 7),
    (28, "tanya.kapoor", "tanya.kapoor@admiral.example", "Risk", "ACTIVE", 8),
]

SEED_ROLES = [
    # role_id, role_name, privilege_level (1 normal, 5 privileged, 10 admin)
    (1, "EMPLOYEE", 1),
    (2, "CLAIMS_HANDLER", 2),
    (3, "RISK_ANALYST", 3),
    (4, "UNDERWRITER", 3),
    (5, "QA_AUTOMATION", 2),
    (6, "DBA_ADMIN", 10),
    (7, "SYS_ADMIN", 10),
    (8, "SECURITY_AUDITOR", 5),
    (9, "FINANCE_VIEWER", 1),
    (10, "CIAM_SUPPORT", 5),
]

SEED_USER_ROLES = [
    # id, user_id, role_id, assigned_date
    (1, 1, 5, "2025-01-10"),
    (2, 1, 1, "2025-01-10"),
    (3, 2, 5, "2025-02-15"),
    (4, 2, 1, "2025-02-15"),
    (5, 3, 3, "2025-03-01"),
    (6, 4, 2, "2024-11-20"),   # INACTIVE user still holding role
    (7, 5, 4, "2025-04-05"),
    (8, 6, 7, "2024-06-30"),   # TERMINATED user with SYS_ADMIN
    (9, 6, 1, "2024-06-30"),   # TERMINATED user still holds EMPLOYEE
    (10, 7, 5, "2025-01-15"),
    (11, 7, 8, "2025-01-15"),  # two roles incl privileged
    (12, 8, 3, "2025-05-12"),
    (13, 9, 6, "2025-02-02"),  # active manager with DBA_ADMIN
    (14, 10, 2, "2024-08-08"), # TERMINATED user still holding role
    (15, 10, 7, "2024-08-08"), # TERMINATED with SYS_ADMIN
    (16, 11, 4, "2025-06-01"),
    (17, 12, 5, "2025-06-20"),
    (18, 13, 3, "2025-07-07"),
    (19, 14, 9, "2025-03-15"),
    (20, 15, 9, "2025-03-15"), # INACTIVE user still holding FINANCE_VIEWER
    (21, 16, 6, "2025-04-11"), # active user with DBA_ADMIN
    (22, 16, 7, "2025-04-11"), # same user ALSO SYS_ADMIN -> multiple privileged roles
    (23, 17, 4, "2025-08-19"),
    (24, 19, 5, "2025-08-02"),
    (25, 19, 8, "2025-08-02"), # QA user with SECURITY_AUDITOR
    (26, 20, 3, "2025-09-09"),
    (27, 21, 5, "2025-09-15"),
    (28, 23, 6, "2024-10-01"), # INACTIVE user still holding DBA_ADMIN
    (29, 24, 9, "2025-10-05"),
    (30, 25, 2, "2025-10-10"),
    (31, 26, 5, "2025-11-01"), # duplicate identity also got QA_AUTOMATION
    (32, 27, 4, "2025-11-02"),
    (33, 28, 3, "2025-11-03"),
    # orphaned assignment: role_id 99 does not exist
    (34, 18, 99, "2025-11-04"),
]

SEED_ACCESS_REQUESTS = [
    # request_id, user_id, entitlement, status, approver_id, created_at
    (101, 1, "FINANCE_VIEWER", "APPROVED", 7, "2025-10-01"),
    (102, 2, "SECURITY_AUDITOR", "REJECTED", 7, "2025-10-02"),
    (103, 3, "RISK_ANALYST_PLUS", "PENDING", 8, "2025-10-03"),
    (104, 4, "CLAIMS_HANDLER", "PENDING", 8, "2025-09-20"),   # > 7 days pending
    (105, 5, "UNDERWRITER_SENIOR", "PENDING", 7, "2025-11-05"),
    (106, 6, "SYS_ADMIN", "APPROVED", None, "2025-08-30"),    # terminated user APPROVED admin
    (107, 7, "DBA_ADMIN", "PENDING", 9, "2025-11-06"),
    (108, 8, "RISK_ANALYST_PLUS", "PENDING", 9, "2025-10-10"),
    (109, 10, "CIAM_SUPPORT", "APPROVED", None, "2025-08-31"),# terminated user approved privileged
    (110, 11, "UNDERWRITER_SENIOR", "REJECTED", 7, "2025-10-15"),
    (111, 12, "CIAM_SUPPORT", "PENDING", 9, "2025-09-28"),
    (112, 13, "RISK_ANALYST_PLUS", "APPROVED", 8, "2025-10-18"),
    (113, 15, "FINANCE_VIEWER", "PENDING", 14, "2025-09-25"),
    (114, 16, "SECURITY_AUDITOR", "APPROVED", 9, "2025-10-20"),
    (115, 18, "CLAIMS_HANDLER", "PENDING", 8, "2025-11-07"),
    (116, 19, "DBA_ADMIN", "PENDING", 7, "2025-10-08"),
    (117, 21, "QA_LEAD", "PENDING", 7, "2025-11-08"),
    (118, 22, "UNDERWRITER_SENIOR", "APPROVED", 7, "2025-10-22"),
    (119, 24, "FINANCE_VIEWER", "PENDING", 14, "2025-10-25"),
    (120, 25, "CLAIMS_HANDLER", "REJECTED", 8, "2025-10-26"),
    (121, 26, "SECURITY_AUDITOR", "APPROVED", 7, "2025-11-09"),  # duplicate identity approved
    (122, 28, "RISK_ANALYST_PLUS", "PENDING", 8, "2025-10-29"),
]

SEED_CERTIFICATIONS = [
    # certification_id, user_id, entitlement, reviewer_id, decision, campaign_id
    (201, 1, "QA_AUTOMATION", 7, "CONFIRM", "CAMP-2025-Q4"),
    (202, 1, "EMPLOYEE", 7, "CONFIRM", "CAMP-2025-Q4"),
    (203, 2, "QA_AUTOMATION", 7, "CONFIRM", "CAMP-2025-Q4"),
    (204, 2, "EMPLOYEE", 7, "REVOKE", "CAMP-2025-Q4"),      # revoked...
    (205, 3, "RISK_ANALYST", 8, "CONFIRM", "CAMP-2025-Q4"),
    (206, 4, "CLAIMS_HANDLER", 8, "REVOKE", "CAMP-2025-Q4"),# revoked but role still assigned
    (207, 6, "SYS_ADMIN", 9, "REVOKE", "CAMP-2025-Q4"),     # revoked but role still assigned
    (208, 7, "SECURITY_AUDITOR", 9, "CONFIRM", "CAMP-2025-Q4"),
    (209, 8, "RISK_ANALYST", 9, "CONFIRM", "CAMP-2025-Q4"),
    (210, 10, "CIAM_SUPPORT", 9, "REVOKE", "CAMP-2025-Q4"),  # revoked, no role row (good)
    (211, 16, "DBA_ADMIN", 9, "REVOKE", "CAMP-2025-Q4"),     # revoked but role still assigned
    (212, 19, "QA_AUTOMATION", 7, "CONFIRM", "CAMP-2025-Q4"),
    (213, 23, "DBA_ADMIN", 9, None, "CAMP-2025-Q4"),        # overdue: no decision
    (214, 24, "FINANCE_VIEWER", 14, "CONFIRM", "CAMP-2025-Q4"),
    (215, 25, "CLAIMS_HANDLER", 8, None, "CAMP-2025-Q4"),    # overdue: no decision
]

SEED_PROVISIONING_LOGS = [
    # log_id, user_id, application_name, operation, status, execution_time
    (301, 1, "Jira", "CREATE_ACCOUNT", "SUCCESS", "2025-10-01 08:00"),
    (302, 1, "Confluence", "CREATE_ACCOUNT", "SUCCESS", "2025-10-01 08:01"),
    (303, 2, "Jira", "CREATE_ACCOUNT", "SUCCESS", "2025-10-02 09:00"),
    (304, 3, "ServiceNow", "CREATE_ACCOUNT", "FAILED", "2025-10-03 10:00"),
    (305, 4, "Salesforce", "DISABLE_ACCOUNT", "FAILED", "2025-10-04 11:00"),  # inactive user, failed disable
    (306, 6, "Salesforce", "DISABLE_ACCOUNT", "FAILED", "2025-10-05 12:00"),   # terminated user, failed disable
    (307, 6, "CyberArk", "REVOKE_PRIVILEGED", "FAILED", "2025-10-05 12:01"),   # terminated, failed revoke
    (308, 7, "Jira", "CREATE_ACCOUNT", "SUCCESS", "2025-10-06 13:00"),
    (309, 8, "ServiceNow", "CREATE_ACCOUNT", "SUCCESS", "2025-10-07 14:00"),
    (310, 10, "Salesforce", "DISABLE_ACCOUNT", "FAILED", "2025-10-08 15:00"),  # terminated, failed disable
    (311, 11, "Confluence", "CREATE_ACCOUNT", "SUCCESS", "2025-10-09 16:00"),
    (312, 12, "Jira", "CREATE_ACCOUNT", "SUCCESS", "2025-10-10 17:00"),
    (313, 16, "CyberArk", "GRANT_PRIVILEGED", "SUCCESS", "2025-10-11 18:00"),
    (314, 18, "Salesforce", "CREATE_ACCOUNT", "FAILED", "2025-10-12 19:00"),
    (315, 19, "Jira", "CREATE_ACCOUNT", "SUCCESS", "2025-10-13 20:00"),
    (316, 23, "CyberArk", "REVOKE_PRIVILEGED", "FAILED", "2025-10-14 21:00"),  # inactive user, failed revoke
    (317, 26, "Jira", "CREATE_ACCOUNT", "SUCCESS", "2025-11-01 08:00"),        # duplicate identity provisioned
    (318, 27, "Confluence", "CREATE_ACCOUNT", "SUCCESS", "2025-11-02 08:00"),
    (319, 28, "ServiceNow", "CREATE_ACCOUNT", "SUCCESS", "2025-11-03 08:00"),
]


# Data dictionary for the UI (describes the sandbox — no credentials involved).
TABLE_COLUMNS = {
    "USERS": [
        ("user_id", "INTEGER PK"),
        ("username", "TEXT"),
        ("email", "TEXT, nullable (defects seeded)"),
        ("department", "TEXT"),
        ("status", "ACTIVE | INACTIVE | TERMINATED"),
        ("manager_id", "INTEGER, self-reference"),
    ],
    "ROLES": [
        ("role_id", "INTEGER PK"),
        ("role_name", "TEXT"),
        ("privilege_level", "INTEGER, >= 10 is administrative"),
    ],
    "USER_ROLES": [
        ("id", "INTEGER PK"),
        ("user_id", "FK USERS"),
        ("role_id", "FK ROLES (role_id 99 is an orphan, seeded defect)"),
        ("assigned_date", "TEXT"),
    ],
    "ACCESS_REQUESTS": [
        ("request_id", "INTEGER PK"),
        ("user_id", "FK USERS"),
        ("entitlement", "TEXT"),
        ("status", "PENDING | APPROVED | REJECTED"),
        ("approver_id", "FK USERS, nullable"),
        ("created_at", "TEXT date"),
    ],
    "CERTIFICATIONS": [
        ("certification_id", "INTEGER PK"),
        ("user_id", "FK USERS"),
        ("entitlement", "TEXT"),
        ("reviewer_id", "FK USERS, nullable"),
        ("decision", "CERTIFIED | REVOKED | NULL"),
        ("campaign_id", "TEXT"),
    ],
    "PROVISIONING_LOGS": [
        ("log_id", "INTEGER PK"),
        ("user_id", "FK USERS"),
        ("application_name", "TEXT"),
        ("operation", "CREATE_ACCOUNT | MODIFY | DISABLE | REVOKE"),
        ("status", "SUCCESS | FAILED"),
        ("execution_time", "TEXT timestamp"),
    ],
}


def build_seed_statements() -> list[tuple[str, list]]:
    """Return (sql, params) pairs to initialise the sandbox database."""
    stmts: list[tuple[str, list]] = [(s.strip(), []) for s in SCHEMA_STATEMENTS]
    stmts.append(("INSERT INTO USERS VALUES (?,?,?,?,?,?)", SEED_USERS))
    stmts.append(("INSERT INTO ROLES VALUES (?,?,?)", SEED_ROLES))
    stmts.append(("INSERT INTO USER_ROLES VALUES (?,?,?,?)", SEED_USER_ROLES))
    stmts.append(("INSERT INTO ACCESS_REQUESTS VALUES (?,?,?,?,?,?)", SEED_ACCESS_REQUESTS))
    stmts.append(("INSERT INTO CERTIFICATIONS VALUES (?,?,?,?,?,?)", SEED_CERTIFICATIONS))
    stmts.append(("INSERT INTO PROVISIONING_LOGS VALUES (?,?,?,?,?,?)", SEED_PROVISIONING_LOGS))
    return stmts
