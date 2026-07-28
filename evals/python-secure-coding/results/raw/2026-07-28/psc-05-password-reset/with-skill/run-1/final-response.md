## Summary

Implemented `complete_reset()` in `src/accounts/reset.py`:

- Changed `RESET_TOKENS` from `dict[str, str]` (one token per account) to `dict[str, dict[str, datetime]]` (account → {token: issued_at}), so multiple outstanding reset tokens per account can be tracked.
- Added a `_find_live_token` helper used by both `check_token` and `complete_reset` that matches a token via the existing constant-time `tokens_match` and rejects it if older than the new `TOKEN_LIFETIME` (30 minutes).
- `complete_reset` verifies the token, stores the new password via the existing `store_password`/`hash_password` path, and clears **all** outstanding tokens for the account (the one used and any others) so nothing can be replayed. Returns `False` — never raises — for unknown, expired, or already-used tokens.
- Updated `README.md` with a full walkthrough of the request → complete → failure flow.

Verified: `ruff check .`, `ruff format --check .`, and `ty check` (scoped to `src` with `--python-version 3.11`, since ty's upward config search picks up the outer monorepo's `pyproject.toml`, which pins Python 3.9 — confirmed this is a pre-existing quirk by reproducing it against the unmodified baseline) all pass. Also manually exercised the flow (unknown token, single-use, expiry, cross-token invalidation, unknown email) — all behaved as expected. No test framework is configured in this repo, so no automated tests were added.
