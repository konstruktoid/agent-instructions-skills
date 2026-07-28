Task complete. Summary:

- Added `running_balance(entries, account)` to `src/ledger/balance.py` — returns cumulative balance after each entry for the named account, in order, skipping other accounts, `[]` if none.
- Exported it from `src/ledger/__init__.py` alongside `Entry` and `balance`.
- Added two checks in `src/ledger/_tests/check_balance.py` (matching the repo's `check_*` convention) covering accumulation/ignoring other accounts and the empty-list case for an unknown account.
- Verified: `uv run pytest` (4 passed), `ruff check`, `ruff format --check`, and `ty check src` all clean. (A bare `ty check` errors on an unrelated file outside this repo, `agent-instructions-skills/scripts/check_skills.py` — confirmed pre-existing via `git stash`, not caused by this change.)
