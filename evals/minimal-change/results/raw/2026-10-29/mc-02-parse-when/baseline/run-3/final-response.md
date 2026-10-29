I added `parse_when(text)` to `planner/when.py`. I ran it on the three formats and on one bad string, and all behaved as expected:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `bad` raises `ValueError`.

It uses `datetime.fromisoformat`, which on this Python (3.14) already handles the `Z` suffix. On Python older than 3.11, `fromisoformat` rejects `Z`, so that input would raise `ValueError`.

A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise.

I didn't add tests.
