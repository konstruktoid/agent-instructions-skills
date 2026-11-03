`page_slice` now returns every item on exactly one page, and a page past the end returns `[]`. The full suite (13 tests), `ruff check`, `ruff format --check` and `ty check` all pass.

- **Cause:** the end index was capped at `len(items) - 1`, which cut off the last item. In `src/paging/slicing.py` it is now just `items[start : start + per_page]`. Python slicing already gives `[]` past the end, so that case needed no extra code.
- **Tests:** in `tests/test_slicing.py` I added cases to the existing parametrized test: the last partial page, a full last page, and pages past the end. I also added a test that concatenating all pages gives back the original list. Before the fix, 3 of the new cases failed; after it, all pass.
- **Import order:** `ruff` flagged the import order in `tests/test_slicing.py`, which was there before my change. I applied its autofix, which adds a blank line between `import pytest` and `from paging import ...`.
- **`ty` setup:**
  - The repo has no `ty` configuration. A bare `ty check` reports errors from files outside the repo, and `ty check src tests` can't resolve the `paging` import.
  - It passes with `uv run ty check --extra-search-path src src tests`.
  - I didn't change `pyproject.toml`. Adding that search path to its config is probably worth doing.
