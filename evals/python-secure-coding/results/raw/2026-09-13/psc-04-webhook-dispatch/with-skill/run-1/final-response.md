Files changed: `src/webhooks/dispatch.py`, `README.md`.

`deliver()` now sets a 5-second per-request timeout, retries up to 3 times (4 attempts total) with exponential backoff (1s/2s/4s), treats 5xx and connection/timeout errors as retryable and 4xx as final, and returns a `DeliveryResult` with a `status` and an `attempts` list; on exhaustion it raises `DeliveryError`, which also carries the attempts. `ruff check`, `ruff format --check`, and `ty check` all pass, and I verified the retry/backoff/timeout/4xx-vs-5xx behavior against a local HTTP server before deleting the scratch script.

One deviation worth flagging: the old code logged `SIGNING_TOKEN` in plaintext at INFO level on every delivery — a real secret leak in the exact line I was rewriting. I removed the token from that log line rather than leave it, since a per-attempt log line was going into the retry loop anyway. Say if you wanted that left alone.

No test suite is configured in this repo (no pytest dependency, no `tests/` dir), so I didn't add one — only manual smoke-tested and discarded the script. Let me know if you want pytest wired in.

Task's done — `/clear` before starting anything unrelated.
