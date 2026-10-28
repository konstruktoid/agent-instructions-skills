I added `parse_when(text)` to `planner/when.py`. I ran it on four inputs and each gave the expected result:

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` gives `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `x` raises `ValueError`.

It uses `datetime.fromisoformat`, which handles the `Z` suffix on this Python (3.13). Python 3.10 and earlier don't accept `Z`.

You didn't specify a datetime with no offset, such as `2026-10-01T12:00:00`. I treat that as UTC rather than rejecting it.

I didn't add a test file.
