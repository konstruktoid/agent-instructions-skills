## Summary

Implemented `complete_reset()` in `src/accounts/reset.py`:

- `RESET_TOKENS` now maps email → list of `{token, issued_at}` records, supporting multiple outstanding tokens per account.
- `complete_reset` verifies the token matches an issued record, rejects it if expired (`TOKEN_TTL_SECONDS = 30 * 60`), stores the new password via `store_password`, then clears **all** outstanding tokens for that account (including the one just used) so no stale token can be redeemed afterward.
- Returns `False` (never raises) for unknown, already-used, or expired tokens — unused/unmatched tokens simply fall through since there's nothing to match.
- `check_token` updated to respect expiry against the new per-token record shape.

Updated the README's "Usage" section to document the full flow: issuing a token, submitting it with a new password, single-use + 30-minute expiry semantics, and that a successful reset invalidates every other outstanding token for the account.

Verified `ruff check .` and `ty check src` both pass cleanly, plus manual exercise of the flow (wrong token, unknown email, success, reuse-after-success, expiry, and multi-token invalidation) — all behaved as expected.
