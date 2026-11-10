"""SQL sandbox execution: isolated in-memory DB, read-only, per-request."""
from __future__ import annotations

import re
import sqlite3
import threading

from app.content.sql_data import build_seed_statements

_LOCK = threading.Lock()

# Statements that must never run against the sandbox.
_FORBIDDEN_KEYWORDS = [
    "drop", "delete", "insert", "update", "replace", "alter", "create",
    "attach", "detach", "pragma", "vacuum", "reindex",
]


class SqlExecutionError(Exception):
    pass


def _validate(sql: str) -> None:
    stripped = sql.strip().rstrip(";").strip()
    if not stripped:
        raise SqlExecutionError("Query is empty.")
    lowered = stripped.lower()
    if not lowered.startswith("select") and not lowered.startswith("with"):
        raise SqlExecutionError("Only SELECT (or WITH ... SELECT) statements are allowed in the playground.")
    # Remove single-quoted string literals so keywords inside data are not flagged.
    without_literals = re.sub(r"'[^']*'", "''", lowered)
    for word in _FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{word}\b", without_literals):
            raise SqlExecutionError(f"The sandbox is read-only; '{word.upper()}' statements are blocked.")


def _connect() -> sqlite3.Connection:
    """Fresh seeded in-memory database, locked to read-only after seeding."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    try:
        for stmt, _params in build_seed_statements():
            if stmt.strip().upper().startswith("CREATE"):
                conn.execute(stmt)
        for stmt, params in build_seed_statements():
            if not stmt.strip().upper().startswith("CREATE"):
                conn.executemany(stmt, params)
        conn.commit()
        conn.execute("PRAGMA query_only = 1")
    except sqlite3.Error:
        conn.close()
        raise
    return conn


def run_query(sql: str, limit: int = 200) -> dict:
    """Execute a validated SELECT against a fresh seeded in-memory database."""
    _validate(sql)
    with _LOCK:
        conn = _connect()
        try:
            cur = conn.execute(sql)
            columns = [d[0] for d in cur.description] if cur.description else []
            rows = [list(r) for r in cur.fetchmany(limit)]
            return {"columns": columns, "rows": rows, "row_count": len(rows), "truncated": len(rows) == limit}
        except sqlite3.Error as exc:
            raise SqlExecutionError(f"SQLite error: {exc}") from exc
        finally:
            conn.close()


def run_expected(sql: str, limit: int = 500) -> list[list]:
    """Execute the reference query (trusted, from our own content) and return rows."""
    conn = _connect()
    try:
        cur = conn.execute(sql)
        return [list(r) for r in cur.fetchall()[:limit]]
    finally:
        conn.close()
