I added `parse_when(text)` to `planner/when.py`. I ran it on four inputs and each gave the expected result:

- **Date alone:** `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- **Trailing `Z`:** `2026-10-01T05:00:00Z` gives `2026-10-01 05:00:00+00:00`.
- **Offset:** `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- **Not a date:** `x` raises `ValueError`.

A datetime with no offset is also treated as UTC. You didn't specify that case, so say if you'd rather it raise. I didn't add any tests or a test file.
