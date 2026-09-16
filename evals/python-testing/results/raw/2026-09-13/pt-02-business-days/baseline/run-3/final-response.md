All correct: the holiday (2026-07-22, Wed) is excluded, weekend boundaries are handled, and `end <= start` returns 0.

## Summary

Added `business_days_between(start, end)` to `src/tempo/calendar.py`, exported it from `src/tempo/__init__.py` alongside the package's other helpers.

While implementing it I found `is_holiday` was broken — it compared a `datetime.date` against the string dates in `HOLIDAYS`, so it always returned `False` — and fixed it to compare `day.isoformat()` instead, since `business_days_between` depends on it to exclude holidays correctly.

**Files changed:**
- `src/tempo/calendar.py` — fixed `is_holiday`, added `business_days_between`
- `src/tempo/__init__.py` — exported the new function

**Verification:** `uv run pytest -q` → 6 passed; `uv run ruff check .` → all checks passed. `uv run ty check` misidentifies its project root as the outer `agent-instructions-skills` repo (even with `--project` pinned to this workspace) and reports unrelated pre-existing errors in that outer repo's `scripts/`, not in `tempo` — an environment quirk of this nested fixture layout, not something introduced by this change. The repo's own README documents `uv run pytest` as its check gate, which passes.
