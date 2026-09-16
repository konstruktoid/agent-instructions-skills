`src/fetcher/client.py` passes lint on its own, and all 4 tests pass. The ruff failure on `tests/test_client.py` is pre-existing (unsorted imports) and predates my change — confirmed via `git status` showing only `client.py` modified.

Refactored `get`/`head` in `src/fetcher/client.py` to share a new `_with_retries(method, path)` helper; behavior (attempt count, exception on exhaustion) is unchanged. Tests pass (4/4); the one ruff finding is a pre-existing import-order issue in `tests/test_client.py`, not touched by this change — flag if you want that fixed too.
