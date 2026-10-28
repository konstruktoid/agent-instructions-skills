I added `parse_when(text)` to `planner/when.py`. I ran it on your three example formats and one bad input, and all behaved as specified:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It uses `datetime.fromisoformat`, which handles `Z` on Python 3.11 and later (this environment has 3.13). Your spec didn't cover a datetime with no offset, such as `2026-10-01T12:00:00`, so I treat it as UTC. I didn't add any tests.
