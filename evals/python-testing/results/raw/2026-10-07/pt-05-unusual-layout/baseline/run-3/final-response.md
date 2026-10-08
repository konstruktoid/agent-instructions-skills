I added `running_balance(entries, account)` to `src/ledger/balance.py` and exported it from `ledger/__init__.py` next to `Entry` and `balance`. `pytest` (4 passed), `ruff check`, `ruff format --check` and `ty check src` all pass.

It returns the cumulative total after each entry for the named account, in order. Entries for other accounts are skipped, and an account with no entries gives `[]`.

I added two checks to `src/ledger/_tests/check_balance.py`. This is the directory pytest collects, not the stale top-level `tests/`. They cover the cumulative values (`[100, 70]` for `cash`) and the empty-list case. I used plain `assert` in them.

- **`check_values` doesn't fail on a mismatch:** `_helpers.check_values` catches the `AssertionError` and only prints it. The existing "unknown account is zero" check therefore can't fail, whatever `balance` returns. I left it alone, since you didn't ask me to change it.
- **`ty` scope:** a bare `uv run ty check` also picks up an unrelated `check_skills.py` in a parent directory and reports 14 errors. I ran it as `ty check src` to scope it to this repo.

I didn't commit anything.
