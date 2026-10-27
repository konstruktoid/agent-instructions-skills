I added `parse_when(text)` to `planner/when.py`. I ran it on the three formats and on bad text, and all four behaved as asked:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `x` raises `ValueError`.

It uses `datetime.fromisoformat`, which on this Python (3.13) accepts all three formats and raises `ValueError` on bad text. Input with no offset is treated as UTC, and input with an offset is converted to UTC.

I didn't add a test file. The `Z` suffix only parses on Python 3.11 or newer.
