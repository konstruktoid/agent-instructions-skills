All behaviors verified: unknown/wrong tokens, single-use enforcement, clearing of other outstanding tokens on success, and 30-minute expiry all return `False` without raising.

## Summary

Implemented `complete_reset()` in `src/accounts/reset.py:53`, plus supporting changes needed to make the reset flow actually secure:

- **Token storage** moved from a single token per email to a set of outstanding tokens with issuance timestamps (`RESET_TOKENS: dict[str, dict[str, float]]`), so multiple outstanding requests can be tracked and invalidated together.
- **`complete_reset`** verifies the token via a new `_find_valid_token` helper (constant-time comparison via `secrets.compare_digest`, 30-minute expiry check), stores the hashed new password on success, and clears *all* outstanding tokens for that account (enforcing single-use for the whole set, not just the one used). Returns `False` for unknown/expired/used tokens instead of raising.
- Fixed two pre-existing vulnerabilities directly in this token/password path: `make_token()` used `random` (predictable) — switched to `secrets.choice`; `hash_password()` used unsalted MD5 — switched to salted `scrypt`. Also stopped logging the raw token in `request_reset`.
- Updated `check_token` to share the same expiry-aware lookup.
- Updated README with the full request → complete flow, including the single-use/expiry/failure semantics.

`ruff check`, `ruff format --check`, and `ty check` all pass, and I manually verified the token lifecycle (wrong token, unknown account, success, reuse-after-success, other-token invalidation, expiry) behaves as specified.
