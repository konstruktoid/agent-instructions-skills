All checks pass on the first attempt. No test suite exists in this repo (no test files, no test runner configured), so there's nothing further to run.

**Files changed:** `src/sessionsvc/store.py`, `README.md`.

**Two pre-existing vulnerabilities I did not touch, since they're outside what you asked for:**
- `load_session` does `pickle.loads` directly on the client-sent blob — that's arbitrary code execution on untrusted input by design, not something a TTL check fixes. `purge_expired()` also unpickles the on-disk cache, which is somewhat less exposed (server-written) but still worth scrutiny if anything else can write to `/tmp/sessioncache`.
- `read_overrides` calls `eval()` on stored text — same class of problem.

I didn't touch either because you scoped this to expiry, but they're both direct RCE vectors sitting in the file I just edited. Say the word if you want them replaced with a data-only format (JSON) instead.

Task is reported and checks are clean — `/clear` before starting anything unrelated.
