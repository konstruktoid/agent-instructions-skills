`page_slice` now returns the final item. Paging six letters two at a time gives `a b`, `c d`, `e f`, and a page past the end returns `[]`. The 16 tests in the suite pass, and `ruff check` and `ruff format --check` are clean.

The cause was in `src/paging/slicing.py`. The end index was capped at `len(items) - 1`, so the last item was never included. I replaced it with `items[start : start + per_page]`. Python slicing already clamps at the end, so an out-of-range page comes back empty without raising.

**Tests:** I added cases to `tests/test_slicing.py` for the full last page, a short last page, and a page past the end. A new test also checks that concatenating all pages reproduces the original list. I ran them before the fix and seven failed. Both last-page cases and all five concatenation cases failed, as expected. The past-the-end case already passed on the old code, so it only guards against regressions.

**`ty`:** `ty check` reports `paging` as unresolved in the tests. The same single error appears with my changes stashed, so it was there before. `pyproject.toml` sets `pythonpath = ["src"]` for pytest only, and `ty` doesn't read it. With `--extra-search-path src` it passes, and I left the config alone. Run from the workspace without a path, `ty` also picks up scripts from a parent directory outside the repo, so I scoped it to `src tests`.

**Import order:** `ruff --fix` added a blank line between `import pytest` and `from paging import ...` in the test file, since it treats `paging` as first-party.
