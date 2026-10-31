I added `parse_when(text)` to `planner/when.py`. I ran it on your three formats and on bad text, and each gave the expected result:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

A datetime with no offset, such as `2026-10-01T12:00:00`, is read as UTC. You didn't specify that case, so say if you'd rather it raise an error.

I didn't add tests, and I didn't test non-string input. As far as I know, `datetime.fromisoformat` raises `TypeError` for that rather than `ValueError`.
