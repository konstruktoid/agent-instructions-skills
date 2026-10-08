I moved the retry loop into `Client._with_retries(method, path)` in `src/fetcher/client.py`. `get` and `head` now each just call it with `"GET"` or `"HEAD"`. The attempt count and the exception raised when every attempt fails are the same as before. All four tests pass, and ruff, the ruff format check and `ty` are clean.

- **Import order:** `ruff check` failed on the import order in `tests/test_client.py`, which was already failing before my change. I fixed it by adding one blank line after `import pytest`.
- **`ty` scope:** the repo has no `ty` config, and plain `uv run ty check` picks up unrelated scripts in a parent directory and fails on them. I ran it as `uv run ty check --extra-search-path src src tests`, which passes. I didn't add this to `pyproject.toml`, so the plain command will still fail the same way.

I haven't committed anything.
