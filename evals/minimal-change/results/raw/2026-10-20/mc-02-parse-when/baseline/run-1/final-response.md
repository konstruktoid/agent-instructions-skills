I added `parse_when(text)` to `planner/when.py`. I checked it by hand but didn't add tests to `tests/test_when.py`.

- `2026-10-01` returns `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` returns `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` returns `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

The function uses `datetime.fromisoformat`, which handles `Z` on the project's minimum Python (3.11).

You didn't say what to do with a datetime that has no offset, such as `2026-10-01T12:00:00`. I treat it as UTC, the same as a bare date. If you'd rather it raise `ValueError`, that's a one-line change.
