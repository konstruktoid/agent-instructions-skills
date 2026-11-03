I fixed `page_slice`, and all the checks now pass. The pytest suite (12 tests), ruff lint, ruff format and `ty` are all clean.

The bug was in `src/paging/slicing.py`: the end index was capped at `len(items) - 1`, which cut off the last item. The function now returns `items[start : start + per_page]`. That puts every item on exactly one page, and a page past the end returns `[]`.

I added tests for four cases: the final page holds the last item, a short final page, all pages together cover every item once, and a page past the end is empty.

- **Import order:** `ruff check` was already failing on the import order in `tests/test_slicing.py`. I ran `ruff check --fix`, which added a blank line before `from paging import ...`.
- **`ty` scope:** a plain `ty check` also scans scripts outside this project and reports 21 errors there. It also can't resolve `paging` without the source path. I ran `uv run ty check --extra-search-path src src tests` instead.
