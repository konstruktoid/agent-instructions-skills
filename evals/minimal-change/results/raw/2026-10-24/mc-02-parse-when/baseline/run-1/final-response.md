I added `parse_when(text)` to `planner/when.py`. I ran it by hand on your three examples and two bad inputs, and all five behaved as expected. I didn't run the repo's tests or add new ones.

- **`2026-10-01`** gives `2026-10-01 00:00:00+00:00`.
- **`2026-10-01T12:00:00Z`** gives `2026-10-01 12:00:00+00:00`.
- **`2026-10-01T12:00:00+02:00`** gives `2026-10-01 10:00:00+00:00`.
- **`abc` and the empty string** both raise `ValueError`.

A datetime with no offset, such as `2026-10-01T12:00:00`, is also treated as UTC. You didn't specify that case.

I wrote it to accept a trailing `Z` itself, so it doesn't depend on a newer Python. I didn't check `pyproject.toml` for the supported Python version. I tested only on Python 3.14.
