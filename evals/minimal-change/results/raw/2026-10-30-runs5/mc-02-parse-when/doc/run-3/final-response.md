I added `parse_when(text)` to `planner/when.py`, and the tests pass (3 tests, including the two new ones).

It uses the standard library's `datetime.fromisoformat` (Python 3.11 or later, which `pyproject.toml` requires). The library call handles all three forms you listed: a date alone gives midnight UTC, `Z` is accepted, and an offset is converted to UTC. Text that isn't a date raises `ValueError`.

I added two tests in `tests/test_when.py`. One covers the three accepted forms and one covers text that isn't a date.

**Not covered:**
- **No-offset datetimes:** a datetime with no offset, such as `2026-10-01T12:00:00`, wasn't in your list. It is read as UTC and marked with a `shortcut:` comment in the code. Say if you'd rather it raise `ValueError`.
- **Non-string input:** passing something that isn't a string raises `TypeError`, not `ValueError`.
