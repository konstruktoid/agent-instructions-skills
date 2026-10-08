`business_days_between(start, end)` is added in `src/tempo/calendar.py` and exported from `tempo/__init__.py`, both in the import and in `__all__`, like the other helpers. The full suite passes with 12 tests, and `ruff check` and `ruff format --check` are clean.

- **Holiday bug fixed:** `is_holiday` compared a `date` against the ISO strings in `HOLIDAYS`, so it never returned True. I changed it to `day.isoformat() in HOLIDAYS`. Without that change the new function would have counted holidays as working days.
- **Calendar helpers:** The function uses `is_weekend` and `is_holiday`. I didn't use `days_between`, because it counts both ends and this function excludes `end`.
- **Tests:** `tests/test_calendar.py` now covers `is_holiday`, which would have caught the bug. It also covers `business_days_between` for excluding `end`, counting `start`, skipping weekends and holidays, and returning 0 when `end` is on or before `start`. I did not run the new `is_holiday` test against the unfixed code to confirm it fails.
- **`ty`:** A bare `uv run ty check` fails. It scans a parent directory outside this repo and can't resolve `tempo`, because the project only puts `src` on the path through pytest's config. `uv run ty check --extra-search-path src src tests` passes. I didn't change the project config.

I left the `__pycache__` directories untracked and did not commit anything.
