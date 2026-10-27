I added `parse_when(text)` to `planner/when.py`. I ran it on your three example formats and on one bad string, and the results were correct:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It relies on `datetime.fromisoformat`, which handles `Z` and offsets on Python 3.11 and later. This environment has 3.13. On an older Python, the `Z` form would fail.

Text without an offset, such as `2026-10-01T12:00:00`, is also treated as UTC, which you didn't specify.

I didn't add a test file or run any existing tests.
