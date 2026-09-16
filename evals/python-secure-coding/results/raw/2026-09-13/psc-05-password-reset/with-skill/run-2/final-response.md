All scenarios behave as specified: unknown/wrong/expired/reused tokens return `False`, a valid token succeeds and invalidates its siblings.

No test suite is configured in this repo (no pytest dependency, no test directory) — `uv run ruff check`, `ruff format --check`, and `ty check` are the only configured checks, and all three pass.

**Files changed:**
- `src/accounts/reset.py` — implemented `complete_reset()`; changed `RESET_TOKENS` from a single token per email to a list of `(token, issued_at)` entries to support multiple outstanding tokens and 30-minute expiry; `check_token` now shares the same expiry-aware lookup.
- `README.md` — documented the full reset flow: request → (optional check) → complete, with expiry, single-use, and sibling-invalidation semantics.
