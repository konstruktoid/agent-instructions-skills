I added `running_balance(entries, account)` and exported it from `ledger`. The full suite passes (4 tests), and `ruff check`, `ruff format --check` and `ty check src` are clean.

- **Function:** it is in `src/ledger/balance.py`. It returns the cumulative balance after each entry for the named account, in order. It skips other accounts' entries and returns `[]` if the account has none.
- **Tests:** I added two checks to `src/ledger/_tests/check_balance.py`, following that file's `check_*` naming. One covers the cumulative result and the skipping of other accounts, the other covers an unknown account. They use plain `assert`.
- **`ty` scope:** a bare `ty check` also picked up unrelated scripts in a parent directory and reported 21 errors there. None are in this repo, so I ran it on `src` only.
- **Tolerant helper:** `_helpers.check_values` in the existing tests only prints a mismatch instead of failing. The existing unknown-account check for `balance` uses it, so it can't fail. I left it alone and didn't use it for the new checks.
- **Untracked files:** `__pycache__` directories now appear as untracked. There is no `.gitignore`, and I didn't add one or commit anything.
