"""Clause builders shared by the audit log queries."""

DEFAULT_SORT = "ts"
DEFAULT_DIRECTION = "desc"


def quote_literal(value: str) -> str:
    """Return a value as a SQL string literal.

    Embedded single quotes are doubled, which is how SQLite escapes a quote
    inside a literal, so a value containing an apostrophe does not end the
    literal early.
    """
    return "'" + value.replace("'", "''") + "'"


def order_clause(sort: str, direction: str) -> str:
    """Return an ORDER BY clause for a column name and a direction."""
    return f" ORDER BY {sort} {direction}"
