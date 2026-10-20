I added `parse_when(text)` to `planner/when.py`. I ran it by hand but didn't add tests or run the repo's checks.

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It's a thin wrapper around `datetime.fromisoformat`, which handles all three forms on the project's Python 3.11+.

A datetime with no offset, such as `2026-10-01T12:00:00`, isn't covered by your spec. I made it count as UTC rather than raise an error. If you'd rather reject it, say so and I'll change it.
