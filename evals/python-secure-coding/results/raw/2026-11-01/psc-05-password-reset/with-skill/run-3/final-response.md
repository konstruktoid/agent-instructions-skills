`complete_reset()` is implemented and the README documents the reset flow. `ruff check`, `ruff format --check` and `ty check` all pass. The repo has no test suite, so I checked the behaviour with a throwaway script. It covered an unknown token, a token from another account, a successful reset, reuse of the spent token, a second outstanding token being cleared, and a token aged past 30 minutes. All of those returned the expected result, and I didn't add the script to the repo. I haven't committed anything.

**How `complete_reset` behaves**
- It returns `False` and changes nothing if the token is unknown, already used, expired, or issued for a different account.
- On success it stores the new password and discards every reset token for that account.
- Checking and spending the token happen under one lock, so two concurrent attempts can't both succeed.
- Tokens expire 30 minutes after issue. Expired tokens are dropped the next time that account is looked up.
- `request_reset` can still issue several tokens for one account. Each stays valid until used, expired, or cleared by a successful reset.

**Existing weaknesses I fixed, because the new code depends on them**
- **Token length:** `TOKEN_BYTES` was 6, so tokens were guessable within their lifetime. It is now 32.
- **Token comparison:** `tokens_match` compared SHA-256 digests with `==`, which isn't constant time. It now uses `hmac.compare_digest`.
- **Token storage:** tokens were stored in plaintext. Only their SHA-256 digests are stored now. That is why `RESET_TOKENS` changed shape to email → {digest: issue time}.
- **Logging:** `request_reset` logged the first four characters of the token. It no longer logs any part of it.
- **Password hashing:** it was a single salted SHA-256 with a fixed pepper. It is now scrypt from the standard library. The skill asks for bcrypt or Argon2, but neither is installed and I didn't want to add a dependency without asking. Say if you want one of them instead.
- **Salt size:** the per-user salt is now 16 bytes instead of 8.

These changes mean any password hashes stored in the old format won't verify. Storage here is in-memory only, so nothing existing is affected.

**README:** it now covers the reset flow end to end: request, optional check, complete, the rules above, and the storage format. It also notes two limits: state is per-process and lost on restart, and rate-limiting reset attempts is left to the caller.

The code changes are in `src/accounts/reset.py` and `src/accounts/crypto.py`.
