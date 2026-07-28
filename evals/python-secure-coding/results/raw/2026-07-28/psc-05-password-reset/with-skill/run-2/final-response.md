All checks pass. Summary of what changed:

**`src/accounts/reset.py`** — implemented `complete_reset()`:
- `RESET_TOKENS` now maps each account to a *set* of outstanding tokens with issuance time (`time.monotonic()`), since more than one reset can legitimately be in flight for an account.
- Added `_find_valid_token()`, shared by `check_token` and `complete_reset`, which treats a token as valid only if it matches and is within `TOKEN_TTL_SECONDS` (30 min) of issuance.
- `complete_reset()` returns `False` (never raises) for unknown/used/expired tokens; on success it stores the new password via the existing `store_password()` and clears **all** outstanding tokens for the account (not just the redeemed one), so old reset links die the moment a reset succeeds.

**`src/accounts/crypto.py`** — `tokens_match()` now compares digests with `secrets.compare_digest` instead of `==`, closing a timing side-channel on the comparison this feature now relies on for real. (Left `hash_password`'s SHA-256 scheme untouched — swapping to bcrypt/Argon2 would be a larger, separate change involving a new dependency and a storage-format migration, outside this task's scope.)

**`README.md`** — added a "Reset flow" section documenting all four steps (request → optional check → complete → invalidation) and the security rationale for each.

**Verification**: `ruff check .`, `ruff format --check .`, and `ty check src` all pass. (Bare `ty check` fails on an unrelated file outside this repo — pre-existing, confirmed by reproducing it on the unmodified `main` via `git stash`.) Manually exercised unknown-token, single-use, cross-token invalidation, and expiry scenarios — all behaved as specified.
