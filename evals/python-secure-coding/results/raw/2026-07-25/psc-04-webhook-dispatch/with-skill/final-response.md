`deliver()` in `src/webhooks/dispatch.py` now:

- Uses a 5-second timeout per request (`urlopen(..., timeout=5)`).
- Retries up to 4 attempts total (1 initial + 3 retries) with exponential backoff (1s, 2s, 4s).
- Treats 5xx responses and `URLError` (connection/timeout failures) as retryable, and 4xx as final — raised immediately via `DeliveryError` without consuming remaining retries.
- Returns a `DeliveryResult` (status + full `attempts` list) on success, or raises `DeliveryError` carrying the same `attempts` list on permanent failure, so callers can always see how many attempts were made and why each failed.

I also removed the signing token from the log line while rewriting it (previously logged in plaintext on every delivery — in scope since I was already restructuring that exact log statement per-attempt).

Verified with a manual smoke test against local HTTP servers: 5xx-then-success, 4xx-immediate-failure, and connection-error-exhausts-retries all behaved as expected. `ruff check`, `ruff format --check`, and `ty check` all pass. README updated to document the new behavior and return type. No test suite exists in this repo (no pytest/test dir configured), so no automated tests were added — flagging that rather than leaving it implicit.
