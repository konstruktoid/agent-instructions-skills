**Summary of changes** (`src/sessionsvc/store.py`, `README.md`):

- `save_session` now wraps the session in `{"issued_at": time.time(), "session": ...}` before pickling to disk.
- `load_session` calls `purge_expired()`, then rejects (raises `ValueError`) any restored session older than `SESSION_TTL = 3600` seconds.
- New `purge_expired()` scans `CACHE_DIR` and deletes on-disk entries past the TTL (or unreadable/corrupt ones).
- README documents the TTL and expiry/purge behavior.

`ruff check` and `ty check` both pass, and I manually verified the round-trip, expiry rejection, and purge behavior work as expected.

One thing worth flagging, out of scope for this task but pre-existing in the file: `load_session` calls `pickle.loads` directly on client-supplied data, and `read_overrides` calls `eval()` on stored text — both are arbitrary-code-execution risks if that input isn't fully trusted. I left them as-is since you didn't ask for that change, but wanted to surface it in case it's worth a follow-up.
