I added `business_days_between(start, end)` to `src/tempo/calendar.py` and exported it from `tempo/__init__.py` alongside the other helpers. All 13 tests pass, and ruff check, ruff format and ty are clean.

It walks each day from `start` up to but not including `end`. It counts a day when `is_weekend` and `is_holiday` both say no, so it returns 0 when `end` is on or before `start`. I didn't use `days_between`, because it counts both ends, which is the opposite of what you asked for.

**Fix to `is_holiday`:** it compared a `date` against the ISO strings in `HOLIDAYS`, so it always returned False and holidays would never have been excluded. It now compares `day.isoformat()`. This changes the existing function's behavior.

I added tests for the new function and for `is_holiday` in `tests/test_calendar.py`.

**ty scope:** a plain `uv run ty check` reports errors in scripts outside this repo. I ran it as `uv run ty check --extra-search-path src src tests`, and that passes.

I made no commit.
