I added `business_days_between(start, end)` to `src/tempo/calendar.py`. `ruff format`, `ruff check`, `ty check` and `pytest` (10 tests) all pass.

- **Behaviour:** it counts days from `start` up to but not including `end`. Weekends and company holidays are skipped. It uses the existing `is_weekend` and `is_holiday` helpers and returns 0 when `end` is on or before `start`.
- **Export:** it is imported in `src/tempo/__init__.py` and listed in `__all__`, the same way as the other helpers.
- **Bug fixed in `is_holiday`:** it checked a `date` against a list of ISO strings, so it always returned False and no holiday was ever excluded. It now compares `day.isoformat()` against `HOLIDAYS`. This changes the behaviour of an existing function.
- **Tests:** I added tests for `is_holiday` and for the new function, covering the weekend skip, the 22 July holiday and empty ranges.
- **`ty` setup:** `ty check` run bare scans files outside this project and fails on them. It also can't resolve `tempo` from the tests. I ran `uv run ty check --extra-search-path src src tests`. I didn't change the project config for this.
