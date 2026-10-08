A test for `src/ledger/balance.py` belongs in `tests/test_balance.py`, and that file already exists.

- **Location:** `tests/` is a flat directory at the repo root, next to `src/`. It has no `tests/ledger/` subdirectory mirroring the package.
- **Name:** `test_balance.py`, which is `test_<module>.py` for `balance.py`. Test functions follow `test_<behavior>`, for example `test_balance_sums_one_account`. The existing tests have docstrings and import with `from ledger.balance import balance`.
- **What to do:** Add new cases to `tests/test_balance.py` rather than creating a second file or a new directory. If you change the behavior of `balance`, update the existing test instead of adding a parallel one.

I found no `pyproject.toml`, `pytest.ini`, `setup.cfg`, `tox.ini` or `conftest.py` in the repo. Nothing there sets `testpaths`, markers or shared fixtures, so I haven't checked how the tests get run or how `ledger` gets onto the import path. The one existing test is only a stub. It asserts `balance([], "cash") == 0`, and its docstring says "Entries for other accounts are ignored", which the empty list doesn't exercise.

I haven't run anything, since you only asked about placement.
