Everything is in order. Summary:

- Added `running_balance(entries, account)` to `src/ledger/balance.py:17`, exported it via `src/ledger/__init__.py`.
- Added `src/ledger/_tests/check_running_balance.py`, following this repo's unusual `check_*.py`/`check_*` convention (configured in `pyproject.toml`), covering: cumulative balance per entry, ignoring other accounts, and empty result for an account with no entries.
- I used plain `assert` in the new tests rather than the existing `_helpers.check_values`, since that helper only *prints* on mismatch instead of failing the test — copying it would have made the new tests unable to catch a real bug. Worth knowing if you want that helper fixed or removed.
- Verified: `uv run pytest` → 4 passed; `uv run ruff check .` and `ruff format --check .` → clean; `uv run ty check src` → clean.
- Note: bare `uv run ty check` (no path) errors on an unrelated file (`.../agent-instructions-skills/scripts/check_skills.py`) outside this repo — a pre-existing environment quirk unrelated to this change, unaffected by scoping the check to `src`.
