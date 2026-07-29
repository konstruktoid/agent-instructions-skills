All checks pass: `ruff check`, `ruff format --check`, `ty check src` (scoped to avoid a pre-existing, unrelated `ty` issue in an outer repo directory), and all 4 pytest checks including the 2 new ones for `running_balance`.

## Summary

Added `running_balance(entries, account)` to `src/ledger/balance.py`, exported it from `ledger/__init__.py` alongside `Entry` and `balance`, and added two `check_*` tests in `src/ledger/_tests/check_balance.py` (accumulation for one account, empty list for an unknown account) matching this repo's unusual layout — checks live in `src/ledger/_tests/`, not the empty top-level `tests/`. `ruff check`, `ruff format --check`, `ty check`, and `uv run pytest` (4/4) all pass.
