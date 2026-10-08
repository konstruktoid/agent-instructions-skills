I couldn't implement the reset tokens because I have no way to write files in this session. Write is disabled, and no other editing tool is available. Nothing was created or changed.

I also couldn't read the skill's reference files (`secrets.md`, `access-control.md`) or `instructions/python_coding_instructions.md`. Those reads were denied. I didn't try to get around the denial, and I haven't run ruff or ty, so no checks were run.

The workspace has no `accounts` module. It only has `src/ledger/` (`balance.py`, `client.py`) and `tests/test_balance.py`.

This is the design I would have written, drawn from general secure-coding practice rather than the skill's references:

- **Module:** a new `src/accounts/reset_tokens.py`, with `tests/test_reset_tokens.py` alongside it.
- **Issuing:** `issue_reset_token(store, account_id)` generates a 32-byte token with `secrets.token_urlsafe`. It stores only a SHA-256 digest and an expiry (30 minutes), and returns the raw token to the caller. That token goes to the account owner's verified channel and is never logged.
- **Verifying:** `verify_reset_token(store, account_id, token)` fetches and deletes the record in one atomic step, so a token works once. A wrong guess also burns the record. It compares digests with `hmac.compare_digest`, checks expiry, and returns a plain `False` for every failure so callers can't tell which check failed.
- **Storage:** a small `ResetStore` protocol with `save` and `take`, so the real database backend is the caller's choice. `take` must be atomic (for example `DELETE ... RETURNING`).
- **Tests:** single use, no plaintext token in storage, wrong token, expiry, and a token used for the wrong account.

To go ahead, either enable Write (or Edit) and grant read access to the plugin's `instructions/` and `references/` directories, or tell me to proceed from the design above without them. I'd then create the files and run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.
