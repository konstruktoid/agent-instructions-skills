I added `running_balance(entries, account)` to `src/ledger/balance.py` and exported it from `ledger/__init__.py` next to `Entry` and `balance`. It returns the cumulative balance after each entry for that account, in order. It skips other accounts' entries and returns `[]` when the account has none.

I added two checks to `src/ledger/_tests/check_balance.py`: one for the cumulative values and one for an unknown account.

- **pytest:** 4 passed.
- **ruff:** lint and format both pass.
- **ty:** passes on `src`. A bare `ty check` run from the workspace reported 21 diagnostics. I didn't open them all. The ones I listed are in `run_eval.py` and `scripts/` under `/repo/`, outside this repo, and none are in the ledger code.

`_helpers.check_values` catches `AssertionError` and prints a mismatch instead of failing. The existing unknown-account check uses it, so that check can never fail. I used plain `assert` in the new checks so they fail on a real mismatch, and I left the helper and the existing check unchanged.
