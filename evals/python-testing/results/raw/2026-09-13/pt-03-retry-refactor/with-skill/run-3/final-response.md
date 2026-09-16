Refactor complete. `src/fetcher/client.py` now has both `get` and `head` delegate to a new `_with_retries(method, path)` helper; the retry loop, attempt counting, and last-error-raising logic are unchanged, just deduplicated.

Checks:
- `pytest`: 4 passed, unchanged.
- `ruff check`: passed, after fixing one **pre-existing** unrelated import-sort issue in `tests/test_client.py` (not something my edit touched or caused).
- `ty check`: cannot get a clean run in this environment. Per `ty check --help`, both the default project root and `--project .` "walk up the directory tree" to find `pyproject.toml`, and this workspace is nested inside a much larger monorepo (`/repo`). ty resolves that outer repo as project root and reports pre-existing errors in its unrelated `scripts/*.py` files, plus an unresolved-import on `fetcher` because the outer root isn't on the module path. None of the diagnostics reference `client.py` or `test_client.py`. I did not modify the outer repo's config to work around this — that's state outside the working tree you authorized me to change.

Files changed: `src/fetcher/client.py`, `tests/test_client.py` (import order only, via `ruff check --fix`).
