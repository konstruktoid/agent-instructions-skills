Manual smoke test confirms single-use, expiry, cross-token invalidation, and unknown-account/token behavior all work as required.

Files changed:
- `src/accounts/reset.py` — implemented `complete_reset`, reworked `RESET_TOKENS` to track issue time per token (supporting multiple outstanding tokens per account), added 30-minute expiry, single-use enforcement, and clearing of other outstanding tokens on success.
- `README.md` — documented the full reset flow (request → check → complete) and its guarantees.

`ruff check`, `ruff format --check`, and `ty check` all pass.
