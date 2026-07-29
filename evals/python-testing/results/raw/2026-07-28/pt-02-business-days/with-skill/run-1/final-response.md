All checks pass. Summary of changes:

- **`src/tempo/calendar.py`**: added `business_days_between(start, end)`, which walks from `start` up to (not including) `end`, counting each day that is not a weekend and not a holiday via the existing `is_weekend`/`is_holiday` helpers. Returns `0` naturally when `end <= start`.
- Fixed a pre-existing bug in `is_holiday`: it compared a `datetime.date` directly against `HOLIDAYS` (a list of ISO date strings), so it always returned `False`. Changed to `day.isoformat() in HOLIDAYS`. This was necessary for `business_days_between` to actually exclude holidays as required.
- **`src/tempo/__init__.py`**: exported `business_days_between` alongside the other helpers, matching the existing export style.
- **`tests/test_calendar.py`**: added coverage for `is_holiday` (confirmed it fails without the fix) and for `business_days_between` — excluding weekends/holidays, counting a qualifying start, excluding a non-qualifying (holiday) start, and returning 0 when `end` is on or before `start`.

Verified with `uv run pytest` (14/14 passing, per the README's documented check command), `ruff check`/`ruff format --check` (clean), and `ty check` (clean once scoped to this project — the eval sandbox nests this fixture inside a larger dev repo whose own `pyproject.toml` `ty` config gets picked up by ty's upward config walk unless the project root is pinned explicitly).
