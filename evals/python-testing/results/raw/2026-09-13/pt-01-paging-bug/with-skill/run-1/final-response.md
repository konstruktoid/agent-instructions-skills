**Files changed:**
- `src/paging/slicing.py` — one-line fix: `end` now caps at `len(items)`, not `len(items) - 1`.
- `tests/test_slicing.py` — added a `(3, 2, ["e", "f"])` case, a dedicated last-item test, and a past-the-end-returns-empty test; also fixed a pre-existing unsorted-import lint failure in this file (unrelated to the bug, caught by the gate since I touched the file).

Verified the new tests fail against the unfixed code, then pass after the fix. Full gate green: `pytest` (11 passed), `ruff check`, `ruff format --check`, `ty check` (scoped with `--extra-search-path src` — `ty` otherwise misresolves its project root to the outer eval-harness repo, a pre-existing quirk confirmed on the unmodified fixture, unrelated to this change).

Task is done — recommend `/clear` before starting anything unrelated.
