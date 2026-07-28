Done. Summary:

- Added `business_days_between(start, end)` to `src/tempo/calendar.py`, built from the existing `is_weekend`/`is_holiday` helpers: it walks each day in `[start, end)`, counting weekdays that aren't holidays, and returns `0` when `end <= start`.
- Exported it from `src/tempo/__init__.py` alongside the package's other helpers.
- Fixed a latent bug in `is_holiday`: it compared a `datetime.date` against `HOLIDAYS` (a list of ISO strings), so it always returned `False` — this would have silently broken holiday exclusion for the new function. Now compares `day.isoformat()`.
- Added tests in `tests/test_calendar.py` covering weekend exclusion, holiday exclusion, start-date inclusion, and the `end <= start` zero case.

Checks: `pytest` (10/10 passed), `ruff check` (all checks passed), and `ty check` (only the same pre-existing, unrelated diagnostic about an outer-repo `scripts/check_skills.py` file that's present on the untouched baseline too — verified via `git stash`).
