`business_days_between(start, end)` is now in `src/tempo/calendar.py` and exported from `tempo/__init__.py` the same way as the other helpers. `ruff format`, `ruff check` and `ty check` are clean, and all 13 tests pass.

- **Behavior:** it counts days from `start` up to but not including `end`. A day counts if `is_weekend` and `is_holiday` both say no, and it returns 0 when `end` is on or before `start`.
- **Bug fix:** `is_holiday` was always returning False. It tested `day in HOLIDAYS`, which compares a `date` to the ISO strings in the list. It now tests `day.isoformat() in HOLIDAYS`, and I added a test for it. Without this fix, holidays would never have been excluded.
- **Tests:** I added them to `tests/test_calendar.py` in the existing style. They cover:
  - counting the start day but not the end day;
  - skipping weekends;
  - skipping the 22 July holiday;
  - a start day that falls on a weekend;
  - the `end == start` and `end < start` cases.
- **Test mistakes:** two of my first expected values were wrong. I had forgotten that 22 July falls inside those ranges. I corrected the expected counts; I did not weaken any assertions.
- **`ty` scope:** a plain `ty check` picks up the parent repository and reports unrelated errors outside this project. I ran `uv run ty check --extra-search-path src src tests` instead, which is clean.
- **`.gitignore`:** I added one containing `__pycache__/` and `.venv/` so the generated files stay out of git.
- **Not committed:** I made no commit.
