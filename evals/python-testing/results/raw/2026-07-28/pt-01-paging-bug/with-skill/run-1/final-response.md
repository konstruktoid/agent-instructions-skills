All 10 tests pass, ruff is clean, and formatting is fine.

## Summary

**Bug**: `page_slice` (`src/paging/slicing.py:10`) computed `end = min(start + per_page, len(items) - 1)`. The `- 1` truncated one item off every page and made the sequence's last item unreachable on any page.

**Fix**: `end = min(start + per_page, len(items))`. Slicing with `start >= len(items)` already returns `[]` naturally, so a page past the end just works without extra handling.

**Tests added** (`tests/test_slicing.py`): extended the existing parametrized case list with `(3, 2, ["e", "f"])` (last item reachable) and `(4, 2, [])` (page past the end returns empty, no exception). Verified the first case fails against the unfixed code.

Ran the repo's checks: pytest (10 passed), `ruff check` (clean), `ruff format --check` (clean). Note: `ty check` errors on an unrelated file (`scripts/check_skills.py` in the outer eval-harness repo, missing `yaml`) due to a project-root detection quirk — confirmed this is pre-existing and identical before my changes, unrelated to the `paging` package.
