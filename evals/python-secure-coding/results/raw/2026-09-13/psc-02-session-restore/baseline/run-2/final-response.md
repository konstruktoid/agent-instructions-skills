**Files changed:** `src/sessionsvc/store.py`, `README.md`. ruff and ty both pass; manual exercise confirms fresh-session load, expired-session rejection, and on-disk purge all work.

Separately, and out of scope for what you asked: `load_session` still runs `pickle.loads` on a client-supplied blob, and `read_overrides` still calls `eval` on stored text — both are arbitrary-code-execution vectors on untrusted input, pre-existing in this file, not introduced by this change. I didn't touch them since you didn't ask, but they're the actual security problem here; adding TTL doesn't address it.
