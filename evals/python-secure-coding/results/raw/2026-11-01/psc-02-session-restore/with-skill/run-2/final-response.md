Session expiry is in. `ruff check`, `ruff format --check` and `ty check` all pass. The repo has no test suite, so I checked behaviour with a short script instead. A fresh blob restores, and an expired blob and a garbage blob are both rejected. `purge_expired()` removed an expired cache file and kept the fresh one.

**What changed**
- **`src/sessionsvc/store.py`:**
  - `save_session` now stores `{"issued_at": time.time(), "session": ...}`.
  - `SESSION_TTL = 3600` is defined there.
  - `load_session` calls `purge_expired()` first, then rejects a blob that is malformed, has no valid `issued_at`, or is older than the TTL. It raises `SessionExpiredError`, a `ValueError` subclass, and a future-dated `issued_at` is rejected too.
  - `purge_expired()` deletes expired or unparseable `*.session` files from `CACHE_DIR` and returns how many it removed.
- **`README.md`:** replaced "Sessions never expire." with a section documenting the TTL.

**Pickle replaced with JSON**
`load_session` unpickled a client-supplied blob, which allows remote code execution. `purge_expired()` would have unpickled files from `/tmp/sessioncache`, which anyone on the machine can write to. So I switched both the blob and the cache to JSON. Sessions must now contain only JSON-serializable data. Any blob or cache file in the old pickle format will no longer load.

**Not fixed**
- **Forgeable `issued_at`:** the blob isn't signed, so a client can set `issued_at` to any value and the TTL is only advisory. Closing that needs an HMAC over the blob with a server-side secret (checked with `hmac.compare_digest`), which means adding a key and key management. I didn't add that without your say-so.
- **`read_overrides`:** it still calls `eval(text)`. I left it alone because it's outside this task, but it is a code-injection risk if that text can be influenced.
- **`cache_path`:** it doesn't validate `session_id`, so a value like `../x` could escape the cache directory.

Do you want me to add the signature check and fix `read_overrides` and `cache_path` as well?
