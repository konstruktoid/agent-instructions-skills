I added `parse_when(text)` to `planner/when.py`. I ran it on three inputs and all gave the expected results:
- `2026-10-01` returns `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` returns `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` returns `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It relies on `datetime.fromisoformat`, which in the Python 3.14 here accepts the `Z` suffix and bare dates. On an older Python, `Z` may not parse and would raise `ValueError`.

You didn't say what to do with a datetime that has no offset, such as `2026-10-01T12:00:00`. I treat it as UTC, but it would be easy to make it raise instead.

I didn't add a test file.
