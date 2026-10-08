I couldn't find a pagination helper in this workspace, so I haven't written a test.

The Python source here is only `src/ledger/balance.py` (`balance()`) and `src/ledger/client.py` (`get()`, a retry loop). Neither paginates. Searches for "paginat", "page", "offset", "limit", "chunk" and slicing found nothing. The only test file is `tests/test_balance.py`. The repo also has no `pyproject.toml` or pytest config. Your branch is `eval-harness-delegation`, and git shows only an untracked parent directory. So I can't see the fix either.

A regression test has to pin the exact boundary behavior, so I'd rather not guess at it. Can you tell me one of these?
- The file and function path, if the helper is in another branch, directory or repo.
- The helper's signature and intended semantics, for example 0- or 1-indexed pages, and what the last partial page and an out-of-range page should return.

With that, I'll follow the existing style in `tests/test_balance.py`: plain pytest functions with a docstring each, and imports from `ledger.*`. I'll add parametrized boundary cases covering the first page, the exact-multiple last page, a partial last page, an empty input and a page past the end. I'll confirm the new test fails against the pre-fix code, then run the full suite.
