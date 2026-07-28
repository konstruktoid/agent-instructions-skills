Fixed and verified:

- **Bug**: `src/paging/slicing.py` — `end = min(start + per_page, len(items) - 1)` off-by-one dropped the last item and made it unreachable. Changed to `len(items)`. Python slicing already returns `[]` when `start > end`, so past-the-end pages work with no extra check needed.
- **Tests**: added a case covering the last page (`(3, 2, ["e", "f"])`) and a new test for a page past the end returning `[]`. Confirmed the new case fails on the unfixed code, passes after the fix.
- **Checks**: `pytest` (10 passed), `ruff check`, `ruff format --check`, and `ty check` all pass. `ty check` was actually broken pre-existing (couldn't resolve the `paging` import because only pytest's `pythonpath` config pointed at `src/`, not ty's) — added a matching `[tool.ty.environment] extra-paths = ["src"]` to `pyproject.toml` so `ty` sees the same layout. Also let ruff auto-fix a pre-existing import-order lint in the test file.
