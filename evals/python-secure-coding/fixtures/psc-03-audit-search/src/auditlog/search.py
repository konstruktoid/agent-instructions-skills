"""Search the audit log."""

import argparse
import sqlite3

DB_PATH = "audit.db"


def connect() -> sqlite3.Connection:
    """Open the audit database."""
    return sqlite3.connect(DB_PATH)


def search(actor: str, action: str) -> list:
    """Return audit rows for one actor and action."""
    query = (
        "SELECT id, actor, action, target, ts FROM audit "
        "WHERE actor = '" + actor + "' AND action = '" + action + "'"
    )
    with connect() as connection:
        return connection.execute(query).fetchall()


def main() -> None:
    """Parse arguments and print matching audit rows."""
    parser = argparse.ArgumentParser(description="Search the audit log")
    parser.add_argument("--actor", required=True)
    parser.add_argument("--action", required=True)
    args = parser.parse_args()
    for row in search(args.actor, args.action):
        print(row)


if __name__ == "__main__":
    main()
