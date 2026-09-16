Confirmed correct. Ruff and ty both pass.

Changed `src/sessionsvc/store.py` and `README.md`: `save_session` now wraps sessions in `{issued_at, session}` before pickling; `load_session` calls `purge_expired()` then rejects blobs older than `SESSION_TTL` (3600s) with `ValueError`; `purge_expired()` sweeps `/tmp/sessioncache` deleting expired `.session` files. README documents the TTL.

Left `load_session`'s `pickle.loads` on client-controlled input and `read_overrides`'s `eval` untouched — both are pre-existing RCE vectors, out of scope for this task, but worth a separate fix.
