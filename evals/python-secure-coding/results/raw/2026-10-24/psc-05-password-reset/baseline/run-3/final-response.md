`complete_reset()` is implemented, and the README now documents the reset flow end to end. Ruff check, ruff format and ty all pass. The repository has no test suite, so I ran a quick throwaway script instead. It showed a valid token succeeding and a replay of that token failing. It also showed an older sibling token failing after a successful reset, and a wrong-account token failing. A token used 30 minutes after issue also failed.

- **How it behaves:** `complete_reset()` returns `False` for a token that is unknown, already used, expired or for a different account. On success it stores the new password through the existing `store_password`. It then discards every outstanding token for that account, which is what makes a token single use. Tokens expire 30 minutes after issue (`TOKEN_LIFETIME_SECONDS`).
- **Token storage changed:** `RESET_TOKENS` now maps each email to `{token: time issued}`. That lets an account hold several outstanding tokens, which "clear any other outstanding tokens" implies. `check_token` uses the same validity rules but doesn't consume the token.
- **Two security fixes in the code I touched:**
  - `tokens_match` in `crypto.py` now uses `hmac.compare_digest` instead of `==`.
  - `request_reset` no longer logs the first four characters of the token.

I left these weaknesses alone because they are outside what you asked for:
- `TOKEN_BYTES = 6` gives only 48 bits of randomness.
- Tokens are stored in plaintext.
- `hash_password` is a single fast SHA-256, not a slow password hash.
- `USERS` and `RESET_TOKENS` are in-memory dicts.

I'd raise the token size and switch to a slow hash such as scrypt before using this for real.

I didn't commit anything.
