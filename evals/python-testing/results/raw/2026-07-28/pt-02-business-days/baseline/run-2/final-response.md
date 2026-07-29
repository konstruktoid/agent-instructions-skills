All checks pass. Summary of changes:

- **`src/tempo/calendar.py`**: added `business_days_between(start, end)`, which walks each day in `[start, end)` and counts weekdays (`is_weekend`) that aren't holidays (`is_holiday`), returning `0` when `end <= start`. Also fixed `is_holiday`, which compared a `date` object against `HOLIDAYS` (a list of ISO strings) and so never matched anything — it now compares `day.isoformat()` against the list. This bug would have made holiday exclusion silently no-op for the new function.
- **`src/tempo/__init__.py`**: exported `business_days_between` alongside the other helpers.
- **`tests/test_calendar.py`**: added tests covering holiday/weekend exclusion, counting `start` when it qualifies, excluding `end`, and returning `0` for a non-positive range.

`uv run pytest` (11 passed) and `uv run ruff check .` (clean) both pass. Note: `ty check` errors out, but that's a pre-existing environment quirk unrelated to this change — it resolves the "first-party" root to a parent monorepo directory and fails on an unrelated file (`scripts/check_skills.py`, missing `yaml`) outside this project; I confirmed via `git stash` that it fails identically on the untouched code. The project's documented check is `uv run pytest` (per README.md).
