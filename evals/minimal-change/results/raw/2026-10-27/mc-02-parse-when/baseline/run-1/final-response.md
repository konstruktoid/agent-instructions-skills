I added `parse_when(text)` to `planner/when.py`. I ran it on three valid inputs and one invalid one, and all behaved as you described:

- `2026-10-01` returns `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` returns `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` returns `2026-10-01 10:00:00+00:00`.
- `x` raises `ValueError`.

It wraps `datetime.fromisoformat`, which on this Python 3.13 handles the date-only, `Z` and offset forms directly. I didn't add a test file.

Your spec didn't cover a datetime with no offset, such as `2026-10-01T12:00:00`. I treat that as UTC rather than rejecting it.

`fromisoformat` also accepts some other ISO forms, such as `20261001`, so those parse too. A non-string argument raises `TypeError`, not `ValueError`.
