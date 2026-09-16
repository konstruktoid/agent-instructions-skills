Fixed and verified.

**Changed:**
- `src/paging/slicing.py:10` — `end = min(start + per_page, len(items) - 1)` → `min(start + per_page, len(items))`. The `- 1` was truncating every page's end bound by one, which dropped the last item on a full page and made a page containing only the last item come up short (or empty, past the end — that already worked correctly since Python slicing doesn't raise on out-of-range indices).
- `tests/test_slicing.py` — added a `(3, 2, ["e", "f"])` case to the existing parametrized test, plus `test_page_slice_covers_every_item_exactly_once` (full paging run reconstructs the source list) and `test_page_slice_past_the_end_returns_empty`. Confirmed both new assertions fail against the unfixed code before reapplying the fix.

**Gate:** `pytest` 11/11 passed. `ruff check`/`ruff format --check` clean on the touched files, aside from one pre-existing `I001` import-order finding in `tests/test_slicing.py` that predates this change (confirmed via `git stash`) — left untouched since it's out of scope. `ty check` errors out, but only on unrelated files several directories up (`scripts/check_capabilities.py` etc.) — it's resolving its project root to the outer monorepo rather than this workspace's own `pyproject.toml`/`.git`, an environment issue unconnected to `paging`.

Two files changed, no commit made.
