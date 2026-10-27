I added `parse_when(text)` to `planner/when.py`. I ran it on the three input forms and on invalid text, and each gave the expected result:

- `2026-10-01` returns `2026-10-01 00:00:00+00:00`.
- `2026-10-01T12:00:00Z` returns `2026-10-01 12:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` returns `2026-10-01 10:00:00+00:00`.
- `x` raises `ValueError`.

It uses `datetime.fromisoformat`, which handles `Z` on Python 3.11 and later (this environment has 3.13). A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC, since you didn't say what to do with that case. I didn't add tests or run any beyond those four inputs.
