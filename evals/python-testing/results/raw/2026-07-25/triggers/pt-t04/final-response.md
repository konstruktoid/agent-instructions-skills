A test already exists: `tests/test_balance.py`, importing `from ledger.balance import balance`.

The repository puts tests in a top-level `tests/` directory mirroring the package structure (not nested `tests/ledger/`), with one file per module named `test_<module>.py`. So a test for `src/ledger/balance.py` belongs at **`tests/test_balance.py`** — which is exactly the file that's already there.
