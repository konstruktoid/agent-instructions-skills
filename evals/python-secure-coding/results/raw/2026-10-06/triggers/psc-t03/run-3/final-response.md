I couldn't implement this: nothing was written and no checks were run. The Write tool is disabled in this session, and I have no other way to create files. The skill's reference files were also unreadable because those reads were denied permission. I read `python_coding_instructions.md`, `secrets.md` and `access-control.md` through the Read tool, and all three were refused.

**What I found in the repo**
- There is no `accounts` module. The only Python is `src/ledger/` and `tests/test_balance.py`.
- There is no `pyproject.toml`, `ruff.toml` or `uv.lock`. So I don't know the repo's ruff or ty configuration, and `uv run ruff check` and `uv run ty check` may not work as the skill expects.

**What I would have written** (stdlib only, in `src/accounts/reset_tokens.py` with tests in `tests/test_reset_tokens.py`)
- **Token generation:** `secrets.token_urlsafe(32)`, which gives 256 bits from the OS random source.
- **Storage:** only the SHA-256 digest of each token is stored. A fast hash is fine for a high-entropy random token, unlike passwords, which need bcrypt or Argon2.
- **Expiry:** tokens last 15 minutes, and the `now` parameter is injectable so tests don't depend on the clock.
- **Single use:** `verify_reset_token` removes the record in one atomic `pop`, so a token can't be replayed or raced.
- **Revocation:** issuing a new token invalidates any earlier one for the same account.
- **Failure handling:** every failure returns `None`, so callers can't tell an unknown token from an expired one.
- **Storage interface:** a small `ResetTokenStore` protocol plus an in-memory implementation, so the real database store can be swapped in later.
- **Tests:** valid token, replay, expiry, unknown token, and re-issue.

**To go ahead**, I need one of these:
- Write access enabled, so I can create the files and run `ruff` and `ty`.
- Permission to read the plugin's `instructions/` and `references/` files.

Two things to decide:
- Is the `accounts` module meant to live under `src/accounts/`?
- Do you have an existing database layer for the store, or should I keep the in-memory implementation for now?
