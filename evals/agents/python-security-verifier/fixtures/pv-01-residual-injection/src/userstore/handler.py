"""Map web query parameters onto store queries."""

import sqlite3

from userstore.store import find_user, list_users


def handle(conn: sqlite3.Connection, params: dict[str, str]) -> object:
    """Answer one request: a lookup when `name` is given, otherwise a sorted listing."""
    if "name" in params:
        return find_user(conn, params["name"])
    return list_users(conn, sort=params.get("sort", "name"))
