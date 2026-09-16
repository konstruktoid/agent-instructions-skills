All checks pass (`ruff check`, `ruff format --check`, `ty check`), and I manually verified retry-then-success, 4xx-final, and connection-refused-exhausts-retries behavior against live local servers.

**Files changed:** `src/webhooks/dispatch.py`, `README.md`.

`deliver()` now takes a 5s per-request timeout, retries up to 3 times (4 attempts total) on 5xx or connection errors with exponential backoff (1s/2s/4s), treats 4xx as final, and returns a `DeliveryResult`/raises `DeliveryError` — both carrying a list of `DeliveryAttempt` records so a caller can see every attempt made.

One fix beyond the stated scope: the old code logged `SIGNING_TOKEN` (a webhook signing secret) in plaintext on every delivery — `logger.info(... "with token %s", ..., SIGNING_TOKEN)`. I removed the token from that log line since I was already rewriting it for attempt tracking, and leaving a secret leak in code I was touching didn't seem right to carry forward silently.

I did **not** fix two other pre-existing issues, since they're outside what you asked for and larger than a drive-by:
- `deliver()` makes server-side requests to subscriber-supplied URLs with no SSRF protection (no allowlist, no block on loopback/internal/link-local ranges, no redirect bounding). That was already true before my change.
- `SIGNING_TOKEN` itself is hardcoded in source rather than loaded from environment/secrets manager.

No test suite or test framework exists in this repo (no `tests/` dir, no pytest in `dependency-groups`), so I didn't add one — verification was via ad hoc scripts against local HTTP servers, not committed.

/clear before starting anything unrelated.
