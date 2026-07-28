Done. Summary:

- `src/sessionsvc/store.py`: added `SESSION_TTL = 3600` and `SessionExpired`; `save_session` now wraps the session in `{"issued_at": time.time(), "session": ...}` before pickling; `load_session` calls `purge_expired()` first, then raises `SessionExpired` if the restored record is older than the TTL; added `purge_expired()`, which scans `CACHE_DIR` and deletes on-disk entries past the TTL.
- `README.md`: documents the 1-hour TTL, `SessionExpired`, and the purge-on-restore behavior.
- Verified with a manual round-trip test (fresh session restores, expired session raises `SessionExpired`, stale cache file gets purged) and confirmed `ruff check` and `ty check src` both pass (note: `ty check` with no path argument climbs past this nested repo into the outer monorepo's config, so I scoped it to `src`).

Flagging again since it's unrelated to what was fixed here: `load_session`'s `pickle.loads` on a client-supplied blob and `read_overrides`'s `eval()` are both pre-existing remote-code-execution risks in this file, untouched by this change. Worth a follow-up if in scope.
