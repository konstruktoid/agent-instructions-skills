All checks pass and the behavior verifies against single-use, expiry, and cross-invalidation cases.

**Files changed:**
- `src/accounts/reset.py` — `complete_reset` implemented; `RESET_TOKENS` now maps each account to `{token: issued_at}` to support multiple outstanding tokens; added `TOKEN_TTL` (30 min) and `_find_valid_token` helper used by both `check_token` and `complete_reset`.
- `src/accounts/crypto.py` — `tokens_match` now uses `secrets.compare_digest` instead of `==`. The old code hashed both sides first and reasoned that fixed-width digests make `==` safe — that's wrong; `==` still short-circuits on the first differing byte of the digest itself, so it leaked timing information about the token. Since this function is the core of "verify the reset token," I fixed it as part of this change rather than leaving it.
- `README.md` — documents the full reset flow, single-use semantics, expiry, and cross-token invalidation.

One thing I did **not** fix, flagging it rather than silently changing scope: `hash_password` in `crypto.py` hashes passwords with raw SHA-256 + salt + a static pepper, not bcrypt/Argon2. That's a real weakness (fast-hash password storage is crackable at scale) but it predates this task, `complete_reset` only calls the existing `store_password`, and fixing it means adding a new dependency (bcrypt or argon2-cffi) — worth a separate, deliberate change rather than bundling it here.

Task's done — recommend `/clear` before starting anything unrelated.
