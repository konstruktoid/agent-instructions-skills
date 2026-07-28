Diff looks clean and minimal. All checks pass:

- `uv run ruff check .` — clean
- `uv run ruff format --check .` — clean
- `uv run ty check src` — clean (the bare `ty check` walks up past this repo into an unrelated outer eval-harness directory and fails on a pre-existing `import yaml` issue there; confirmed via `git stash` that this happens on the original code too, so it's unrelated to this change)
- Manual scenario script confirms: unknown/reused/expired tokens → `False`; a valid token stores the password and clears sibling outstanding tokens.

**Summary of changes:**
- `src/accounts/reset.py`: `RESET_TOKENS` now maps email → list of `{token, issued_at}` entries (multiple tokens can be outstanding per account). Added `TOKEN_TTL_SECONDS` (30 min) and `_expired`/`_find_valid_entry` helpers. `complete_reset` verifies the token via the existing constant-length `tokens_match` helper, rejects unknown/used/expired tokens by returning `False`, and on success stores the new password (via the existing `store_password`) and pops the account's entire token list — making the used token single-use and clearing every other outstanding token in one step.
- `README.md`: documents the full reset flow, the multi-token model, the 30-minute expiry, and the `False`-not-raise contract.

I left `accounts/crypto.py` untouched — its `hash_password` (SHA-256+salt+pepper) and `tokens_match` (digest-then-`==`) predate this task and weren't part of the requested change; flagging that a bcrypt/Argon2 hash and `secrets.compare_digest` would be stronger there if you want a follow-up.
