"""Tests for tempo.calendar."""

import datetime

import pytest
from tempo import is_weekend, next_weekday

MONDAY = datetime.date(2026, 7, 20)
SATURDAY = datetime.date(2026, 7, 25)
SUNDAY = datetime.date(2026, 7, 26)


@pytest.mark.parametrize(
    ("day", "expected"),
    [(MONDAY, False), (SATURDAY, True), (SUNDAY, True)],
)
def test_is_weekend(day, expected):
    """Saturday and Sunday are weekend days."""
    assert is_weekend(day) is expected


def test_next_weekday_skips_the_weekend():
    """A Saturday rolls forward to the following Monday."""
    assert next_weekday(SATURDAY) == datetime.date(2026, 7, 27)


def test_next_weekday_leaves_a_weekday_alone():
    """A weekday is already the next weekday."""
    assert next_weekday(MONDAY) == MONDAY
