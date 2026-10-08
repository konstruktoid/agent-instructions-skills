A test for `src/ledger/balance.py` already exists at `tests/test_balance.py`, so add to that file rather than creating a new one.

- **Location:** the repo has a flat top-level `tests/` directory. It has no per-package subdirectory like `tests/ledger/`, and no `conftest.py`.
- **File name:** `test_<module>.py`, which gives `test_balance.py`. It imports with `from ledger.balance import balance`.
- **Test function names:** `test_<behavior>`, with a one-line docstring. The existing one is `test_balance_sums_one_account`.

I found no `pyproject.toml`, `pytest.ini`, `setup.cfg` or `tox.ini`. That means no `testpaths`, markers or `python_files` override, so pytest's default `test_*.py` discovery applies. I also haven't checked how `src/` gets onto the import path. `from ledger.balance import ...` only works if the package is installed or `src` is on `PYTHONPATH`. Check that before you rely on a bare `pytest` run.

If you need coverage for `src/ledger/client.py`, follow the same pattern and put it in `tests/test_client.py`.

The existing test is thin. It calls `balance([], "cash")` on an empty list, so its docstring claims more than it checks. When you change `balance`, extend `tests/test_balance.py` and update that test rather than adding a parallel file.
