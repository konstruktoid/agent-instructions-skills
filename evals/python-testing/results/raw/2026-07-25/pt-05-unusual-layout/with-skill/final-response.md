All checks pass. Summary of changes:

- `src/ledger/balance.py`: added `running_balance(entries, account)` — returns cumulative balances after each matching entry, in order, empty list if none.
- `src/ledger/__init__.py`: exported `running_balance` alongside `Entry` and `balance`.
- `src/ledger/_tests/check_balance.py`: added `check_running_balance_accumulates_one_account` and `check_running_balance_of_an_unknown_account_is_empty`, matching the existing `check_*` convention.

Verified: `uv run pytest` (4 passed), `uv run ruff check .` / `ruff format --check .` (clean), `uv run ty check src` (clean). Note: a bare `uv run ty check` (no path) fails on an unrelated file in the *outer* git repository this workspace is nested in (`yaml` import in `../../../../../../scripts/check_skills.py`) — confirmed via `git stash` that this happens on the pre-existing baseline too, so it's a pre-existing environment quirk, not something my change introduced.
