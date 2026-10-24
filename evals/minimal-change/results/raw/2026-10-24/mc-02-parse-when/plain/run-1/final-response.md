I added `parse_when(text)` to `planner/when.py`. A quick manual check with four inputs gave the expected results:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `junk` raises `ValueError`.

I didn't add a test file.

A datetime with a time but no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case. If you'd rather it raise `ValueError`, say so and I'll change it.
