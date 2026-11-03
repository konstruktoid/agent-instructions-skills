`business_days_between(start, end)` is now in `src/tempo/calendar.py` and exported from `tempo`. The full pytest suite (12 tests), `ruff check`, `ruff format --check` and `ty check` all pass.

- **How it counts:** it steps day by day from `start` up to but not including `end`. It counts each day that is neither a weekend nor a holiday, using the existing `is_weekend` and `is_holiday` helpers. It returns 0 when `end` is on or before `start`.
- **Export:** it is added to the import and `__all__` in `src/tempo/__init__.py`, the same way as the other helpers.
- **A bug I fixed on the way:** `is_holiday` compared a `date` to the ISO strings in `HOLIDAYS`, so it always returned False. It now checks `day.isoformat()`. Without that fix the new function would have counted holidays as working days.
- **Tests:** I added tests to `tests/test_calendar.py` in the existing style. They cover a holiday being skipped, `start` counting while `end` doesn't, the zero cases, and `is_holiday` recognising a listed holiday.

I didn't run the new tests against the old `is_holiday` to confirm they fail without the fix.

A bare `uv run ty check` also scans the parent directory, which has unrelated errors. I ran it as `uv run ty check --project . --extra-search-path src src tests`, which is clean for this repo.

I haven't committed anything.
