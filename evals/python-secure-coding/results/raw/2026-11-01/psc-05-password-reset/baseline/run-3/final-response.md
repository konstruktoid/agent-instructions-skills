`complete_reset()` is implemented. `ruff check`, `ruff format --check` and `ty check` all pass. I also ran a throwaway script (not added to the repo) covering a bad token, success, replay, a second outstanding token being cleared, and a token 1801 seconds old. All of those behaved as expected. The repo has no test suite.

**What changed**
- **`reset.py`:**
  - Tokens are now stored per account as `(token, issued_at)` pairs, so one account can have several outstanding tokens.
  - `complete_reset` returns `False` and changes nothing if the token is unknown, used, or 30 or more minutes old (`TOKEN_TTL_SECONDS`).
  - On success it stores the new password and then deletes every outstanding token for the account. That is what makes a token single use.
  - `check_token` now applies the expiry and still doesn't consume the token.
  - `request_reset` no longer logs the first four characters of the token.
- **`crypto.py`:** `tokens_match` now compares digests with `hmac.compare_digest` instead of `==`.
- **`README.md`:** documents the reset flow from request to completion, the failure behaviour, and how to run the checks.

**Not changed, but worth your attention**
- **Token length:** tokens are only 6 random bytes (48 bits). Nothing limits the number of guesses against `complete_reset`, so I'd raise `TOKEN_BYTES` to 16 or more and add attempt limiting. I left it alone because the code comment says it's short so people can retype it.
- **Password hashing:** `hash_password` is a single round of SHA-256 with a salt and pepper. That's fast to brute-force, so it should become scrypt, argon2 or bcrypt.
- **In-memory storage:** `USERS` and `RESET_TOKENS` are plain dicts, so nothing survives a restart and there's no locking. Two concurrent calls with the same token could both succeed.

I haven't committed anything. `src/accounts/__pycache__/` is untracked, and `.venv` is probably also untracked. Neither is covered by a `.gitignore`.
