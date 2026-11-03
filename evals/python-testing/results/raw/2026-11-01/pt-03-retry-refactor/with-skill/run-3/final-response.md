`Client.get` and `Client.head` now both call a new private `_with_retries(method, path)` helper in `src/fetcher/client.py`. The helper holds the one retry loop, so the attempt count (`MAX_ATTEMPTS`) and the re-raise of the last `TransportError` are unchanged.

All four checks pass now:
- **Tests:** `pytest` gives 4 passed. I didn't add a test, because the existing ones already cover success, retry-then-succeed, giving up after the attempt limit, and HEAD.
- **Lint:** `ruff check` passed after one fix, and `ruff format --check` was already clean. The fix was an import-sort error in `tests/test_client.py` that was there before my change. I fixed it with `ruff check --fix`, which added a blank line between the `pytest` import and the `fetcher` imports.
- **Types:** `ty check` passes when run as `uv run ty check --extra-search-path src src tests`. Without the extra search path it can't resolve `from fetcher import Client`, because the repo only sets `pythonpath = ["src"]` for pytest. Left to default, it also picked up an unrelated directory higher up the tree.
