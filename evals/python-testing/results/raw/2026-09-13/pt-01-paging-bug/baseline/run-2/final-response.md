Both pass. `ty check` isn't usable here: it walks up the directory tree, finds the outer monorepo's `pyproject.toml`, and type-checks that repo's unrelated `scripts/` instead of this package — a path-resolution artifact of this workspace being nested inside `agent-instructions-skills`, not a defect in the paging code (confirmed by scoping to `ty check src tests`, which then fails to resolve the local `paging` import for the same reason). The README's own check command is `uv run pytest`, which passes.

**Fix**: `src/paging/slicing.py:10` — `end` was clamped to `len(items) - 1` instead of `len(items)`, which both dropped the last element and made out-of-range pages behave inconsistently. Changed to `min(start + per_page, len(items))`.

**Also fixed**: `tests/test_slicing.py` had an unsorted import block (ruff `I001`), applied `ruff check --fix`.

Files changed: `src/paging/slicing.py`, `tests/test_slicing.py`.
