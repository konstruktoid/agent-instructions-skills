I added `parse_when(text)` to `planner/when.py`. I ran it on your three examples and on `nope`, and each gave the expected result. I didn't add tests or run the existing ones.

- `2026-10-01` returns `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` returns `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` returns `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It relies on `datetime.fromisoformat`, which handles `Z` and offsets because the project requires Python 3.11 or later. A datetime with no offset, like `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say so if you'd rather it raise.
