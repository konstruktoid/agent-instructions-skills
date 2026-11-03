`running_balance(entries, account)` is now in `src/ledger/balance.py` and exported from `ledger/__init__.py` next to `Entry` and `balance`. It returns the cumulative total after each matching entry, in order. Other accounts are skipped, and an account with no entries gives `[]`.

I added two checks to `src/ledger/_tests/check_balance.py`, which is where `pyproject.toml` collects `check_*` functions. One covers the cumulative result (`[100, 70]` for `cash`), the other the empty list for an unknown account.

`uv run pytest` passes (4 tests), and `ruff check`, `ruff format --check` and `ty check src` are all clean. I committed nothing.

- **`ty` scope:** Run from `src/ledger`, `ty check` picked up unrelated files in a parent directory and reported errors there. From the repo root, scoped to `src`, it is clean.
- **Tolerant helper:** `_tests/_helpers.check_values` only prints a mismatch and never fails, so the new checks use plain `assert`. The existing "unknown account" check for `balance` still goes through that helper, so it can't fail. I left it alone.
- **Leftover files:** `tests/` is empty on purpose, and I added nothing there. `__pycache__` directories showed up untracked under `src/ledger`.
