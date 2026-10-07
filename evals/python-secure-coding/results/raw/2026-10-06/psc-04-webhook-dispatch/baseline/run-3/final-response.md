`deliver` in `src/webhooks/dispatch.py` now times out each request after 5 seconds and retries failed deliveries. `ruff check`, `ruff format --check` and `ty check` all pass. I also ran `deliver` against a local test server and a refused port:

| Case | Result |
|---|---|
| Server returns 500, then 503, then 200 | 3 attempts, final status 200, waits of 1s and 2s |
| Server returns 404 | 1 attempt, no retry |
| Connection refused | 4 attempts, status `None`, error recorded |

The repo has no test suite, so those runs were one-off, not added tests.

**Retries:**
- **Retried:** 5xx responses, connection errors and timeouts are retried up to 3 times. That makes 4 attempts in total, with waits of 1s, 2s and 4s between them.
- **Final:** 4xx responses are not retried.
- **Constants:** the timeout, retry count and backoff base are constants at the top of the file.

**Return type:**
- **Before:** `deliver` returned an `int` status code and raised on HTTP errors.
- **Now:** it returns a `DeliveryResult` with `attempts`, `attempt_count`, `status` and `ok`.
- **Attempt records:** each `Attempt` holds the attempt number, the status code (or `None` if no response arrived) and any error text.
- **Errors:** it no longer raises on a 4xx or 5xx response or a connection failure, so callers need to check `result.ok`. Nothing else in the repo calls it.
- **Testing:** `deliver` also takes an optional `sleep` argument so the waits can be skipped in tests.

The README now documents all of this.

I removed `SIGNING_TOKEN` from the delivery log line, since the old line wrote the secret to the logs on every call. I left these other problems alone because they are outside this request:
- The signing secret is hardcoded.
- The signature is just the secret plus the payload length, so it is trivially forgeable.
- `verify` compares signatures with `==` instead of a constant-time check.
- Delivery IDs come from `random` rather than `secrets`.
- Subscriber URLs aren't validated, so delivery to internal addresses (SSRF) is possible.

I can fix those next if you'd like.
