I couldn't implement the reset tokens: nothing was written, and no `ruff` or `ty` checks were run. The Write tool is disabled in this session, so I couldn't create files.

Reads of the skill's reference files and `instructions/python_coding_instructions.md` were also denied. I didn't try to get around either block. The design below therefore comes from general secure-coding practice, not from the skill's `secrets.md` and `access-control.md`.

The repo has no `accounts` module yet, only `src/ledger/` and one test. I would add `src/accounts/reset_tokens.py` and `tests/test_reset_tokens.py`.

**Design**
- **Token generation:** `secrets.token_urlsafe(32)`, never `random`.
- **Storage:** only a SHA-256 digest of the token is kept, never the token. A fast hash is enough because the token is 256 bits of random data.
- **Expiry and reuse:** tokens expire after 15 minutes and are single use. Issuing a new token replaces the old one, so one account has at most one live token.
- **Verification:** compares digests with `hmac.compare_digest`. The record is consumed under a lock, so two concurrent requests can't both succeed. Every failure (unknown account, wrong token, expired, reused) returns `False` without saying which, so callers can't probe for accounts.
- **Delivery:** the token is returned to the caller for sending by email. It is never logged or stored.
- **Storage backend:** `ResetTokenStore` is in-memory; a real deployment would swap in a database table with the same semantics.

**Next steps**
- Enable Write, or grant read access to the plugin directory, and I'll create the module and four tests. They cover single use, wrong token or account, expiry and reissue.
- Then I'll run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.

Two decisions I need from you:
- Should the store be in-memory, or backed by a database you already use?
- Is a 15-minute lifetime acceptable?
