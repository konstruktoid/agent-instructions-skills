I added `parse_when(text)` to `planner/when.py`. I ran it on the three example forms and on one invalid string.

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

A datetime with no offset, such as `2026-10-01T12:00:00`, is also treated as UTC, since you didn't say what it should do. I didn't write any test files.
