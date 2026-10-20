I added `parse_when(text)` to `planner/when.py`. I ran it on three inputs, and each gave the expected UTC result:

- `2026-10-01` gave `2026-10-01 00:00:00+00:00`.
- `2026-10-01T05:00:00Z` gave `2026-10-01 05:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gave `2026-10-01 10:00:00+00:00`.

The string `nope` raised `ValueError`. I didn't add a test file.

It also treats a datetime with no offset, such as `2026-10-01T12:00:00`, as UTC.

If `text` isn't a string, `datetime.fromisoformat` raises `TypeError` rather than `ValueError`.
