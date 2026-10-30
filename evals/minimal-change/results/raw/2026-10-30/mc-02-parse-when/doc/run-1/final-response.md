I added `parse_when(text)` to `planner/when.py`, and the tests pass (3 ran).

- **Accepted forms:** a date alone gives midnight UTC. A datetime ending in `Z` or carrying an offset is converted to UTC.
- **Errors:** anything else raises `ValueError`. That includes a datetime with no offset, like `2026-10-01T12:00:00`, which your spec doesn't list and which I rejected instead of guessing a timezone.
- **Implementation:** it uses the standard library's `fromisoformat` (rung 3 of the reuse ladder), so there are no new dependencies. `date.fromisoformat` runs first because on Python 3.11 and later `datetime.fromisoformat` would return a date-only string as a naive datetime.
- **Tests:** I added one small test class in `tests/test_when.py`. It covers the three accepted forms, plus rejection of `"tomorrow"`, `""` and a datetime with no offset.

Not checked: Python 3.11 specifically, since I ran the tests only on 3.14. `pyproject.toml` requires 3.11 or later. `fromisoformat` accepts more ISO variants than your examples, such as `20261001`, and I didn't narrow it.
