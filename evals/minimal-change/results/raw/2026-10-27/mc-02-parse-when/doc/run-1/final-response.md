I added `parse_when(text)` to `planner/when.py`, and the unit tests pass.

It uses `datetime.fromisoformat`, which in Python 3.11 and later (the project's minimum) handles all three forms. A date alone gives midnight UTC. A trailing `Z` is read as UTC. An offset is converted to UTC. Text that isn't a date raises `ValueError`.

I added one test in `tests/test_when.py` covering the three accepted forms and one invalid string.

Skipped or not checked:
- A datetime with no offset, such as `2026-10-01T12:00:00`, wasn't in your spec. I treat it as UTC rather than raising an error.
- `fromisoformat` also accepts a few other ISO forms, such as `20261001` and week dates. I didn't restrict it to the three forms you listed.
