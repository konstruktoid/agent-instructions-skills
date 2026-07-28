All checks pass (16 tests, ruff clean and formatted). `ty check` fails identically on the unmodified baseline due to a pre-existing `src`-layout module-resolution gap unrelated to this change, so it's not a regression.

Summary of changes:
- **`src/tempo/calendar.py`**: added `business_days_between(start, end)`, counting weekdays that aren't holidays in `[start, end)`. Also fixed a pre-existing bug in `is_holiday` — it compared a `datetime.date` against the ISO-string `HOLIDAYS` list, so it always returned `False`; now uses `day.isoformat() in HOLIDAYS`. This bug would have silently broken holiday exclusion in the new function.
- **`src/tempo/__init__.py`**: exported `business_days_between` alongside the other helpers.
- **`tests/test_calendar.py`**: added coverage for `business_days_between` (weekend/holiday exclusion, start-inclusive/end-exclusive boundaries, `end <= start` → 0) and for `is_holiday` itself (previously untested). Verified the new tests fail against the unfixed `is_holiday`.
