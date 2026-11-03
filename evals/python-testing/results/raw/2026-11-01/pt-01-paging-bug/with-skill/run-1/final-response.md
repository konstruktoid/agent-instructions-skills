I fixed `page_slice` so every item now appears on exactly one page, and a page past the end returns `[]`. The full suite passes (13 tests), and `ruff check`, `ruff format --check` and `ty check` are clean.

**The bug:** in `src/paging/slicing.py`, the end index was `min(start + per_page, len(items) - 1)`. The `- 1` cut off the last item. It is now `items[start : start + per_page]`. Python slicing already handles a short final page and a page past the end, so no special case was needed.

**Tests added** in `tests/test_slicing.py`:
- The final partial page of the six letters at two per page is `["e", "f"]`.
- A short final page is returned whole (page 2 at four per page).
- Concatenating all pages reproduces the original list.
- Pages past the end return `[]`.

Before the fix, three of the new tests failed. The past-the-end test already passed, because the old code returned `[]` there too.

I also made two changes beyond the bug:
- I fixed an import-order error `ruff` was already reporting in `tests/test_slicing.py`, with `ruff check --fix`.
- A plain `uv run ty check` picks up the parent directory's project and reports unrelated errors from other files. To check only this repo, I ran `uv run ty check --project . --extra-search-path src src tests`.
