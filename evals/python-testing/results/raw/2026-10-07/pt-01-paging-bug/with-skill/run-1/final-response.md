`page_slice` now returns every item on exactly one page, and a page past the end returns `[]` instead of raising. `uv run pytest` passes (16 tests), as do `ruff check`, `ruff format --check` and `ty check`.

**Cause:** the end index was capped at `len(items) - 1`, which cut off the last item. `page_slice` in `src/paging/slicing.py` now returns `items[start : start + per_page]`. Python slicing already clamps at the end of the list.

**Tests:** I added three tests to `tests/test_slicing.py`:
- The final item is on the last page.
- Concatenating all pages gives back the original list, for page sizes 1, 2, 4, 6 and 10.
- Pages 4 and 100 return `[]`.

Six of these failed against the old code. They all pass with the fix.

**Other checks:**
- `ruff check` was already flagging an import-order error in `tests/test_slicing.py` before my change, so I fixed that too.
- A plain `ty check` picked up files outside this project, which fail on their own errors. I ran `ty check --extra-search-path src src tests` instead, which passes. Without the search path, `ty` can't resolve the `paging` import.
