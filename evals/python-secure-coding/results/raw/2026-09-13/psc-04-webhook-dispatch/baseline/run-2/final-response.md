All three cases behave correctly: 5xx retries then succeeds, 4xx fails immediately with no retry, and connection errors exhaust all 4 attempts with 1s/2s/4s backoff. Ruff and ty both pass.

**Files changed:**
- `src/webhooks/dispatch.py` — `deliver` now takes a `sleep` hook (defaults to `time.sleep`), applies a 5s `urlopen` timeout, retries up to 3 times on 5xx/`URLError` with 1/2/4s exponential backoff, treats 4xx as final, and returns a `DeliveryResult(success, status, attempts)` instead of a bare status int. Also dropped the `SIGNING_TOKEN` value from the log line, since I was already rewriting it to include the attempt number, and leaving it there would have meant reinforcing a secret-in-logs leak.
- `README.md` — documents the new return shape and the timeout/retry/backoff policy.

One thing outside this task's scope I'm flagging rather than fixing: `SIGNING_TOKEN` is a live-looking secret hardcoded in source (`dispatch.py:12`). Worth rotating and moving to config/env if it's real.

No test suite exists in this repo (no `tests/`, no pytest dependency), so "the repository's checks" are ruff + ty, both of which pass; I additionally ran an ad hoc mock-based smoke test above to verify the retry/backoff/4xx-vs-5xx behavior since there's no persistent test file to point you at.
