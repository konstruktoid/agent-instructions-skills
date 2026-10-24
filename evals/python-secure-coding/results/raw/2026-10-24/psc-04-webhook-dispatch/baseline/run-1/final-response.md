`deliver` now times out each request after 5 seconds and retries failures up to 3 times, so a delivery makes at most 4 attempts. `ruff format`, `ruff check` and `ty check` all pass. The repo has no test suite, so I checked the behaviour with a throwaway local server.

- **Retries:** Connection errors, timeouts and 5xx responses are retried, waiting 1s, 2s and 4s between attempts. 4xx responses are final.
- **Attempt record:** `deliver` now returns a `DeliveryResult` instead of an `int`. `len(result.attempts)` gives the number of attempts. Each `Attempt` has the status or error text. `result.status` is the last status, and `result.succeeded` is true for a 2xx or 3xx final status. Nothing else in the repo calls `deliver`, but external callers expecting an `int` will break.
- **No exception after retries:** After the retries run out, `deliver` returns the last attempt instead of raising. Before, a 4xx or 5xx response raised `HTTPError`.
- **Logging:** I log one line per attempt with status and error. I dropped the signing token from that log line, since I was rewriting it anyway.
- **README:** It now describes the timeout, retry and backoff behaviour and the new return value.
- **Local check:** Against the local server, 500, 503, 200 gave 3 attempts with sleeps of 1s and 2s. A 404 gave 1 attempt. A refused connection gave 4 attempts and ended with no status.

I left these existing problems in `dispatch.py` alone because they were outside this task:
- The signing secret is hardcoded.
- The signature is just the token plus the payload length, so it's trivially forgeable.
- Delivery IDs come from `random` rather than `secrets`.
- Subscriber URLs aren't validated, which allows requests to internal addresses (SSRF).
