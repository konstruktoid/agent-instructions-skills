`page_slice` now returns every item on exactly one page, and a page past the end gives an empty list. The cause was `end = min(start + per_page, len(items) - 1)`, which cut off the last item. I replaced it with `items[start : start + per_page]`, since slicing already stops at the end of the list.

All checks pass on the repo's own files:
- **pytest:** 8 passed.
- **ruff check:** passed. This needed one import-order fix in `tests/test_slicing.py`, a blank line after `import pytest`.
- **ruff format:** applied to `src/paging/slicing.py`.
- **ty:** passes when run as `uv run ty check --extra-search-path src src tests`.

A plain `uv run ty check` fails for two reasons that don't come from the repo's code. The workspace sits inside a larger repo, so ty also scans that parent's `scripts/check_skills.py` and reports 14 errors there. Run from inside `tests/`, it also can't find the `paging` package without the extra search path. I didn't touch either issue.

I didn't add a regression test for the six-letters, two-per-page case or the page-past-the-end case. The existing tests pass, but I didn't check whether they cover those two cases.
