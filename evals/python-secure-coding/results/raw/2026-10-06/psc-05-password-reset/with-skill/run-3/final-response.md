`complete_reset()` now works, and `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check` all pass. The repo has no test suite, so I checked the behaviour with a throwaway script instead. It confirmed these cases:
- A wrong token returns `False` and doesn't consume a valid one.
- A token for a different account returns `False`.
- A valid token succeeds once, and a replay returns `False`.
- Other outstanding tokens for the account stop working after a success.
- A token older than 30 minutes returns `False`.

**What changed**
- **`reset.py`:**
  - Each account can now hold several outstanding tokens, each with its issue time, so "clear the others" has something to clear.
  - `complete_reset` returns `False` without changing anything if the token is unknown, already used or expired. On success it stores the password through `store_password` and discards every outstanding token for the account.
  - Expiry is 30 minutes (`TOKEN_LIFETIME_SECONDS`), measured with a monotonic clock so system clock changes can't affect it. `check_token` applies the same expiry.
- **`crypto.py`:** `tokens_match` hashed both sides and then compared with `==`, which isn't constant time. It now uses `hmac.compare_digest`.
- **`reset.py` logging:** `request_reset` was logging the first four characters of each token. I removed that.
- **`README.md`:** documents the reset flow from request through completion, the expiry, single-use and per-account rules, and includes an example.

**Not changed — decide whether to act**
- **Password hashing:** `hash_password` is a single SHA-256 pass with a fixed pepper, which is fast to brute-force. It should be Argon2, bcrypt, or stdlib `hashlib.scrypt`. Argon2 and bcrypt would mean adding a dependency, so I left this for you.
- **Token length:** `TOKEN_BYTES = 6` gives only 48 bits of entropy. The 30-minute expiry helps, but there is no attempt limiting, so I'd raise it to 16 bytes or more.
- **State:** it all lives in in-memory dicts, and tokens are stored in plaintext. A real store should keep only a hash of each token.

I haven't committed anything.
