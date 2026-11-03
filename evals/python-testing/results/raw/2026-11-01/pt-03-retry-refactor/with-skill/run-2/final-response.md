`Client.get` and `Client.head` now both call a new private `_with_retries(method, path)` in `src/fetcher/client.py`, and pytest, ruff and ty all pass.

The loop is copied over unchanged. It still makes up to `MAX_ATTEMPTS` (3) attempts, increments `self.attempts` on each one, and raises the last `TransportError` if every attempt fails. The four existing tests cover this: success, retry-then-succeed, the 3-attempt limit with the final error raised, and HEAD reaching the transport as HEAD. I added no tests, because a pure refactor with those behaviours already covered doesn't need new ones.

- **Import-order fix:** `ruff check` was already failing before my change, with an import-order error (I001) in `tests/test_client.py`. I fixed it with `ruff check --fix`, which only adds a blank line after `import pytest`.
- **ty:** I ran it as `ty check --extra-search-path src src tests`. A bare `ty check` can't resolve `fetcher`, because `pyproject.toml` doesn't tell ty about `src`.

`git status` also shows untracked `__pycache__` directories from the test runs. I left them uncommitted, and I haven't committed anything.
