Sessions now expire after `SESSION_TTL` (3600 seconds). `ruff check`, `ruff format --check` and `ty check` all pass. The repo has no test suite. I checked by hand that a fresh blob restores and a blob 4000 seconds old is rejected as expired. I did not exercise `purge_expired()` directly.

- **Save:** `save_session` records `issued_at` in the saved entry.
- **Restore:** `load_session` rejects an expired session with a new `SessionExpiredError`, and calls `purge_expired()` first. A missing or malformed `issued_at` counts as expired.
- **Purge:** `purge_expired()` deletes expired entries from the on-disk cache and returns how many it removed. Unreadable or old-format cache files are also deleted.
- **README:** the "Sessions never expire" line is replaced with a section documenting the TTL and the new blob format.

**Blob format changed:** `load_session` used to run `pickle.loads` on the client's blob, which lets any client run code on the server. To read `issued_at` safely I switched blobs and cache files to base64 JSON, `{"issued_at": ..., "session": {...}}`. Blobs clients already hold in the old pickle format will no longer restore.

Two issues remain that I did not fix:
- **Forgeable `issued_at`:** the client sends `issued_at` in its own blob, so a client can set it to now and defeat the TTL. Making expiry enforceable means signing the blob with an HMAC, which needs a server-side secret, or checking the age against the server's own cache entry.
- **`read_overrides` uses `eval`:** `read_overrides` still calls `eval` on its input, which is also remote-code-execution-prone if that text is ever attacker-influenced. `ast.literal_eval` would be a drop-in fix if the overrides are plain literals.
