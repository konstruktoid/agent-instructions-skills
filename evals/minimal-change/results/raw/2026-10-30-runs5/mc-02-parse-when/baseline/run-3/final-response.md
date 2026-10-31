I added `parse_when(text)` to `planner/when.py`. I ran it by hand on your three examples and one bad string, but I didn't add tests or run the existing test suite.

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It relies on `datetime.fromisoformat`, which accepts `Z` because the project requires Python 3.11 or later. A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC, which you didn't specify. A non-string input would raise `TypeError` rather than `ValueError`.
