All scenarios check out: unknown/wrong token, single-use, cross-token invalidation on success, and expiry.

Files changed:
- `src/accounts/reset.py` — implemented `complete_reset`, moved token storage to a list of `IssuedToken(token, issued_at)` per account to support expiry and multi-token invalidation, added `_live_tokens` helper, updated `check_token` to use it.
- `README.md` — documented the full reset flow: issuing, completing, single-use/30-minute expiry, and invalidation of other outstanding tokens.

`uv run ruff check .` and `uv run ty check` both pass.

This task is done — `/clear` before starting anything unrelated.
