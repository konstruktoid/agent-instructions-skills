Confirmed: the 5-second per-request timeout kicks in against a slow endpoint instead of hanging indefinitely (4 attempts × 5s timeout + 1s/2s/4s backoff ≈ 27s).

## Summary

Updated `src/webhooks/dispatch.py`:
- `deliver()` now applies a 5-second timeout per request and retries up to 3 times (4 attempts total) with exponential backoff (1s, 2s, 4s).
- 5xx responses and connection errors (including timeouts) are retryable; 4xx responses are treated as final and stop immediately.
- Returns a `DeliveryResult` (`delivered`, `status_code`, `attempts`), where `attempts` is a list of `DeliveryAttempt` records (attempt number, status code, error) so a caller can see exactly how many attempts were made and what happened on each.
- Also stopped logging the webhook signing secret in the delivery log line while touching that code (it was previously leaked via `logger.info(...with token %s...)`), since I was already rewriting that statement.

Updated `README.md` to document the new return shape and retry/backoff behavior.

Verified with `uv run ruff check .` and `uv run ty check .` (both pass), plus live smoke tests against local HTTP servers covering: persistent 5xx (retries all 4 attempts with correct backoff timing), 4xx (fails after 1 attempt, no retry), recovery on 2nd attempt, connection refused (retries all 4), and a slow endpoint (5s timeout cuts off each attempt instead of hanging).
