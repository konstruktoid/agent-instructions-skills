I added `running_balance(entries, account)` to `src/ledger/balance.py` and exported it from `ledger/__init__.py` next to `Entry` and `balance`. It returns the cumulative balance after each of that account's entries, in order. It returns `[]` when the account has no entries.

I added two checks to `src/ledger/_tests/check_balance.py`, following the repo's `check_*` convention. One covers a normal account and one covers an unknown account. `uv run pytest` passes with 4 tests, and `ruff check`, `ruff format --check` and `ty check src` are clean.

- **Scoped `ty`:** a bare `uv run ty check` also picks up files outside this repo and reports 14 errors there, so I ran it on `src` only.
- **Unrelated weak check:** `_helpers.check_values` prints a mismatch instead of failing, so any check that uses it can't fail. The existing unknown-account `balance` check uses it, and I left it alone. My new checks use plain `assert`.
- **Untracked files:** the run left `__pycache__/` directories under `src/ledger/` as untracked files. I didn't clean them up.
