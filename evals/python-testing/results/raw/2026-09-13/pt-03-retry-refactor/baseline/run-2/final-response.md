Scoped to this project's `src`, `ty` passes cleanly. All checks relevant to this change are green: 4/4 tests pass, `ty check src` is clean, and the sole ruff finding (`tests/test_client.py` import order) predates my edit — confirmed via `git stash`.

**Changed:** `src/fetcher/client.py` — extracted the duplicated retry loop from `get`/`head` into `_with_retries(method, path)`; both public methods now delegate to it. Attempt counting and the final raised exception on exhaustion are unchanged.
