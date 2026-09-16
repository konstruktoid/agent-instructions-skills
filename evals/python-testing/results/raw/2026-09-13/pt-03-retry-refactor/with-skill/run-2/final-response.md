Existing tests already cover attempt count, retry-then-succeed, exhaustion, and both methods — all 4 pass unchanged, confirming behavior is preserved. No new tests needed since this is a pure internal refactor with no new observable behavior.

**Changed:** `src/fetcher/client.py` — extracted the shared retry loop from `get`/`head` into `_with_retries(method, path)`.

Pytest and ruff pass on the changed file. Two pre-existing failures on `main` are unrelated to this change and I left them alone: `ruff` flags an unsorted import in `tests/test_client.py`, and `ty check` can't resolve the `fetcher` package (it's treating the outer `agent-instructions-skills` git root as first-party instead of this nested project).
