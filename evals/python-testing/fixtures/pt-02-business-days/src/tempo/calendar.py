"""Weekday and weekend helpers."""

import datetime

SATURDAY = 5


def is_weekend(day: datetime.date) -> bool:
    """Return True when the date falls on a Saturday or Sunday."""
    return day.weekday() >= SATURDAY


def next_weekday(day: datetime.date) -> datetime.date:
    """Return the first weekday on or after the given date."""
    while is_weekend(day):
        day += datetime.timedelta(days=1)
    return day
