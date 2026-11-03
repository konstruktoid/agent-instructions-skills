I moved the retry loop into `Client._with_retries(method, path)` in `src/fetcher/client.py`, and `get` and `head` now call it with `"GET"` and `"HEAD"`. The loop body is unchanged, so the attempt count and the exception raised when every attempt fails are the same as before.

Check results:
- **pytest:** 4 passed.
- **ruff format:** clean.
- **ruff check:** it flagged an import-sorting error in `tests/test_client.py` that was there before my change. I fixed it by adding a blank line after `import pytest`, and it now passes.
- **ty:** it can't find `fetcher.client` by default because the project doesn't tell ty about `src/`. I didn't change the project config. With `uv run ty check --extra-search-path src src tests` it passes. Running `ty check` on its own also picks up files in a parent `scripts/` directory outside this repo, which I ignored.

If you want plain `ty check` to work, add the `src` search path to `pyproject.toml`.

I didn't commit anything.
