Behavior verified: single-use, unknown, and expired tokens all correctly return `False`, and a valid reset succeeds.

Files changed:
- `src/accounts/reset.py` — implemented `complete_reset`, added expiry/issued-at tracking to `RESET_TOKENS`, updated `check_token` to enforce the 30-minute TTL.
- `README.md` — documented the full reset flow (request → complete, single-use, expiry, `False` on failure).

`ruff check` and `ty check` both pass. No test suite exists in this repo to run beyond that.
