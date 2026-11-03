It should go in **`tests/test_balance.py`**. That file already exists, so add new tests to it rather than creating another one.

**What's in the repo:**
- There's one test root, `tests/`. It doesn't mirror the package structure: the test is `tests/test_balance.py`, not `tests/ledger/test_balance.py`.
- The naming pattern is `test_<module>.py` for the file. Test functions are named `test_<function>_<behavior>` (e.g. `test_balance_sums_one_account`) and each has a one-line docstring.
- Tests are plain functions using bare `assert`. There's no `conftest.py`, no fixtures, no parametrization and no mocking.
- There's no pytest config at all: no `pyproject.toml`, `pytest.ini`, `setup.cfg` or `tox.ini`. So there are no markers, `testpaths` or `addopts` to follow.

**So:**
- **File:** `tests/test_balance.py`, next to the existing test.
- **Test names:** follow `test_balance_<what it checks>`, e.g. `test_balance_ignores_other_accounts` or `test_balance_nets_debits_and_credits`.
- **Imports:** `from ledger.balance import balance`, like the existing test.

**Two things I noticed:**
1. **The existing test doesn't check what its name says.** `test_balance_sums_one_account` says "Entries for other accounts are ignored," but it only calls `balance([], "cash")`. With an empty list, the filter on account never runs. A real test needs entries for at least two accounts, using objects with `.account` and `.amount` (e.g. a small dataclass or `types.SimpleNamespace`). Fix or rename this test rather than adding a near-copy next to it.
2. **The import may fail under a plain `pytest` run.** The code lives under `src/`, but nothing puts `src` on the import path: there's no `pythonpath = ["src"]` setting and no installable package config. I haven't run it, but unless the package is installed some other way, `pytest` will probably need `PYTHONPATH=src`. Check how CI runs the tests before relying on that.

I didn't make any changes.
