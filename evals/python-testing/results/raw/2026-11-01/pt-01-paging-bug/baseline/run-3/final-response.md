I fixed `page_slice` in `src/paging/slicing.py`. Pytest, ruff and ty now pass.

**Cause:** the end index was `min(start + per_page, len(items) - 1)`. That `- 1` cut off the last item. Python slicing already stops at the end of the list, so I replaced it with `items[start : start + per_page]`. Six letters two at a time now give three full pages, and a page past the end returns `[]`.

**Tests:** I added three tests to `tests/test_slicing.py`: one for the final item, one that all pages together reproduce the list exactly once, and one for a page past the end.

**Checks:**
- **pytest:** 11 passed.
- **ruff:** one existing import-order error in the test file. I fixed it with `ruff check --fix`, which only added a blank line.
- **ty:** a plain `ty check` run from the repo reported 21 diagnostics. They are in `/repo/scripts/check_skills.py` and a `paging` import it couldn't resolve. The repo doesn't tell ty where `src` is. Run with `--extra-search-path src` on `src tests`, ty passes. I did not change the project config to make that permanent.
