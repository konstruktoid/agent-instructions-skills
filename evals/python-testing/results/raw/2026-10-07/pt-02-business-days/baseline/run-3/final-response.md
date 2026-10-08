I added `business_days_between(start, end)` to `src/tempo/calendar.py` and exported it from `tempo/__init__.py`, including `__all__`. Ruff lint, ruff format, `ty check src tests` and pytest (11 tests) all pass. I haven't committed anything.

It uses the existing `is_weekend` and `is_holiday` helpers. I didn't use `days_between`, because that counts both ends and this function excludes `end`.

I also made two changes you didn't ask for:
- **`is_holiday` fix:** it did `day in HOLIDAYS`, but `HOLIDAYS` holds ISO strings, so a `date` never matched and it always returned `False`. It now checks `day.isoformat() in HOLIDAYS`. Without this, the new function would have counted holidays as working days.
- **`ty` config:** `ty` couldn't resolve `import tempo` in the tests, so `ty check` failed. I added `[tool.ty.environment] root = ["src"]` to `pyproject.toml`. Running bare `ty check` also scans the parent `aisk` repo and reports errors in its scripts. I ran it as `ty check src tests` to stay within this project.

I added tests for `is_holiday` and for the new function. They cover the inclusive start, the exclusive end, weekends, a holiday, and an empty or reversed range.
