I extracted the retry loop into `Client._with_retries(method, path)` in `src/fetcher/client.py`. `get` now calls it with `"GET"` and `head` with `"HEAD"`. The loop body is unchanged, so the attempt count and the last `TransportError` raised when every attempt fails are the same as before.

The checks pass: 4 pytest tests, `ruff check`, `ruff format --check`, and `ty check`.

Two things about the checks:
- **Ruff:** `ruff check` was already failing on import ordering in `tests/test_client.py`, so I added the one blank line it asked for.
- **ty:** run as plain `uv run ty check`, it reports 21 diagnostics. They come from checking files outside this repo, such as `/repo/scripts/check_skills.py`, and it also can't resolve `fetcher.client`. Scoped to `src` and `tests` with `--extra-search-path src`, it passes. I didn't change the project config.

I didn't commit anything.
