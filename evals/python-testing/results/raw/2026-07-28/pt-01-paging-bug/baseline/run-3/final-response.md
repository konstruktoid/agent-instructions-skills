Third page now correctly returns `['e', 'f']` and a page past the end returns `[]` without raising.

Fixed `page_slice` in `src/paging/slicing.py:10`: `end` was capped at `len(items) - 1` instead of `len(items)`, dropping the last item and truncating the final page. Also fixed a pre-existing unsorted-import lint issue in `tests/test_slicing.py`. `pytest` (8 passed) and `ruff check` now pass; a pre-existing `ty` module-resolution error is unrelated to this bug and present on `main` before my changes.
