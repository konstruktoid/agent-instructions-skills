I fixed `page_slice`, and pytest, ruff and `ty` now all pass.

**The bug:** in `src/paging/slicing.py`, the end index was `min(start + per_page, len(items) - 1)`. The `- 1` cut off the last item. The `min` wasn't needed anyway, because Python slicing already stops at the end of the list. It now returns `items[start : start + per_page]`. A page past the end gives `[]` instead of raising.

**Tests:** I added cases in `tests/test_slicing.py` for these:
- The third page of six letters at two per page is `["e", "f"]`.
- Page 2 at four per page is `["e", "f"]`.
- Pages past the end are empty.
- Concatenating every page gives back the original list, so each item is on exactly one page.

**Checks:**
- **pytest:** 13 passed.
- **ruff:** it reported an import-order error in `tests/test_slicing.py`, which was there before my change. I fixed it with `--fix`. `ruff format --check` is clean.
- **`ty`:** a plain `uv run ty check` picks up a parent directory's project. It reports 14 diagnostics, none in this repo, and it can't resolve `paging`. Run as `uv run ty check --project . --extra-search-path src src tests`, it passes cleanly.

I haven't committed anything. `__pycache__` directories are untracked in the working tree.
