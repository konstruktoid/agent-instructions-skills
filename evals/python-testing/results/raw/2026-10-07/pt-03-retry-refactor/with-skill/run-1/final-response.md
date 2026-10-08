I extracted the retry loop into `Client._with_retries(method, path)` in `src/fetcher/client.py`. `get` and `head` now just call it with `"GET"` and `"HEAD"`. The loop body is unchanged, so the attempt count and the last-error re-raise behave as before. All 4 existing tests pass, and ruff and ty report no problems.

I didn't add a test, since the existing ones already cover the retry, give-up and HEAD paths.

- **Import-order fix in the test file:** `ruff check` was flagging `tests/test_client.py` for import ordering, so I applied `ruff --fix`. It only added a blank line between the `pytest` and `fetcher` imports.
- **ty needed a search path:** run plainly, ty couldn't resolve `fetcher.client`. I ran it as `uv run ty check --extra-search-path src src tests`. I didn't change the project config.
- **Untracked `__pycache__` directories:** the test run left `src/fetcher/__pycache__/` and `tests/__pycache__/` in the working tree. I didn't commit anything.
