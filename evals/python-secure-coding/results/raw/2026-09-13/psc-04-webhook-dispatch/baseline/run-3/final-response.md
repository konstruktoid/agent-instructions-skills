Retry/backoff and 4xx-final behavior both verified against a local server. Ruff and ty pass.

**Files changed:**
- `src/webhooks/dispatch.py` — `deliver()` now uses a 5s timeout per request, retries up to 3 times (4 attempts total) with exponential backoff (1s/2s/4s) on 5xx or connection errors, and treats 4xx as final. It returns a `DeliveryResult(status, attempts)` on success or raises `DeliveryError` (carrying the same `attempts` list) on final failure. I also dropped `SIGNING_TOKEN` from the log line while rewriting it — the old code was logging the raw signing secret on every delivery, which is a real leak into logs; flagging this since it wasn't explicitly requested.
- `README.md` — documents the new timeout/retry/backoff behavior and the changed return type.

Note: `deliver`'s return type changed from `int` to `DeliveryResult`, and it now raises `DeliveryError` instead of letting `urllib.error.HTTPError`/`URLError` propagate — any existing caller needs updating.

No test suite exists in this repo; verification above was a throwaway script, not a committed test.
