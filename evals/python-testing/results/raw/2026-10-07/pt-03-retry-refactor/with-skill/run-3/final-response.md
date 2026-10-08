`Client.get` and `Client.head` now both call a new private `_with_retries(method, path)` in `src/fetcher/client.py`. The loop is unchanged, so the attempt count and the exception raised when every attempt fails are the same as before.

Pytest passes (4 tests), and `ruff check` and `ruff format --check` pass. `ty check` also passes, but only when I point it at this project with `--project . --extra-search-path src src tests`. A bare `uv run ty check` picks up files from the parent directory and reports 14 errors, none of them in this repo.

`ruff check` was already failing on an unsorted import block in `tests/test_client.py`, which I didn't touch. I ran `ruff check --fix`, which reordered those imports. That means the diff includes one change to `tests/test_client.py` that has nothing to do with the refactor.

I didn't add a test. The existing tests already cover this retry behaviour for both methods.
