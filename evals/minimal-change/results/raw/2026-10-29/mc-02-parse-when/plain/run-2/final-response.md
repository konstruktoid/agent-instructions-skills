I added `parse_when(text)` to `planner/when.py`. I ran it on your three examples and on `nope`, and it behaved as specified:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It relies on `datetime.fromisoformat`, which in Python 3.14 handles all three formats. A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC, which you didn't specify.

I didn't add tests or run any existing ones.
