"""SQL sandbox security and grading behaviour."""
from __future__ import annotations

import pytest

from app.services import sql_runner


def test_select_allowed():
    result = sql_runner.run_query("SELECT username FROM USERS WHERE status = 'ACTIVE' ORDER BY username")
    assert result["row_count"] > 0
    assert result["columns"] == ["username"]


def test_with_cte_allowed():
    result = sql_runner.run_query(
        "WITH admin_roles AS (SELECT role_id FROM ROLES WHERE privilege_level >= 10) "
        "SELECT COUNT(*) AS n FROM admin_roles"
    )
    assert result["row_count"] == 1


def test_write_statements_blocked():
    for bad in [
        "DELETE FROM USERS",
        "DROP TABLE USERS",
        "INSERT INTO USERS VALUES (1, 'x', 'x', 'IT', 'ACTIVE', NULL)",
        "UPDATE USERS SET status = 'ACTIVE'",
        "CREATE TABLE evil (x INTEGER)",
        "ALTER TABLE USERS ADD COLUMN evil TEXT",
        "ATTACH DATABASE 'x' AS x",
        "PRAGMA query_only = 0",
    ]:
        with pytest.raises(sql_runner.SqlExecutionError):
            sql_runner.run_query(bad)


def test_keywords_inside_literals_do_not_block():
    """A string literal containing 'delete' must not block a SELECT."""
    result = sql_runner.run_query(
        "SELECT COUNT(*) AS n FROM USERS WHERE department = 'delete me'"
    )
    assert result["row_count"] == 1


def test_empty_query_rejected():
    with pytest.raises(sql_runner.SqlExecutionError):
        sql_runner.run_query("   ")


def test_write_blocked_via_tricks():
    with pytest.raises(sql_runner.SqlExecutionError):
        sql_runner.run_query("select * from users; drop table users")


def test_row_limit_truncates():
    result = sql_runner.run_query("SELECT user_id FROM USERS", limit=5)
    assert result["row_count"] == 5
    assert result["truncated"]
