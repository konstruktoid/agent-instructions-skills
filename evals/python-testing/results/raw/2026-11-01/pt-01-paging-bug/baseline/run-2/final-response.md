I fixed `page_slice` so every item lands on exactly one page and a page past the end returns `[]`. All checks pass except one `ty` import error that was already there.

The bug was in `src/paging/slicing.py`. The end index was capped at `len(items) - 1`, which dropped the last item. Python slicing already stops at the end of the list, so I removed the cap and the function now returns `items[start : start + per_page]`.

I added three tests in `tests/test_slicing.py`:
- **Final item:** the last page includes the final item.
- **Every item once:** joining all pages gives back the original list, for page sizes 1, 2, 4 and 10.
- **Past the end:** pages beyond the last return `[]`.

Check results:
- **pytest:** 14 passed.
- **ruff check and ruff format:** clean. I ran the formatter on the test file.
- **ty:** passes when I add `--extra-search-path src`. A plain `ty check src tests` reports one unresolved `paging` import, and it did the same before my change. `ty` picks up the parent directory as the project root and doesn't find `src`. I left the `pyproject.toml` config alone.

I haven't committed anything.
