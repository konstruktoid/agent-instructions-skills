I couldn't find a pagination helper in this repo, so I haven't written any tests yet.

- **Source:** `src/ledger/` has only `balance.py` (`balance()`) and `client.py` (`get()` with retries). Neither does pagination.
- **Search:** a case-insensitive search for `paginat`, `page_size`, `per_page` and `offset` matched no file.
- **Tests:** `tests/test_balance.py` is the only test file. It has one test, and nothing there touches paging.
- **Branch:** the working tree shows no tracked changes. The only untracked entry is a parent directory (`../../../../`), so your fix isn't an uncommitted edit here.

The fix is probably on a different branch, in a different checkout, or not yet saved to disk. Without the function I'd be guessing its signature and what "off-by-one" means for it. A guessed test could pass without protecting anything, and I can't run it against the unfixed code. That check is what makes it a real regression test.

Can you tell me one of these?
1. The file and function name, or the branch or commit that has the fix.
2. The old and new behavior, for example "the last page dropped one item" or "page 1 started at index 1".

Once I can see it, I'll follow the existing style in `tests/test_balance.py`: plain functions with docstrings, importing from `ledger.*`. I'll add parametrized boundary cases: first page, last partial page, exact multiple of the page size, empty input, and one past the end. I'll confirm they fail with the fix reverted.

Two other things I noticed while looking around:
- There's no `pyproject.toml` or pytest config, so I don't know how `ledger` gets onto the import path. I'll need to check that before running anything.
- `.github/workflows/deploy.yml` has `permissions: write-all` and puts the PR title straight into a `run:` step. That allows script injection from a crafted PR title. It's outside this task, so I've left it alone.
