I added `parse_when(text)` to `planner/when.py`. I ran it by hand on your three example formats and on `"nope"`. I didn't run the existing tests in `tests/test_when.py`, and I didn't add new ones.

- `2026-10-01` returns `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` returns `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` returns `2026-10-01 10:00:00+00:00`.
- `"nope"` raises `ValueError`.

It uses `datetime.fromisoformat`, which handles the `Z` suffix because the project requires Python 3.11 or later. A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise an error.

Because it relies on `fromisoformat`, it also accepts other ISO forms that Python 3.11 allows, such as `20261001`. Non-string input raises `TypeError`, not `ValueError`.
