"""Weekday, weekend and holiday helpers."""

import datetime

SATURDAY = 5

# Company holidays, as ISO dates.
HOLIDAYS = [
    "2026-07-22",
    "2026-12-25",
]


def is_weekend(day: datetime.date) -> bool:
    """Return True when the date falls on a Saturday or Sunday."""
    return day.weekday() >= SATURDAY


def is_holiday(day: datetime.date) -> bool:
    """Return True when the date is a company holiday."""
    return day in HOLIDAYS


def days_between(start: datetime.date, end: datetime.date) -> int:
    """Return the number of days from start to end, counting both ends."""
    return (end - start).days + 1


def next_weekday(day: datetime.date) -> datetime.date:
    """Return the first weekday on or after the given date."""
    while is_weekend(day):
        day += datetime.timedelta(days=1)
    return day
