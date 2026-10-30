I added `parse_when(text)` to `planner/when.py`. I ran it on four inputs and each gave the expected result:

- `2026-10-01` returned `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` returned `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` returned `2026-10-01 10:00:00+00:00`.
- `nope` raised `ValueError`.

It uses `datetime.fromisoformat`, which accepts a trailing `Z` on Python 3.11 and later. This environment runs 3.14. On an older Python, the `Z` case would raise `ValueError`.

A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't say what to do with that case, so say if you'd rather it raise.

I didn't add tests.
