`business_days_between(start, end)` is added in `src/tempo/calendar.py` and exported from `tempo/__init__.py` alongside the other helpers. It returns 0 when `end` is on or before `start`.

I also fixed an existing bug in `is_holiday`. It tested `day in HOLIDAYS`, a `date` against a list of ISO strings, so it was always False and no holiday was ever excluded. It now checks `day.isoformat() in HOLIDAYS`. The new function would have counted holidays as working days without that fix.

I added tests to `tests/test_calendar.py` in the existing style. They cover `is_holiday`, the weekend and exclusive end, start being counted, a holiday being skipped, and the zero result for an end on or before start.

Checks:
- **pytest:** `uv run pytest` passes, 12 tests.
- **ruff:** `ruff check` and `ruff format --check` are clean.
- **ty:** `uv run ty check src tests` fails for two reasons that aren't about this change. It picks up scripts in a parent directory (`aisk/scripts`) and reports errors there. It also can't resolve `tempo` because the project doesn't give it a `src` path. `uv run ty check --extra-search-path src src tests` passes.

I didn't confirm that the holiday tests fail against the old `is_holiday`.
