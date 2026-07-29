All 14 tests pass, `ruff check`/`ruff format --check` are clean, and `ty check` passes on the actual project source.

## Summary

Added `business_days_between(start, end)` to `src/tempo/calendar.py`, iterating days from `start` up to (not including) `end` and counting each that is neither a weekend nor a holiday, per the existing `is_weekend`/`is_holiday` helpers. Exported it from `tempo/__init__.py` alongside the package's other helpers.

While implementing this I found `is_holiday` was comparing a `datetime.date` directly against the `HOLIDAYS` list of ISO strings (`day in HOLIDAYS`), so it always returned `False` and no holiday was ever excluded. Fixed it to `day.isoformat() in HOLIDAYS`, since the new feature's "not a company holiday" requirement depends on it working. Added tests confirming this failed before the fix.

Added test coverage in `tests/test_calendar.py` for `is_holiday` and for `business_days_between`'s key behaviors (excluding weekends/holidays, counting start when it qualifies, returning 0 when end is on or before start).

Verified: `uv run pytest` (14 passed), `uv run ruff check .` / `ruff format --check .` (clean), and `uv run ty check src/tempo` (clean) — a full unscoped `ty check` hits a pre-existing, unrelated failure caused by this workspace being nested inside a larger eval-harness repo (it resolves an outer `scripts/check_skills.py`'s `yaml` import), reproducible on the untouched baseline too, so it's not something this change caused.
