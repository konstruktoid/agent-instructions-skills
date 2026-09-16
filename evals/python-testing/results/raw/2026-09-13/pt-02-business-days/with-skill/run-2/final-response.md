`business_days_between(start, end)` is added to `src/tempo/calendar.py:34` and exported from `src/tempo/__init__.py`, using the package's existing `is_weekend` and `is_holiday` helpers.

**Files changed:**
- `src/tempo/calendar.py` — new `business_days_between`; also fixed `is_holiday`, which compared a `datetime.date` to the `HOLIDAYS` list of ISO strings and so always returned `False`. Without this fix, holidays could never be excluded, defeating the point of the new function.
- `src/tempo/__init__.py` — exports `business_days_between` alongside the other helpers.
- `tests/test_calendar.py` — coverage for `is_holiday` (previously untested, and the fix fails without it) and `business_days_between` (weekend/holiday exclusion, counting a qualifying start, excluding end, zero when end is on or before start).

**Verification:** `uv run pytest` → 13 passed. `uv run ruff check .` and `uv run ruff format --check .` → clean. `uv run ty check` on the bare project sweeps in an unrelated outer monorepo (this workspace is nested under `evals/.../results/...` inside a larger repo whose `pyproject.toml` gets picked up by ty's upward config walk) and reports pre-existing errors in that outer repo's `scripts/check_skills.py` — unrelated to this change. Scoped to this project (`ty check --extra-search-path src src tests`), it passes clean.

Task's done — recommend `/clear` before anything unrelated.
