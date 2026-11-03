`business_days_between(start, end)` is now in `src/tempo/calendar.py` and exported from `tempo/__init__.py` and `__all__`. The checks pass: `ruff check`, `ruff format --check`, `ty check`, and `pytest` (13 passed).

It counts days from `start` up to but not including `end`. A day counts when `is_weekend` and `is_holiday` both say no. It returns 0 when `end` is on or before `start`.

**Bug fix in `is_holiday`:** `is_holiday` could never return True. `HOLIDAYS` holds ISO strings, but it compared them to a `date`. I changed it to `day.isoformat() in HOLIDAYS`, because the new function would otherwise have counted holidays as working days. I did not run the new tests against the unfixed `is_holiday`.

**Tests:** I added tests to `tests/test_calendar.py` for the following:
- the `is_holiday` fix
- a holiday being skipped
- `end` being excluded, including when it is a holiday
- the 0 cases
- a weekend-only span

My first draft of one test had the wrong expected count (5 instead of 4), because the span included the 22 July holiday. I corrected the test, not the code.

**`ty` scope:** a bare `uv run ty check` also scans the parent directory, which is outside this repo, and reports errors there. I ran `uv run ty check --extra-search-path src src tests` instead, and it is clean. Without the extra search path, `ty` can't resolve `tempo` in the tests.
