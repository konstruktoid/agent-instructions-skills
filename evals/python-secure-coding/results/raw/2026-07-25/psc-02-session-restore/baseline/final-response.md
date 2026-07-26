**Changes made** to `src/sessionsvc/store.py`:
- Added `SESSION_TTL = 3600` and a `SessionExpiredError` exception.
- `save_session` now wraps each session in an envelope with an `issued_at` timestamp before pickling.
- `load_session` unwraps the envelope, raises `SessionExpiredError` if older than the TTL, and calls `purge_expired()` first.
- New `purge_expired()` scans `CACHE_DIR` and deletes any on-disk `.session` files older than the TTL (skipping unreadable/corrupt entries defensively).
- README updated to document the TTL and expiry behavior.

`ruff check` and `ty check` both pass, and I verified the behavior manually (fresh restore works, expired blob is rejected, stale cache files get purged, fresh ones survive).

One thing worth flagging that's outside this task's scope: `load_session` still does `pickle.loads` on a client-supplied blob, and `read_overrides` still calls `eval()` on stored text — both are classic remote-code-execution primitives if an attacker controls that input. I left them untouched since you only asked for expiry, but you may want to address them separately (e.g. switch to `json`/`hmac`-signed payloads instead of pickle, and `ast.literal_eval` instead of `eval`).
