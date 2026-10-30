I added `parse_when(text)` to `planner/when.py`. I ran it on the cases you listed and on one invalid string:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It uses `datetime.fromisoformat`. That accepts the `Z` suffix on the Python 3.14 here, but I didn't check it on older versions. A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise.

I didn't add tests.
