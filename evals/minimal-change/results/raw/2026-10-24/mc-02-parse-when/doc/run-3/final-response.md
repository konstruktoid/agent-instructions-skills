I added `parse_when(text)` to `planner/when.py`. It handles all three forms you listed, and the tests pass.

- **Date alone:** `2026-10-01` gives midnight UTC.
- **`Z` suffix or offset:** the result is converted to UTC.
- **Not a date:** `ValueError` is raised.

I used `datetime.fromisoformat`, which handles all three forms on Python 3.11+. That matches the `requires-python` setting in `pyproject.toml`.

A datetime with no offset, such as `2026-10-01T12:00:00`, wasn't in your list. I treat it as UTC and marked that with a `shortcut:` comment in the code.

I added one test in `tests/test_when.py` covering the three accepted forms and one invalid string.

Skipped: I didn't test other malformed inputs (for example `None` or an empty string) or the offset-less datetime.
