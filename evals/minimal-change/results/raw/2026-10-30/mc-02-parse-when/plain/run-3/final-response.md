I added `parse_when(text)` to `planner/when.py`. I ran it on the three formats and on invalid text:

- **Date alone:** `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- **`Z` suffix:** `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- **Offset:** `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- **Not a date:** `"nope"` raises `ValueError`.

A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise.

It relies on `datetime.fromisoformat` accepting a trailing `Z`, which needs Python 3.11 or later. I ran it on 3.14 and didn't add tests.
