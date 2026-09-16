Behavior verified: fresh sessions restore, expired ones raise `SessionExpiredError`, and `purge_expired()` (called from `load_session`) removes stale cache files by mtime.

**Changed files:** `src/sessionsvc/store.py`, `README.md`.

Checks pass: `ruff check`, `ruff format --check`, `ty check` all clean.

One flag outside this task's scope: `load_session` still calls `pickle.loads` on a client-supplied blob, and `read_overrides` still calls `eval` on stored text — both pre-existing arbitrary-code-execution paths, untouched here since you didn't ask for them. Worth a separate task if you want them fixed.

`/clear` before starting anything unrelated.
