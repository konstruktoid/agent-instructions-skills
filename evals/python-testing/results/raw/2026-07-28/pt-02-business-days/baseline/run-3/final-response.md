Same pre-existing, unrelated failure (it's resolving an outer, unrelated repo as the first-party root and can't even see this `tempo` project) — confirmed unaffected by my change.

## Summary

Added `business_days_between(start, end)` to `src/tempo/calendar.py`, built on the existing `is_weekend`/`is_holiday` helpers with a half-open day-by-day walk (`src/tempo/calendar.py:29-36`), and exported it from `tempo/__init__.py` alongside the package's other helpers.

Along the way I found `is_holiday` was silently broken — it compared a `datetime.date` against `HOLIDAYS` (a list of ISO strings), which never matches, so holidays were never actually excluded anywhere in the package. Fixed it to compare `day.isoformat()` instead, since `business_days_between`'s correctness depends on it.

Added tests covering weekend/holiday exclusion, start-inclusion, end-exclusion, the zero-day case, and `is_holiday` itself.

Checks: `pytest` (13 passed) and `ruff check` (clean) both pass. `ty check` fails identically before and after my change — it resolves an unrelated outer repository as its first-party root and can't even see the `tempo` package, a pre-existing environment issue outside this task's scope.
