I added `business_days_between(start, end)` to `src/tempo/calendar.py` and exported it from `tempo/__init__.py` next to the other helpers. `ruff check`, `ruff format --check`, `ty check` and `pytest` (12 tests) all pass.

It walks each day from `start` up to but not including `end`. It counts a day when `is_weekend` and `is_holiday` both say no, and it returns 0 when `end` is on or before `start`. I didn't reuse `days_between`, because that counts both ends.

**Bug fix in `is_holiday`:** it compared a `date` against the list of ISO strings in `HOLIDAYS`, so it never returned True. I changed it to `day.isoformat() in HOLIDAYS`. Without that, the new function would have counted holidays as working days.

**Tests:** I added tests in `tests/test_calendar.py` for the holiday fix and for `business_days_between`. They cover a weekend, a holiday, a weekend start day, and `end` equal to or before `start`.

**`ty`:** run from the repo root, `ty check` also picks up unrelated scripts in a parent directory and fails on them. It passes when limited to this project with `uv run ty check --extra-search-path src src tests`.
