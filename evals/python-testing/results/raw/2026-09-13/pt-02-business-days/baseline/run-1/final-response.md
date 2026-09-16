Ruff and pytest pass (9/9). `ty` fails with an unresolved `tempo` import, but that's pre-existing on main (verified via stash) — the tool isn't configured to see `src/` as source root, unrelated to this change.

Files changed:
- `src/tempo/calendar.py` — added `business_days_between`; fixed `is_holiday`, which compared a `date` to a list of ISO strings and so always returned `False`
- `src/tempo/__init__.py` — exported `business_days_between`
- `tests/test_calendar.py` — added coverage for the new function
