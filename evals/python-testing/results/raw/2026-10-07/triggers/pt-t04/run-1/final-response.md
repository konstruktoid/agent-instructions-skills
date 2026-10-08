A test for `src/ledger/balance.py` belongs in **`tests/test_balance.py`**, and that file already exists.

- **Location:** the repo has a flat top-level `tests/` directory. There's no `conftest.py` and no pytest config (`pyproject.toml`, `pytest.ini`, `setup.cfg` or `tox.ini`). Nothing points to a different layout, such as tests next to the source or a `tests/ledger/` mirror of `src/`.
- **Name:** the file is `test_<module>.py`, so `balance.py` maps to `test_balance.py`. Test functions are named `test_balance_<behavior>`, as in `test_balance_sums_one_account`. They import with `from ledger.balance import balance` and use plain `assert`, with no fixtures.

**What to do:**
- **Add to the existing file.** New tests for `balance()` go in `tests/test_balance.py` and shouldn't create a parallel file. This follows the skill's rule of updating the existing test rather than adding a second one.
- **Fix the current test.** Its docstring says "Entries for other accounts are ignored", but it only calls `balance([], "cash")`. It never passes entries for another account, so it checks nothing about filtering. A real test would pass entries for two accounts and assert that only the requested one is summed.
- **Add a client test only if you change `client.py`.** It would go in a new `tests/test_client.py`, following the same mapping.

I haven't written or run any tests, since you only asked where one should go.
