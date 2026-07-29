Refactor complete. `get` and `head` now both delegate to a new private `_with_retries(method, path)` helper that contains the single copy of the retry loop — behavior (attempt count, retry logic, and raising the last `TransportError` on exhaustion) is unchanged. I also fixed a pre-existing, unrelated ruff import-order issue in `tests/test_client.py` so the full check suite is clean.

All checks pass (run via the local `./.venv/bin/python`, since `.venv/bin/activate` had a stale hardcoded path from a different fixture and would silently invoke the wrong interpreter):
- `pytest`: 4 passed
- `ruff check`: all checks passed
- `ty check`: all checks passed
