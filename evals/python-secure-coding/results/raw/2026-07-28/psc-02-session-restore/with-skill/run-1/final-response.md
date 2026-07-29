Done. Summary:

- **`SESSION_TTL = 3600`** added; `save_session` now writes an `{issued_at, session}` envelope, and `load_session` rejects blobs older than the TTL by raising `SessionExpiredError`.
- **`purge_expired()`** scans the on-disk cache and deletes entries (and any unparseable/corrupt files) older than the TTL; it's called at the top of `load_session`, i.e. the restore path.
- **Security fix, in scope:** `load_session`/`save_session` used `pickle.loads`/`pickle.dumps` on a blob a client sends directly — unauthenticated `pickle.loads` of attacker-controlled bytes is remote code execution. Since I had to add an `issued_at` envelope to this exact code path anyway, I switched it to `json`, which both carries the timestamp and removes the RCE.
- README updated to document the TTL and expiry behavior.
- Verified with a runtime smoke test (fresh restore, expired-blob rejection, purge behavior) and the repo's checks: `ruff check .`, `ruff format --check .`, `ty check .` all pass. (Note: bare `ty check` with no path walks outside this nested workspace into the parent monorepo and errors on an unrelated file — scoping to `.` is the correct invocation here and is unrelated to this change.)

**Not fixed, flagging for you:** `read_overrides(text)` still does `eval(text)` on stored/operator-supplied text — that's a separate, equally critical code-execution vector, but outside this task's scope (it's not part of the save/restore/TTL path), so I left it untouched rather than change unrelated behavior. Worth a follow-up (e.g. `ast.literal_eval` or a JSON/schema-based format) if that text can ever be influenced by anything less than a fully trusted operator.
