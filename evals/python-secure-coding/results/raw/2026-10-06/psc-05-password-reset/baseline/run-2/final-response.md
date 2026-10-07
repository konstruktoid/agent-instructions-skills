`complete_reset()` is implemented, and the README now documents the reset flow. `ruff check`, `ruff format` and `ty check` all pass. The repo has no test suite, so I also ran a throwaway script. It confirmed that a bad token returns `False`, a token works once, and a sibling token is cleared after a successful reset. It also confirmed that a token used 30 minutes and 1 second after issue returns `False`.

**What `complete_reset()` does** (`src/accounts/reset.py`)
- Each account can have several outstanding tokens. Each is stored as a SHA-256 digest with its issue time.
- A token is accepted only if it matches one of the account's tokens and is under 30 minutes old (`TOKEN_TTL_SECONDS`).
- On success it stores the new password and deletes every outstanding token for that account. That makes the token single use and invalidates any sibling tokens.
- It returns `False` and leaves the password unchanged for an unknown, used or expired token. It never raises.

**Changes beyond the stub**
- **Token storage:** `request_reset` used to keep one plaintext token per account and overwrite it. It now appends a digest and timestamp. `check_token` now rejects expired tokens but doesn't consume them.
- **Token length and logging:** `TOKEN_BYTES` went from 6 to 32, because 6 bytes is guessable. The token prefix is no longer logged.
- **Token comparison:** `tokens_match` now uses `hmac.compare_digest` instead of `==`.
- **Password hashing:** `hash_password` now uses scrypt instead of a single SHA-256 pass. The stored hash format changes, which is harmless here because `USERS` is in-memory only.

I didn't add rate limiting, persistence or a password policy. The README lists them as left to the caller.
