I added `parse_when(text)` to `planner/when.py`, and the tests pass. It uses `datetime.fromisoformat`, which handles all three input forms on the repo's Python 3.11+ (`requires-python = ">=3.11"`). The result is converted to UTC, and text that isn't a date raises `ValueError`.

- **Date alone:** `2026-10-01` becomes midnight UTC.
- **`Z` and offsets:** `Z` and `+02:00` are converted to UTC.
- **Naive datetime:** a datetime with no `Z` or offset, such as `2026-10-01T12:00:00`, is read as UTC. You didn't specify this case, so say if you'd rather it raise `ValueError`.
- **Non-string input:** something like `None` raises `TypeError`, not `ValueError`.

I added one test to `tests/test_when.py` covering the three accepted forms and one invalid string. I didn't add separate tests for the naive-datetime case or non-string input.
