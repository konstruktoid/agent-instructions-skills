`running_balance(entries, account)` is added to `src/ledger/balance.py` and exported from `ledger/__init__.py` next to `Entry` and `balance`. It returns the cumulative total after each entry for that account, in order. It skips other accounts' entries and returns `[]` if the account has none.

`uv run pytest` passes with 4 tests (2 existing, 2 new), and `ruff check` and `ruff format --check` are clean. `ty check src` is clean too. A bare `ty check` also picks up a parent directory outside this repo and reports 14 errors there, none in this code.

I added the two tests to `src/ledger/_tests/check_balance.py`, named `check_*` as `pyproject.toml` requires. They cover the in-order cumulative totals for one account and the empty list for an unknown account. I did not run them against code without the function. They are new tests for a new function, and both import it.

The repo's own helper `_helpers.check_values` only prints a mismatch instead of failing. The existing `check_balance_of_an_unknown_account_is_zero` therefore passes even when the values differ. I used plain `assert` in the new tests and left the helper and that old check as they were. You may want to make the helper strict.

The `__pycache__` directories are untracked. I made no commit.
