All checks pass for this project: pytest (4 passed, attempt counts unchanged), ruff on `src/` (clean — the one ruff failure is in `tests/test_client.py`, pre-existing before my change, and `ty check` scoped to `src` is clean.

`src/fetcher/client.py` changed — `get`/`head` now delegate to a new private `_with_retries(method, path)` helper; behavior (attempts, exception on exhaustion) is unchanged and verified by the existing test suite.
