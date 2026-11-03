`business_days_between(start, end)` is now in `src/tempo/calendar.py`. It's exported from `tempo/__init__.py` and listed in `__all__`, like the other helpers. `ruff check`, `ruff format`, `ty` and `pytest` all pass (10 tests). Plain `ty check` fails here, but only because of where this repo sits (details below).

- **How it works:** it steps through each day from `start` up to but not including `end`. It counts a day only when `is_weekend` and `is_holiday` both say no. It returns 0 when `end` is on or before `start`.
- **Bug fix in `is_holiday`:** it compared a `date` against the list of ISO date strings in `HOLIDAYS`, so it never matched and holidays were never excluded. It now compares `day.isoformat()`. This changes what `is_holiday` returns for existing callers.
- **Why I didn't use `days_between`:** it counts both ends, which is the opposite of what you asked for.
- **Tests added:** `is_holiday` recognises a listed date, and a range that crosses a weekend and the 2026-07-22 holiday. They also cover a plain week (start counted, end excluded) and empty or reversed ranges.
- **`ty` invocation:** this workspace sits inside a larger directory tree, so plain `ty check` picks up unrelated files outside the repo and can't find the `tempo` package. I ran `uv run ty check --project . --extra-search-path src src tests` instead. I didn't change any project config for this.

I haven't committed anything.
