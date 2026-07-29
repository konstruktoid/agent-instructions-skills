All checks pass: ruff, ty, and pytest (8 tests).

Fixed `page_slice` in `src/paging/slicing.py:10` — the end index was computed as `min(start + per_page, len(items) - 1)`, which off-by-one truncated the last item on every page and made it unreachable. Changed to `min(start + per_page, len(items))`. Out-of-range pages already return `[]` naturally via Python slice semantics, no extra guard needed. Also fixed a pre-existing unsorted-import lint failure in `tests/test_slicing.py` via `ruff check --fix`.
