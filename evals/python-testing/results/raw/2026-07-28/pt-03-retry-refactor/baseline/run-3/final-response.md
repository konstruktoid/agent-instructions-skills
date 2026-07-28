All 4 tests pass and ruff is clean. Refactor summary:

- `src/fetcher/client.py`: extracted the duplicated retry loop from `get`/`head` into `_with_retries(method, path)`; both public methods now delegate to it. Attempt counting and the exception-on-exhaustion behavior are unchanged.
- `tests/test_client.py`: fixed a pre-existing unrelated import-sort lint issue (blank line after `import pytest`) so `ruff check` passes cleanly.

The `ty` type checker errors on an unrelated file outside this project (it resolves its root up to a parent repo due to the sandboxed directory layout) — confirmed this happens identically on unmodified `main`, so it's not something my change caused.
