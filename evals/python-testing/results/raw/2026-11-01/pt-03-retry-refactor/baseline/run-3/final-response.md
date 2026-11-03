I extracted the retry loop into `Client._with_retries(method, path)` in `src/fetcher/client.py`. `get` and `head` now just call it with `"GET"` and `"HEAD"`. The loop body is unchanged, so the attempt count and the exception raised when every attempt fails are the same as before.

All checks pass:
- **pytest:** 4 passed.
- **ruff check and format:** clean.
- **ty:** clean, but only when I ran `uv run ty check --extra-search-path src src tests`. A plain `uv run ty check` can't resolve `fetcher.client` in `tests/test_client.py` and reports a diagnostic on that import.

Ruff was also flagging an import-order error in `tests/test_client.py`, a file I hadn't touched. I fixed it with `ruff check --fix`, which added one blank line there.

I didn't commit anything.
