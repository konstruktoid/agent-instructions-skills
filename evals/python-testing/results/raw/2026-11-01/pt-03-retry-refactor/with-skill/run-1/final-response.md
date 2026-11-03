I extracted the retry loop into `Client._with_retries(method, path)`, and `get` and `head` now just call it with `"GET"` and `"HEAD"`. The loop body is the same as before, so the attempt count (`MAX_ATTEMPTS = 3`) and the last `TransportError` raised after the final failure are unchanged. All four checks now pass: pytest (5 passed), `ruff check`, `ruff format --check` and `ty check src tests`.

Two checks were already failing on the baseline, before my change, and I fixed both:
- **ruff:** the import block in `tests/test_client.py` was out of order (I001), and I applied ruff's autofix.
- **ty:** it couldn't resolve `fetcher.client`, so I added `[tool.ty.environment] extra-paths = ["src"]` to `pyproject.toml`.

I also added `test_head_gives_up_after_the_attempt_limit`. The existing tests only covered the all-attempts-fail path through `get`, and `head` now depends on the shared helper.

`__pycache__` directories are showing up as untracked and the repo has no `.gitignore`. I haven't committed anything.
