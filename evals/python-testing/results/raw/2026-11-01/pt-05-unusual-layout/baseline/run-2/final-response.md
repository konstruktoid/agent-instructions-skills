I added `running_balance(entries, account)` to `src/ledger/balance.py`. It's exported from `ledger/__init__.py` next to `Entry` and `balance`.

It returns the cumulative balance after each entry for the named account, in order. Entries for other accounts are skipped, and an account with no entries gives `[]`.

I added two checks to `src/ledger/_tests/check_balance.py`, using plain `assert`. One covers the cumulative case (`[100, 70]` for `"cash"`), the other the empty case.

- **pytest:** 4 passed.
- **`ruff check` and `ruff format --check`:** clean.
- **`ty check src`:** clean.
- **Bare `ty check`:** reports 21 diagnostics, all in files outside this repo (`/repo/scripts/` and `run_eval.py`). It scans a parent directory, so I left those alone.

`_tests/_helpers.py::check_values` never fails. It catches the `AssertionError` and prints a "mismatch" message, so any check that uses it passes even when the values differ. The existing unknown-account check in `check_balance.py` goes through it. I didn't use it for the new checks, and I didn't change it, since that's outside what you asked for. You'll probably want to make it a strict assert.
