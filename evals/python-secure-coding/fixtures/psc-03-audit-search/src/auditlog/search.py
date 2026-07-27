"""Search the audit log."""

import argparse
import sqlite3

from auditlog.filters import DEFAULT_DIRECTION, DEFAULT_SORT, order_clause, quote_literal

DB_PATH = "audit.db"

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS audit ("
    "id INTEGER PRIMARY KEY, actor TEXT, action TEXT, target TEXT, ts TEXT)"
)


def connect() -> sqlite3.Connection:
    """Open the audit database, creating the table on first use."""
    connection = sqlite3.connect(DB_PATH)
    connection.execute(SCHEMA)
    return connection


def search(
    actor: str,
    action: str,
    sort: str = DEFAULT_SORT,
    direction: str = DEFAULT_DIRECTION,
) -> list:
    """Return audit rows for one actor and action."""
    query = (
        "SELECT id, actor, action, target, ts FROM audit "
        "WHERE actor = " + quote_literal(actor) + " AND action = " + quote_literal(action)
    )
    query += order_clause(sort, direction)
    with connect() as connection:
        return connection.execute(query).fetchall()


def main() -> None:
    """Parse arguments and print matching audit rows."""
    parser = argparse.ArgumentParser(description="Search the audit log")
    parser.add_argument("--actor", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--sort", default=DEFAULT_SORT)
    parser.add_argument("--direction", default=DEFAULT_DIRECTION)
    args = parser.parse_args()
    for row in search(args.actor, args.action, args.sort, args.direction):
        print(row)


if __name__ == "__main__":
    main()
