I added `parse_when(text)` to `planner/when.py`, and the tests pass (3 run, including the 2 new ones). It uses `datetime.fromisoformat`, which in Python 3.11 and later handles all three forms, including `Z`. That matches the project's `requires-python = ">=3.11"`. Aware inputs are converted to UTC, and anything that isn't a date raises `ValueError`.

The new tests in `tests/test_when.py` cover the three accepted forms and one invalid string (`"tomorrow"`).

I left out the choice of how to treat naive datetimes. You didn't specify them, so `2026-10-01T12:00:00` with no offset is read as UTC rather than rejected. The code has a `shortcut:` comment on that line. If you'd rather reject them, say so and I'll change it.
