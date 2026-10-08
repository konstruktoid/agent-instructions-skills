`Client.get` and `Client.head` now both call a new private `_with_retries(method, path)` in `src/fetcher/client.py`. It holds the single copy of the retry loop. Behaviour is unchanged: three attempts, `self.attempts` counts as before, and the last `TransportError` is re-raised when every attempt fails.

The four tests pass, and `ruff check`, `ruff format --check` and `ty check` are clean.

- **Import-order fix:** `ruff check` was already failing on import ordering in `tests/test_client.py`. I ran `ruff check --fix`, which added a blank line between the `pytest` import and the `fetcher` imports.
- **How I ran `ty`:** A plain `uv run ty check` from the workspace picked up unrelated files in a parent directory, so I ran `ty check --extra-search-path src src tests`. Without the extra path it couldn't resolve `fetcher.client`.

I didn't commit anything.
