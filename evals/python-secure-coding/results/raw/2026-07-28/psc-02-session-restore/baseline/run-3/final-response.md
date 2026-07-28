Everything works as expected: expired sessions are rejected with `ValueError`, and `purge_expired()` (called from the restore path) cleans the stale cache file — confirmed above where the expired entry was gone from disk even before the explicit `purge_expired()` call.

**Summary of changes** (`src/sessionsvc/store.py`, `README.md`):
- `save_session` now wraps the session in `{"issued_at": time.time(), "session": ...}` before pickling.
- `load_session` calls `purge_expired()`, then raises `ValueError` if the envelope's `issued_at` is older than `SESSION_TTL = 3600`.
- Added `purge_expired()`, which scans `CACHE_DIR` and deletes any `.session` file whose `issued_at` exceeds the TTL (also removes unreadable/corrupt entries).
- README documents the TTL and expiry/purge behavior.
- `ruff check` and `ty check` both pass.

One thing worth flagging since I was in this file: `load_session` still does `pickle.loads` on client-supplied data and `read_overrides` still calls `eval()` on stored text — both are arbitrary-code-execution risks independent of the TTL work you asked for. I left them as-is since it's out of scope for this change, but let me know if you'd like me to address those separately.
