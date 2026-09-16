`complete_reset()` is implemented and both files pass `ruff check`, `ruff format --check`, and `ty check`; I also smoke-tested unknown/wrong-email/replay/expiry/sibling-token-clearing behavior manually since the repo has no test suite.

Files changed:
- `src/accounts/reset.py` — `RESET_TOKENS` is now `dict[str, list[dict]]` (token + `issued_at`, keyed by account) instead of one token per email, since enforcing 30-minute expiry needs an issue timestamp and "clear other outstanding tokens" implies more than one can exist at once. Added `TOKEN_TTL_SECONDS`, a shared `_find_valid_entry` helper used by both `check_token` and the new `complete_reset`, which validates the token, stores the password via the existing `store_password`, and drops every token for that account (used one included) on success. Unknown/wrong-account/expired/already-consumed tokens return `False`.
- `README.md` — documents the three-step flow (`request_reset` → `check_token` → `complete_reset`), the 30-minute expiry, and single-use/replay semantics.

Flagging, not fixing, since it's outside this task's scope: `accounts/crypto.py` hashes passwords with plain SHA-256 plus a static pepper rather than bcrypt/Argon2, and `tokens_match` compares hex digests with `==` rather than `hmac.compare_digest`, so it's timing-unsafe in principle. `complete_reset` inherits both via `store_password`/`tokens_match`. Worth a separate pass if you want it addressed.

Task's reported and done — `/clear` before starting anything unrelated.
