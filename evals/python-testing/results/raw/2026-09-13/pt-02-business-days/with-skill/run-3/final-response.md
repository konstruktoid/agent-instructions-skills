Done. Files changed: `src/tempo/calendar.py`, `src/tempo/__init__.py`, `tests/test_calendar.py`.

- Added `business_days_between(start, end)` in `calendar.py`, built on the existing `is_weekend`/`is_holiday` helpers, and exported it from `__init__.py` alongside the others.
- Fixed a pre-existing bug in `is_holiday`: it compared a `datetime.date` against `HOLIDAYS`, a list of ISO strings, so it always returned `False`. Without that fix, `business_days_between` couldn't satisfy the "not a company holiday" requirement, so it was in scope. Confirmed the new holiday tests fail against the unfixed version, then verified they pass with the fix.
- `pytest` (12 passed), `ruff check`, `ruff format --check` all pass. `ty check` also passes — run bare it reports 12 unrelated diagnostics against `agent-instructions-skills/scripts/*.py`, because this workspace sits nested inside that outer repo's own `pyproject.toml`/`[tool.ty]` config and `ty` walks up past our own `pyproject.toml` to find it. I confirmed via an isolated copy outside that tree that `ty check` is clean on this repo on its own; this is an eval-harness nesting artifact, not something my change caused.

Task's done — recommend `/clear` before starting anything unrelated.
