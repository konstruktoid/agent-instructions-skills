`Client.get` and `Client.head` now both call a new private `_with_retries(method, path)` in `src/fetcher/client.py`. The loop is otherwise unchanged. It still makes up to `MAX_ATTEMPTS` (3) attempts, increments `self.attempts` on each, and re-raises the last `TransportError` if all of them fail.

The repository's checks pass:
- **pytest:** all 4 tests pass.
- **ruff:** it flagged an import-order error in `tests/test_client.py`, which I fixed by adding the blank line between the `pytest` import and the first-party imports. That is the only change outside the refactor.
- **ty:** passes on `src` and `tests` with `--extra-search-path src`. A bare `uv run ty check` does not work here. It picks up the parent `aisk` directory and reports 14 diagnostics in `scripts/check_skills.py`, which is outside this repo. Without the extra search path it also can't resolve `fetcher.client`.

The test run left `__pycache__` directories untracked. I didn't add or commit anything.
