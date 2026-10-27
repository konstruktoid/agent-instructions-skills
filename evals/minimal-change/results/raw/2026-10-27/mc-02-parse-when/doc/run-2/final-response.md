I added `parse_when(text)` to `planner/when.py`, and the tests pass. It uses `datetime.fromisoformat`, which on Python 3.11+ (the project's minimum) already handles all three forms. It converts the result to UTC. Text that isn't a date raises `ValueError` from `fromisoformat`.

- **Naive input:** A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify this case, so say if you'd rather it raise.
- **Tests:** I added two tests to `tests/test_when.py`, one covering the three accepted forms and one for the `ValueError`.

Skipped: nothing else. I didn't test other ISO 8601 shapes such as week dates, because `fromisoformat` defines what it accepts.
