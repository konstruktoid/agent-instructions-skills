`Client.get` and `Client.head` now both call a private `_with_retries(method, path)` helper in `src/fetcher/client.py`. The loop, the `attempts` counting and the re-raise of the last `TransportError` are unchanged. The `MAX_ATTEMPTS` limit of 3 is also the same.

All of these pass:
- `pytest`: 5 passed.
- `ruff check`: clean, after one fix described below.
- `ruff format --check`: clean.
- `ty check`: clean on `src` and `tests`. A bare `uv run ty check` also picks up files outside this repo, and without `--extra-search-path src` it can't resolve `fetcher.client`. I ran it with `--project . --extra-search-path src src tests`. The result is the same with my changes stashed.

I made two changes beyond the refactor:
- **New test:** `test_head_gives_up_after_the_attempt_limit` in `tests/test_client.py`. Only `get` had a give-up test before, so the `head` failure path (3 attempts, then `TransportError`) had no coverage.
- **Import-order fix:** `ruff check` flagged an unsorted import block in `tests/test_client.py`, which was already there before my edits. I applied the auto-fix, which adds a blank line between `import pytest` and the `fetcher` imports.

The run also left untracked `__pycache__` directories under `src/fetcher/` and `tests/`. I didn't commit anything.
