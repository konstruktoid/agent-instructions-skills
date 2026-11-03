Good news: there's already a home for it. Add the test to **`tests/test_balance.py`**, which exists now.

**Why that file:**
- **Layout:** Tests go in a top-level `tests/` directory, separate from `src/`. Nothing in the repo puts tests next to the source files or inside the package.
- **Naming:** Files are named `test_<module>.py` after the module, so `balance.py` maps to `test_balance.py`. Test functions follow a `test_<function>_<behaviour>` pattern, like the existing `test_balance_sums_one_account`. Each has a one-line docstring and uses a plain `assert`.
- **Imports:** Tests import the package by name (`from ledger.balance import balance`), not as `src.ledger...`. Follow that.

A new test for `balance.py` should be a new function in that file, such as `test_balance_ignores_other_accounts`. Don't create a second file or a new directory for it.

**Things to know before you write it:**
- **Config:** There's no `pyproject.toml`, `pytest.ini`, `setup.cfg`, `tox.ini` or `conftest.py`. That means nothing sets `testpaths`, markers or fixtures. Nothing puts `src/` on the import path either, so `from ledger...` only works if you install the package first or set `PYTHONPATH=src`. Neither CI file (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`) mentions pytest, so the tests don't run in CI.
- **Fixtures:** There's no fixture style to copy. `balance()` only reads `.amount` and `.account` from each entry, so a simple stand-in like `types.SimpleNamespace(account="cash", amount=10)` is enough. You don't need a mocking library.
- **The existing test is weak:** Its docstring says "Entries for other accounts are ignored", but it only checks that an empty list returns 0. It never tests the filtering. Update that test to include entries for other accounts rather than adding a near-duplicate next to it.

I didn't change anything, since you asked where the test should go rather than for the test itself.
