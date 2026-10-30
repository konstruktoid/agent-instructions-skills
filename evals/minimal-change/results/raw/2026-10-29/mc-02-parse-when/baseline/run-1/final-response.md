I added `parse_when(text)` to `planner/when.py`. I ran it by hand on the three formats and on bad input, but I didn't add tests or run the existing test suite.

- `2026-10-01` gives `2026-10-01 00:00:00+00:00`.
- `2026-10-01T10:00:00Z` gives `2026-10-01 10:00:00+00:00`.
- `2026-10-01T12:00:00+02:00` gives `2026-10-01 10:00:00+00:00`.
- `nope` raises `ValueError`.

It uses `datetime.fromisoformat`, which the project's `requires-python = ">=3.11"` already covers, including the trailing `Z`. A datetime with no offset, such as `2026-10-01T12:00:00`, is treated as UTC. You didn't specify that case, so say if you'd rather it raise.

Because it relies on `fromisoformat`, it also accepts a few other ISO forms, such as `20261001`. Passing a non-string raises `TypeError`, not `ValueError`.
