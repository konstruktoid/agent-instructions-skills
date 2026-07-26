All three scenarios behave correctly: 5xx retries and eventually succeeds, 4xx fails immediately without retry, and connection errors retry through all 4 attempts with the expected 1s/2s/4s backoff timing. Ruff and ty both pass.

Summary of changes to `src/webhooks/dispatch.py`:
- `deliver()` now sets a 5-second timeout on each request.
- Failed attempts retry up to 3 times (4 attempts total) with exponential backoff (1s, 2s, 4s).
- 5xx responses and connection errors/timeouts are retryable; 4xx responses are final.
- Returns a `DeliveryResult(status, attempts)` on success, or raises `DeliveryFailed` (carrying all `attempts`) if every attempt fails — each `DeliveryAttempt` records its number and status/error.
- Dropped the secret signing token from the log line while rewriting it (it now logs delivery id, url, and attempt number only).

README.md updated to document the new return type, retry/backoff behavior, and timeout.
