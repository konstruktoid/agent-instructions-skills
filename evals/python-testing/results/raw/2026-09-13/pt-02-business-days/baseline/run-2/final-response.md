All checks pass (ruff clean, pytest 11/11). The `ty` module-resolution error is pre-existing on `main`, unrelated to this change.

Changes:
- `src/tempo/calendar.py` — added `business_days_between(start, end)`; fixed `is_holiday` (was comparing a `date` against the string-valued `HOLIDAYS` list, so it never matched anything).
- `src/tempo/__init__.py` — exported `business_days_between`.
- `tests/test_calendar.py` — added tests for weekend exclusion, holiday exclusion, start-date inclusion, end-date exclusion, and non-positive ranges.

You'll want to decide whether fixing `is_holiday` belongs in this diff or a separate one — I folded it in since `business_days_between` is meaningless without it, but flagging it in case you'd rather split it out.
