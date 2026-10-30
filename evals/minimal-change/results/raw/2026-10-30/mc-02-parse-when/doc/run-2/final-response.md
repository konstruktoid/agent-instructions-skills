I added `parse_when(text)` to `planner/when.py`, and the unit tests pass.

It uses the standard library's `datetime.fromisoformat`, which on Python 3.11 handles all three forms you listed. A date alone becomes midnight UTC, `Z` is read as UTC, and an offset is converted to UTC. Anything else raises `ValueError`.

I added one test to `tests/test_when.py`. It covers the three accepted forms and one non-date string.

Nothing was skipped. Two cases the request didn't cover:
- **No offset:** a datetime with no `Z` or offset, such as `2026-10-01T12:00`, is read as UTC rather than rejected. If you'd rather it raise, that's a one-line change.
- **Non-string input:** input that isn't a string raises `TypeError`, not `ValueError`.
