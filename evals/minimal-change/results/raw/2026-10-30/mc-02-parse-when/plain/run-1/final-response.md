I added `parse_when(text)` to `planner/when.py`. I ran it on each case and each gave the expected result:

- **Date alone:** `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- **Trailing `Z`:** `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- **Offset:** `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- **Not a date:** `x` raises `ValueError`.

A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case.

I didn't add tests or run any existing ones.
