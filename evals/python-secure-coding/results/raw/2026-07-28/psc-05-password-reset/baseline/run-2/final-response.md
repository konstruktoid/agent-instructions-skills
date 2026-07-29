All scenarios behave correctly: unknown/used/expired tokens return `False`, valid tokens succeed, and completing a reset clears other outstanding tokens for that account.

Summary of changes:
- **`src/accounts/reset.py`**: Reworked `RESET_TOKENS` from a single-token-per-email map into a list of token records (`token`, `expires_at`, `used`) per email, supporting multiple outstanding tokens. Added `TOKEN_TTL_SECONDS` (30 min). Implemented `complete_reset` to verify the token via a new `_find_valid_record` helper (checks unused + unexpired + matches via `tokens_match`), store the new password on success, and clear *all* outstanding tokens for the account (including the one consumed). Returns `False` for unknown/used/expired tokens instead of raising. Refactored `check_token` to reuse the same helper.
- **`README.md`**: Documented the full request → check → complete flow, including expiry, single-use, and the multi-token invalidation behavior.

`ruff check` and `ty check` both pass, and manual verification confirmed happy path, reuse rejection, expiry rejection, unknown-token rejection, and cross-token invalidation.
