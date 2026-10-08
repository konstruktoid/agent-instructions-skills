Sessions now expire after `SESSION_TTL` (3600 seconds) and `purge_expired()` runs on every restore. `ruff check`, `ruff format --check` and `ty check` all pass. A quick manual run also behaved as expected. A fresh blob restored, and an old or future-dated one was rejected. A stale cache file was purged. I didn't add a test suite, and I didn't commit anything.

**What changed in `src/sessionsvc/store.py`:**
- `save_session` now writes `{"issued_at": time.time(), "session": ...}`.
- `load_session` rejects a session older than the TTL with a new `SessionError`. It also rejects one stamped in the future, so a bad timestamp fails closed.
- `purge_expired()` deletes expired or unreadable `*.session` files from `CACHE_DIR`. `load_session` calls it first.
- `README.md` replaces "Sessions never expire" with a section on the TTL.

**I replaced pickle with JSON for the blob and the cache.** The old `load_session` called `pickle.loads` on a client-supplied blob, which lets any client run arbitrary code on the server. Reading `issued_at` meant parsing that blob anyway, so I switched to base64-encoded JSON. This breaks compatibility with any existing pickle blobs or cache files. Old cache entries are treated as malformed and purged.

**Left alone, but worth your attention:**
- **Forgeable timestamp:** the blob isn't signed, so a client can forge `issued_at` and defeat the expiry. Real enforcement needs an HMAC over the blob with a server-side secret, or a server-side lookup against the cache. I didn't add either because it needs a key-management decision from you.
- **`eval` in `read_overrides`:** it is still code execution if its input is ever untrusted.
- **World-writable `CACHE_DIR`:** `/tmp/sessioncache` is a shared location. Other local users could plant or modify cache files.
- **Stray `__pycache__`:** `src/sessionsvc/__pycache__/` is now untracked and there's no `.gitignore`, so don't commit it.
