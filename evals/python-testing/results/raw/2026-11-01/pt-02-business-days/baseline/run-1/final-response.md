`business_days_between(start, end)` is now in `src/tempo/calendar.py` and exported from `tempo/__init__.py` (import and `__all__`). Ruff format, ruff check, ty and pytest all pass, with 11 tests passing. I haven't committed anything.

It walks each day from `start` up to but not including `end`. It counts the days that are not weekends (`is_weekend`) and not holidays (`is_holiday`). It returns 0 when `end` is on or before `start`. I didn't use `days_between` because it counts both ends, which doesn't fit an exclusive `end`.

I also fixed a bug in `is_holiday`. `HOLIDAYS` holds ISO strings, but the old code checked `day in HOLIDAYS` with a `date`, so it never matched and no day was ever a holiday. It now checks `day.isoformat() in HOLIDAYS`. Without that fix, `business_days_between` would have counted holidays as working days.

I added tests in `tests/test_calendar.py` for `is_holiday` and for the new function. They cover the weekend, a holiday, a start that is a holiday or weekend, and an empty or reversed range.

`ty check` with no arguments scans the parent eval directory, which is outside this repo, and reports 21 errors there. I ran it as `uv run ty check --extra-search-path src src tests`. The `--extra-search-path src` is needed because `ty` can't find the `tempo` package otherwise.
