I added `running_balance(entries, account)` and exported it from `ledger` next to `Entry` and `balance`. The checks pass: `pytest` ran 4 tests, all passed, and `ruff check`, `ruff format --check` and `ty check src` are clean.

- **Function:** it's in `src/ledger/balance.py`. It returns a list of cumulative totals for the named account's entries, in order, and `[]` if the account has none.
- **Tests:** I put two checks in `src/ledger/_tests/check_balance.py`, because that is the directory pytest collects and the top-level `tests/` is not collected. They cover a normal account (`[100, 70]` for `cash`) and an unknown account (`[]`).
- **`ty` scope:** a bare `ty check` also picked up unrelated scripts in a parent directory and reported 21 errors, none in this project. I ran it on `src` only.
- **Tolerant helper:** the existing `_helpers.check_values` only prints a mismatch instead of failing. I used plain `assert` in the new checks so they can actually fail. You may want to fix that helper separately, since `check_balance_of_an_unknown_account_is_zero` can't fail while it uses it.
