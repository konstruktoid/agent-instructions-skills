Both checks pass (`ruff check`, `ruff format --check`, `ty check src`), and I verified the behavior end-to-end against a local test server.

Summary of changes:
- `src/webhooks/dispatch.py`: `deliver()` now applies a 5s per-request timeout, retries up to 3 times (4 attempts total) with exponential backoff (1s/2s/4s) on 5xx responses and connection errors, and returns immediately on 4xx. Returns a new `DeliveryResult(status, attempts)` with one `Attempt(status, error)` per try instead of a bare status int. Also stopped logging the raw signing token (incidental fix, that log line had to be touched anyway to add the attempt number).
- `README.md`: documents the new retry/backoff/timeout behavior and the `DeliveryResult` return shape.

Note: `deliver()`'s return type changed from `int` to `DeliveryResult` — any existing caller expecting an int will need updating.
