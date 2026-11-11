"""SQL -> English translator: deterministic, offline, rule-based.

This is deliberately NOT an LLM. The query is parsed on the server into an
AST (sqlglot, SQLite dialect - the same engine the sandbox executes) and
each clause is mapped to plain English, plus a beginner "basics" layer that
explains what tables, columns, fields, rows, joins and aliases ARE using the
query's own names as the examples. Honest limits:

- Only SELECT / WITH ... SELECT / set operations are explained — the only
  statements the read-only sandbox runs anyway.
- Complex expressions are quoted verbatim inside the clause text rather
  than paraphrased, so the translation can never invent meaning.
- Explaining a query never executes it and stores nothing.
"""
from __future__ import annotations

import sqlglot
from sqlglot import exp

# How deep to recurse into set operations (UNION sides) before summarising
# the side with its one-line summary instead of clause-by-clause.
_MAX_DEPTH = 2

_JOIN_MEANING = {
    "": "only rows that match on both sides are kept",
    "inner": "only rows that match on both sides are kept",
    "left": "all rows from the left table are kept even without a match",
    "right": "all rows from the right table are kept even without a match",
    "full": "rows from both tables are kept even without a match",
    "cross": "every row of the left table is paired with every row of the right table",
}

_AGG_WORDS = {
    "count": "the number of rows",
    "sum": "the total",
    "avg": "the average",
    "min": "the smallest value",
    "max": "the largest value",
}


class SqlExplainError(Exception):
    """Raised for input the translator honestly refuses to explain."""


def _sql(node: exp.Expression) -> str:
    return node.sql(dialect="sqlite")


def _list(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def _distinct_arg(arg: exp.Expression) -> str:
    """SQL fragment inside DISTINCT, or '' if the arg is not a Distinct."""
    if isinstance(arg, exp.Distinct):
        cols = [c.sql(dialect="sqlite") for c in (arg.expressions or ([arg.this] if arg.this else []))]
        return ", ".join(cols) if cols else "values"
    return ""


def _describe_projection(node: exp.Expression) -> str:
    """One column/aggregate in the SELECT list, in English."""
    if isinstance(node, exp.Star):
        return "all columns (*)"
    if isinstance(node, exp.Alias):
        return f"{_describe_projection(node.this)} (shown as {node.alias})"
    if isinstance(node, exp.Count):
        distinct_cols = _distinct_arg(node.this)
        if distinct_cols:
            return f"the number of distinct {distinct_cols} values"
        if isinstance(node.this, exp.Star) or node.this is None:
            return "the number of rows"
        return f"the number of rows where {_sql(node.this)} is not null"
    if isinstance(node, (exp.Sum, exp.Avg, exp.Min, exp.Max)):
        word = _AGG_WORDS.get(type(node).__name__.lower(), "an aggregate of")
        distinct_cols = _distinct_arg(node.this)
        if distinct_cols:
            return f"{word} of distinct {distinct_cols}"
        return f"{word} of {_sql(node.this)}"
    if isinstance(node, exp.Column):
        return _sql(node)
    return _sql(node)


def _join_kind(join: exp.Join) -> str:
    side = (join.side or "").upper()
    kind = (join.kind or "").upper()
    label = side or kind or "INNER"
    return (side or kind or "").lower()


def _with_clause(with_node: exp.With) -> dict | None:
    """English clause describing the CTEs of a WITH node."""
    ctes = list(with_node.expressions)
    if not ctes:
        return None
    parts = [f"{cte.alias} = ({_sql(cte.this)})" for cte in ctes]
    return {
        "label": "WITH",
        "text": f"Defines {len(ctes)} named subquer{'y' if len(ctes) == 1 else 'ies'} used later in the query: "
        + "; ".join(parts),
    }


def _select_clauses(select: exp.Select) -> list[dict]:
    clauses: list[dict] = []

    # WITH (CTEs)
    with_node = select.find(exp.With)
    if with_node is not None:
        clause = _with_clause(with_node)
        if clause is not None:
            clauses.append(clause)

    # SELECT list
    projections = select.expressions
    if projections:
        distinct = select.args.get("distinct") is not None
        cols = _list([_describe_projection(p) for p in projections])
        text = ("Returns unique combinations of " if distinct else "Returns ") + cols
        clauses.append({"label": "SELECT", "text": text})

    # FROM
    from_node = select.args.get("from_")
    if from_node is not None and isinstance(from_node.this, exp.Table):
        table = from_node.this
        alias = f" (aliased as {table.alias})" if table.alias else ""
        clauses.append({"label": "FROM", "text": f"Reads from table {table.name}{alias}"})
    elif from_node is not None:
        inner = from_node.this
        text = _sql(inner)
        if not isinstance(inner, (exp.Subquery, exp.Values)):
            text = f"({text})"
        clauses.append({"label": "FROM", "text": f"Reads from a subquery: {text}"})

    # JOINs
    for join in select.args.get("joins") or []:
        target = join.this
        name = getattr(target, "name", _sql(target))
        alias = f" (aliased as {target.alias})" if getattr(target, "alias", None) else ""
        on = join.args.get("on")
        on_text = f", matching rows where {_sql(on)}" if on is not None else ""
        kind = _join_kind(join)
        meaning = _JOIN_MEANING.get(kind, "rows are combined by this join")
        clauses.append(
            {"label": (kind or "inner").upper() + " JOIN", "text": f"Joins with {name}{alias}{on_text} - {meaning}"}
        )

    # WHERE
    where = select.args.get("where")
    if where is not None:
        condition = where.this
        ands = len(list(condition.find_all(exp.And)))
        ors = len(list(condition.find_all(exp.Or)))
        extra = ""
        if ands >= 2:
            extra = f" ({ands + 1} conditions combined with AND)"
        elif ors >= 2:
            extra = f" ({ors + 1} alternatives combined with OR)"
        clauses.append({"label": "WHERE", "text": f"Keeps only rows where {_sql(condition)}{extra}"})

    # GROUP BY
    group = select.args.get("group")
    if group is not None:
        cols = _list([_sql(g) for g in group.expressions])
        clauses.append({"label": "GROUP BY", "text": f"Groups rows by {cols} - one result row per group"})

    # HAVING
    having = select.args.get("having")
    if having is not None:
        clauses.append({"label": "HAVING", "text": f"Keeps only groups where {_sql(having.this)}"})

    # ORDER BY
    order = select.args.get("order")
    if order is not None:
        parts = []
        for ordered in order.expressions:
            direction = "descending" if ordered.args.get("desc") else "ascending"
            parts.append(f"{_sql(ordered.this)} {direction}")
        clauses.append({"label": "ORDER BY", "text": f"Sorts the results by {_list(parts)}"})

    # LIMIT / OFFSET
    limit = select.args.get("limit")
    offset = select.args.get("offset")
    if limit is not None:
        clauses.append({"label": "LIMIT", "text": f"Limits the result to at most {_sql(limit.expression)} rows"})
    if offset is not None:
        clauses.append({"label": "OFFSET", "text": f"Skips the first {_sql(offset.expression)} rows"})

    return clauses


def _select_summary(select: exp.Select, clauses: list[dict]) -> str:
    """One flowing sentence assembled from the clause list."""
    parts: list[str] = []
    for c in clauses:
        label, text = c["label"], c["text"]
        if label == "FROM":
            parts.append(text.replace("Reads from", "reads"))
        elif label == "SELECT":
            continue  # covered by the final "returns ..." assembly below
        else:
            t = text[0].lower() + text[1:] if text else text
            parts.append(t)
    # Lead with what is returned.
    projections = select.expressions
    distinct = select.args.get("distinct") is not None
    if projections:
        cols = _list([_describe_projection(p) for p in projections])
        head = ("Returns unique combinations of " if distinct else "Returns ") + cols
    else:
        head = "Returns rows"
    body = ", ".join(parts)
    sentence = head + (f"; {body}" if body else "")
    return sentence.rstrip(".") + "."


def _explain_set_operation(node: exp.Expression, depth: int) -> tuple[str, list[dict]]:
    """UNION / UNION ALL / EXCEPT / INTERSECT — explain both sides."""
    op = type(node).__name__.upper()
    distinct = bool(node.args.get("distinct"))
    keep_word = "removes duplicates" if distinct else "keeps duplicates"
    left_summary, left_clauses = _explain_node(node.this, depth + 1)
    right_summary, right_clauses = _explain_node(node.expression, depth + 1)
    summary = f"Stacks the results of two queries ({op} {keep_word}): first {left_summary} Second, {right_summary}"
    clauses: list[dict] = []

    # A WITH attached to the set operation itself (sqlglot stores it in
    # args["with_"] on the top-level node, not on either SELECT side).
    with_node = node.args.get("with_")
    if isinstance(with_node, exp.With):
        clause = _with_clause(with_node)
        if clause is not None:
            clauses.append(clause)
            summary = f"{clause['text']} Then it {summary[0].lower() + summary[1:]}"

    clauses += [
        {"label": op, "text": f"Combines the result rows of the two queries below and {keep_word}."},
        {"label": "QUERY 1", "text": left_summary},
        {"label": "QUERY 2", "text": right_summary},
    ]
    if depth + 1 < _MAX_DEPTH:
        clauses += [{"label": f"Q1 {c['label']}", "text": c["text"]} for c in left_clauses]
        clauses += [{"label": f"Q2 {c['label']}", "text": c["text"]} for c in right_clauses]
    return summary, clauses


def _explain_node(node: exp.Expression, depth: int) -> tuple[str, list[dict]]:
    if isinstance(node, exp.Select):
        clauses = _select_clauses(node)
        return _select_summary(node, clauses), clauses
    if isinstance(node, (exp.Union, exp.Except, exp.Intersect)):
        return _explain_set_operation(node, depth)
    # Anything else (VALUES, table-less SELECT, ...) — honest fallback.
    return f"Runs: {_sql(node)}", [{"label": type(node).__name__.upper(), "text": _sql(node)}]


_AGG_MEANING = {
    "count": "counts the rows",
    "sum": "adds the values together",
    "avg": "averages the values",
    "min": "finds the smallest value",
    "max": "finds the largest value",
}


def _basics(tree: exp.Expression) -> list[dict]:
    """Beginner layer: what a table, column, field, row, join and alias ARE -
    each definition grounded in the actual tables and columns of this query,
    so the explanation teaches vocabulary with the user's own query as the example."""
    basics: list[dict] = []
    selects = list(tree.find_all(exp.Select))

    # Tables + their nicknames.
    tables: list[str] = []
    table_aliases: list[str] = []
    for t in tree.find_all(exp.Table):
        if t.name and t.name not in tables:
            tables.append(t.name)
        if t.alias and t.name and f"{t.alias}={t.name}" not in table_aliases:
            table_aliases.append(f"'{t.alias}' is a nickname for the table {t.name}")
    if tables:
        basics.append(
            {
                "term": "Table",
                "text": "A table stores data like a spreadsheet: many rows that all have the same columns. "
                f"This query reads: {', '.join(tables)}.",
            }
        )

    # Columns (the attributes named in the query).
    columns: list[str] = []
    for col in tree.find_all(exp.Column):
        s = _sql(col)
        if s not in columns:
            columns.append(s)
    if columns:
        shown = ", ".join(columns[:8]) + ("..." if len(columns) > 8 else "")
        basics.append(
            {
                "term": "Column",
                "text": "A column is one attribute that every row of a table has - like username or status. "
                f"Columns this query uses: {shown}.",
            }
        )
        basics.append(
            {
                "term": "Field",
                "text": "A field is one single value: where one column meets one row. "
                f"For example, the {columns[0]} value of one specific record.",
            }
        )

    # Rows, grounded by grouping / limit when present.
    row_ground = "one row for every record that passes the filters"
    sel = tree if isinstance(tree, exp.Select) else (selects[0] if selects else None)
    if sel is not None:
        if sel.args.get("group") is not None:
            row_ground = "one row per group after grouping"
        limit = sel.args.get("limit")
        if limit is not None:
            row_ground += f" - at most {_sql(limit.expression)} in total"
    basics.append(
        {
            "term": "Row (record)",
            "text": f"A row is one record: one user, one request. This query returns {row_ground}.",
        }
    )

    # Joined columns.
    joins = [j for s in selects for j in (s.args.get("joins") or [])]
    if joins:
        on_parts: list[str] = []
        join_cols: list[str] = []
        for j in joins:
            on = j.args.get("on")
            if on is None:
                continue
            on_parts.append(_sql(on))
            for c in on.find_all(exp.Column):
                if _sql(c) not in join_cols:
                    join_cols.append(_sql(c))
        if join_cols:
            basics.append(
                {
                    "term": "Joined columns",
                    "text": "A join connects two tables by matching values in shared columns - a row from each "
                    f"table pairs up when those columns are equal. Joined columns here: {', '.join(join_cols)}.",
                }
            )

    # Aliases: table nicknames and named computed columns.
    col_aliases: list[str] = []
    for s in selects:
        for p in s.expressions:
            if isinstance(p, exp.Alias):
                col_aliases.append(f"'{p.alias}' is the name given to the computed column {_sql(p.this)}")
    if table_aliases or col_aliases:
        parts = (table_aliases + col_aliases)[:6]
        basics.append(
            {
                "term": "Variable (alias)",
                "text": "An alias works like a variable name in code: a nickname that makes the query shorter. "
                f"It never changes the data. Here: {'; '.join(parts)}{'...' if len(table_aliases) + len(col_aliases) > 6 else ''}.",
            }
        )

    # Aggregate functions.
    aggs: list[str] = []
    for node in tree.find_all(exp.Count, exp.Sum, exp.Avg, exp.Min, exp.Max):
        word = _AGG_MEANING.get(type(node).__name__.lower(), "combines many rows into one value")
        entry = f"{_sql(node)} {word}"
        if entry not in aggs:
            aggs.append(entry)
    if aggs:
        shown = "; ".join(aggs[:4]) + ("..." if len(aggs) > 4 else "")
        basics.append(
            {
                "term": "Aggregate function",
                "text": f"An aggregate squashes many rows into one value. Used here: {shown}.",
            }
        )

    # Conditions.
    wheres = [s.args.get("where") for s in selects if s.args.get("where") is not None]
    if wheres:
        basics.append(
            {
                "term": "Condition (WHERE)",
                "text": f"A condition is a test every row must pass to be kept. This query keeps only rows where {_sql(wheres[0].this)}.",
            }
        )

    return basics


def explain(sql: str) -> dict:
    """Translate one SQL statement into English. Raises SqlExplainError on
    input the translator honestly cannot handle."""
    stripped = (sql or "").strip().rstrip(";").strip()
    if not stripped:
        raise SqlExplainError("Query is empty.")

    try:
        tree = sqlglot.parse_one(stripped, read="sqlite")
    except sqlglot.errors.ParseError as exc:
        raise SqlExplainError(f"This query could not be parsed as SQLite: {str(exc).splitlines()[0]}") from exc

    if not isinstance(tree, (exp.Select, exp.Union, exp.Except, exp.Intersect)):
        raise SqlExplainError(
            "Only SELECT statements (optionally with WITH / UNION / EXCEPT / INTERSECT) are explained here."
        )

    summary, clauses = _explain_node(tree, 0)

    tables: list[str] = []
    for table_node in tree.find_all(exp.Table):
        name = table_node.name
        if name and name not in tables:
            tables.append(name)

    subqueries = len(list(tree.find_all(exp.Subquery)))

    notes = [
        "Deterministic translator: your query is parsed on the server (sqlglot, SQLite dialect) - "
        "not an AI, nothing is executed, nothing is stored."
    ]
    if subqueries:
        notes.append(
            f"Contains {subqueries} nested SELECT{'s' if subqueries != 1 else ''} - shown verbatim inside the clause text."
        )

    return {
        "statement": type(tree).__name__.upper(),
        "summary": summary,
        "clauses": clauses,
        "basics": _basics(tree),
        "tables": tables,
        "subqueries": subqueries,
        "notes": notes,
    }
