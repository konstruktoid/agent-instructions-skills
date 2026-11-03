I haven't added the test yet because I couldn't find a pagination helper in this workspace. I also can't write files or run commands here: I only have read and search tools, so I couldn't add or run a test even once the code turns up.

**What the repo contains**
- Python code: just `src/ledger/balance.py`, which has `balance()` (a sum over entries), and `src/ledger/client.py`, which has `get()` (a retry loop that tries up to 3 times).
- Tests: just `tests/test_balance.py`, with one test.
- I searched every file for `page`, `paginat`, `offset` and `limit` and got no matches.
- The rest is non-Python (Go, Terraform, Ansible, CI configs).

So your fix isn't in this checkout. It may be on another branch or in a different repo, or it hasn't been saved or committed yet.

**What I need from you**
1. Where the fix is: the file path, branch or repo, or paste the function along with the before and after of the line you changed.
2. Write access (file editing and a shell) in this session, so I can add the test and run it.

**What I'll do once I have those**
- Add a test in `tests/`, following the existing pattern: flat `test_<module>.py` files, plain functions with docstrings, plain `assert`, no fixtures or mocks.
- Make it parametrized over the cases where off-by-one bugs usually show up: an empty input, a total that's an exact multiple of the page size, one item over a boundary, the first and last page, and a page past the end.
- Assert that every item appears exactly once across the pages, with none missing or duplicated.
- Confirm the test fails with your fix reverted, then run the full suite plus `ruff` and `ty` on the test file.
