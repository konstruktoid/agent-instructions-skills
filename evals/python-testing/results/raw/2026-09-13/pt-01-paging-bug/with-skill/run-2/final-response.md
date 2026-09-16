Full suite (11 tests), `ruff check`, and `ruff format --check` all pass. `ty check` shows the same failure on the unmodified baseline (it misresolves its first-party root to the outer eval-harness repo rather than this workspace), so it's a pre-existing environment issue, not something this change introduced.

Files changed:
- `src/paging/slicing.py` — fixed the off-by-one: the page's end index was capped at `len(items) - 1` instead of `len(items)`, which dropped the last item and, for `per_page=1`, could make `end < start` and return the wrong slice. Python slicing already yields `[]` for a past-the-end `start`, so no extra bounds check was needed for that case.
- `tests/test_slicing.py` — added a case for a page landing exactly on the sequence tail, a dedicated test asserting the final partial page includes the last item, a test for a page past the end returning `[]`, and fixed a pre-existing import-order lint violation.

Recommend `/clear` before starting unrelated work.
