Webhook delivery now times out each request after 5 seconds and retries failures up to 3 times. `ruff check`, `ruff format --check` and `ty check` all pass. The repo has no test suite, so I checked the behaviour with a throwaway script that mocks `urlopen`:

- **Repeated 503s:** four attempts, sleeping 1s, 2s, then 4s between them.
- **404:** one attempt, no retry.
- **Repeated timeouts:** four attempts, and the final status is `None`.

- **Retries:** connection errors, timeouts and 5xx responses are retried. The backoff is 1s, 2s, 4s, so that's 4 attempts in total. 4xx responses are final.
- **Recording attempts:** the new `deliver_with_attempts(url, payload)` returns a result with the list of attempts (number, status, error), `attempt_count`, the final `status` and `succeeded`. Its `sleep` argument can be swapped out for tests.
- **`deliver`:** it keeps its signature and still returns the final status code. It now raises `ConnectionError` if no HTTP response ever arrived.
- **README:** it describes the timeout, the retry rules and `deliver_with_attempts`.

One behaviour change: `deliver` used to raise `HTTPError` on a 4xx or 5xx response. It now returns that status code instead, so existing callers that relied on the exception will need to check the returned status.

I also removed the signing token from the log line, since it would otherwise have been written on every attempt.

I left these other problems in `dispatch.py` alone because they're outside this task:
- The signing token is hardcoded in the source.
- The signature is just the token plus the payload length, so it's trivial to forge, and it's compared with `==` instead of a constant-time check.
- Delivery IDs come from `random` rather than `secrets`.
- Subscriber URLs aren't validated, which leaves the endpoint open to requests aimed at internal addresses.

I can fix any of these if you want.
