Put it in **`tests/test_balance.py`**. That file already exists, so add new test functions there rather than creating a new file.

What the repository does now:

- **Layout:** there's one flat `tests/` directory at the root. It doesn't copy the `src/ledger/` structure, so the convention is `tests/test_<module>.py`, not `tests/ledger/test_balance.py`. There's no `conftest.py` and no test configuration in `pyproject.toml`, `pytest.ini`, `setup.cfg` or `tox.ini`, so nothing overrides pytest's default `test_*.py` discovery.
- **Naming:** test functions are named `test_balance_<behavior>`, like the existing `test_balance_sums_one_account`. Each has a one-line docstring and uses plain `assert`, with no fixtures or mocks. New tests should follow the same pattern, for example `test_balance_ignores_other_accounts` or `test_balance_nets_debits_and_credits`.
- **Style:** the test imports the public function directly (`from ledger.balance import balance`). Write new tests against `balance()` the same way.

Two things I noticed while looking:

1. **The existing test doesn't check what it claims.** Its docstring says "Entries for other accounts are ignored", but it only calls `balance([], "cash")` on an empty list. A test with entries for several accounts would cover that claim. You could add it as a new test, or fix this one and rename it to match.
2. **The import may fail depending on how you run it.** The test imports `ledger` from `src/`, but there's no config that adds `src` to the path. Unless the package is installed (for example with `pip install -e .`), running it probably needs `PYTHONPATH=src pytest`. I didn't run the suite to confirm this.
