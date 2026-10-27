I added `parse_when(text)` to `planner/when.py`. I ran it on four inputs and each gave the expected result:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `x` raises `ValueError`.

A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise instead.

I didn't add a test file or run any other tests.
