"""Cache refresh."""

from .client import fetch

CACHE: dict[int, dict] = {}


def sync_all() -> None:
    """Refresh every cached user."""
    for user_id in list(CACHE):
        CACHE[user_id] = fetch(user_id)
