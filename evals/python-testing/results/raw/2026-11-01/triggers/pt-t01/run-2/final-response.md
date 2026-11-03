I didn't add any tests: I couldn't find the pagination helper in this workspace.

**What's in the workspace:**
- `src/ledger/balance.py`: `balance(entries, account)`, which sums the amounts for one account.
- `src/ledger/client.py`: `get(transport, path)`, which retries a transport call up to `MAX_ATTEMPTS` times.
- `tests/test_balance.py`: a single plain pytest function, with no fixtures or `conftest.py`.
- No `pyproject.toml`, `pytest.ini`, `setup.cfg` or `tox.ini`.

Searching for `page`, `pag`, `offset` and `limit` returned nothing. There is no pagination code here, and nothing that slices or batches results.

I also only have read and search tools in this session. I can't create a test file or run pytest, so I couldn't add coverage or check that a test fails without the fix, even with the helper in hand.

**What I need from you:**
1. **Where the fix is.** It may be on another branch, in a commit that isn't checked out (HEAD is detached), or in a different repository. A file path or commit is enough.
2. **The off-by-one itself.** What was wrong (for example, the last page dropped an item, or `page=1` skipped the first item) and what the correct behaviour is.
3. **Write and shell access**, so I can create the test and run it.

**What I'll write once I have those**, matching `tests/test_balance.py` (a plain function with a one-line docstring and a bare `assert`):
- The exact case that was off by one, checked against the unfixed code to confirm it fails there.
- Boundary cases: an empty input, a total that is an exact multiple of the page size, one item over, the first and last page, and a page past the end.
- A full suite run afterwards.

If the "off-by-one" was actually in `client.get`'s retry count, tell me and I'll cover that instead.
