`ty check` with no args walks up to the outer monorepo and reports unrelated pre-existing errors there; scoped to this project's `src`, it's clean. Tests pass (8/8); the one ruff finding is a pre-existing import-order issue in `tests/test_slicing.py`, unrelated to this fix, which I left alone.

**Fix**: `src/paging/slicing.py:10` — `end` was clamped to `len(items) - 1`, dropping the last element and never returning it on any page. Changed to `len(items)`.

Only file changed: `src/paging/slicing.py`.
