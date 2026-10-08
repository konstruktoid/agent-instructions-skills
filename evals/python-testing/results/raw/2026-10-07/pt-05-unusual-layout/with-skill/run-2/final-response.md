I added `running_balance(entries, account)` to `src/ledger/balance.py` and exported it from `ledger/__init__.py` next to `Entry` and `balance`. `uv run pytest` passes (4 tests), and `ruff check` and `ruff format --check` are clean. `ty check src` is clean too.

A bare `uv run ty check` fails, but not on this code. It picks up a parent directory's scripts, where it reports a missing `yaml` module and type errors, so I ran it on `src` only.

It returns the cumulative total after each entry for the named account, in order. Entries for other accounts are skipped, and an account with no entries gives `[]`.

I put two checks in `src/ledger/_tests/check_balance.py`, which is where `pyproject.toml` collects tests and uses the `check_*` naming. The `tests/` directory is not collected, so I left it alone. One check covers accumulation in order with another account's entries mixed in, and the other covers the empty case.

I used plain `assert` instead of the existing `_helpers.check_values`. That helper catches the `AssertionError` and only prints a mismatch, so a check using it can never fail. This also means the existing `check_balance_of_an_unknown_account_is_zero` can't fail either. I left it as is, since it's outside this request. You may want to make the helper strict once the balance rewrite lands.
