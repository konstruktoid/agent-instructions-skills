Fixed and verified:

- **`src/paging/slicing.py`**: the page-end bound was `min(start + per_page, len(items) - 1)`, which excluded the last index of the sequence entirely — no page could ever contain it. Changed to `min(start + per_page, len(items))`.
- **`tests/test_slicing.py`**: added a case to the existing parametrized test for the full last page (`page=3, per_page=2` → `["e", "f"]`), plus two new tests — one confirming the final item is reachable, one confirming a page past the end returns `[]` rather than raising (Python slicing already handles this once the bound is correct). Confirmed both new tests fail against the unfixed code and pass with the fix.

Checks: `pytest` (11 passed), `ruff check` and `ruff format --check` (clean, after auto-fixing an unrelated import-order lint in the test file). `ty check` fails, but identically on the unmodified baseline — it resolves its project root to the outer `agent-instructions-skills` repo instead of this nested workspace and chokes on an unrelated file (`scripts/check_skills.py`), a pre-existing environment issue, not something caused by this change.
