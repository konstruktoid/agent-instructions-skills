Added `running_balance(entries, account)` to `src/ledger/balance.py`, exported it from `src/ledger/__init__.py`, and added checks in `src/ledger/_tests/check_balance.py` following the repo's `check_*` convention (checks live under `src/ledger/_tests/`, not the empty top-level `tests/`, per `pyproject.toml`/`README.md`).

Verified:
- `uv run pytest` — all 5 checks pass (3 new + 2 existing)
- `uv run ruff check .` — passes
- `uv run ty check` — has one pre-existing unrelated error from outside this project (an outer fixtures repo file importing `yaml`); confirmed via `git stash` that it exists on the clean baseline too, unaffected by these changes
