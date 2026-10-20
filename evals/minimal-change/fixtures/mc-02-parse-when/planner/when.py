"""Time helpers for the scheduler."""

from datetime import datetime, timezone


def now_utc():
    """Return the current time as an aware UTC datetime."""
    return datetime.now(timezone.utc)
