I added `parse_when(text)` to `planner/when.py`. I ran it by hand on your three examples and one bad input, and all four behaved as expected. I didn't add tests or run the existing suite.

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It uses `datetime.fromisoformat`, which handles `Z` on Python 3.11 and later; the project already requires 3.11 or later.

You didn't specify a datetime with no offset, such as `2026-10-01T12:00:00`. I treat it as UTC rather than rejecting it.

`fromisoformat` also accepts some compact ISO forms, such as `20261001`. I haven't restricted that.
