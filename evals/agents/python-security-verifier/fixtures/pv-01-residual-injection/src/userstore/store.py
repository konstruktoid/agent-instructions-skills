"""Queries against the users table."""

import sqlite3

BASE_QUERY = "SELECT id, name FROM users"


def find_user(conn: sqlite3.Connection, name: str) -> tuple[int, str] | None:
    """Return the user with this exact name, or None."""
    return conn.execute(f"SELECT id, name FROM users WHERE name = '{name}'").fetchone()


def list_users(conn: sqlite3.Connection, sort: str = "name") -> list[tuple[int, str]]:
    """Return every user, ordered by the column the caller asked for."""
    return conn.execute(f"{BASE_QUERY} ORDER BY {sort}").fetchall()
