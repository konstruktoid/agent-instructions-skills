Good — those `.pyc` files were already tracked in the baseline commit, so their modification is just a side effect of running the tests, not something I introduced. No further action needed there since I haven't committed anything.

## Summary

Added `business_days_between(start, end)` to `src/tempo/calendar.py`, exported it from `src/tempo/__init__.py` alongside the existing helpers, and added parametrized test coverage in `tests/test_calendar.py` (weekday counting, weekend exclusion, and the two zero-day edge cases) following the existing test style. `pytest`, `ruff check`, `ruff format --check`, and `ty check` all pass.

Note: `ty check` needs `--extra-search-path src` in this nested eval-harness checkout — `ty` walks up past this repo to an outer `pyproject.toml` for config resolution, which breaks first-party import resolution regardless of any code change (verified this occurs on the untouched baseline too, so it's a pre-existing environment quirk, not something introduced here).
