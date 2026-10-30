I added `parse_when(text)` to `planner/when.py`. It uses `datetime.fromisoformat`, treats a value with no timezone as UTC, and converts anything with an offset to UTC.

I ran it on four inputs:
- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `x` raises `ValueError`.

The `Z` suffix needs Python 3.11 or later. I tested on 3.14 and didn't check which Python versions the project supports.

I didn't add tests.
